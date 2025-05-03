import json
import xml.etree.ElementTree as ET
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Union

import openai

from letta.agents.base_agent import BaseAgent
from letta.schemas.agent import AgentState
from letta.schemas.block import BlockUpdate
from letta.schemas.enums import MessageStreamStatus
from letta.schemas.letta_message import LegacyLettaMessage, LettaMessage
from letta.schemas.letta_message_content import TextContent
from letta.schemas.letta_response import LettaResponse
from letta.schemas.message import Message, MessageCreate, ToolReturn
from letta.schemas.openai.chat_completion_request import ChatCompletionRequest, Tool, UserMessage
from letta.schemas.usage import LettaUsageStatistics
from letta.schemas.user import User
from letta.server.rest_api.utils import convert_in_context_letta_messages_to_openai, create_input_messages
from letta.services.agent_manager import AgentManager
from letta.services.block_manager import BlockManager
from letta.services.message_manager import MessageManager
from letta.system import package_function_response


# TODO: Move this to the new Letta Agent loop
class VoiceSleeptimeAgent(BaseAgent):
    """
    A stateless agent that helps with offline memory computations.
    """

    def __init__(
        self,
        agent_id: str,
        convo_agent_state: AgentState,
        openai_client: openai.AsyncClient,
        message_manager: MessageManager,
        agent_manager: AgentManager,
        block_manager: BlockManager,
        target_block_label: str,
        message_transcripts: List[str],
        actor: User,
    ):
        super().__init__(
            agent_id=agent_id,
            openai_client=openai_client,
            message_manager=message_manager,
            agent_manager=agent_manager,
            actor=actor,
        )

        self.convo_agent_state = convo_agent_state
        self.block_manager = block_manager
        self.target_block_label = target_block_label
        self.message_transcripts = message_transcripts

    def update_message_transcript(self, message_transcripts: List[str]):
        self.message_transcripts = message_transcripts

    async def step(self, input_messages: List[MessageCreate], max_steps: int = 10) -> LettaResponse:
        """
        Process the user's input message, allowing the model to call memory-related tools
        until it decides to stop and provide a final response.
        """
        agent_state = self.agent_manager.get_agent_by_id(agent_id=self.agent_id, actor=self.actor)
        in_context_messages = create_input_messages(input_messages=input_messages, agent_id=self.agent_id, actor=self.actor)
        openai_messages = convert_in_context_letta_messages_to_openai(in_context_messages, exclude_system_messages=True)

        # 1. Store memories
        request = self._build_openai_request(openai_messages, agent_state, tools=self._build_store_memory_tool_schemas())

        chat_completion = await self.openai_client.chat.completions.create(**request.model_dump(exclude_unset=True))
        assistant_message = chat_completion.choices[0].message

        # Process tool calls
        tool_call = assistant_message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "store_memories":
            print("Called store_memories")
            print(function_args)
            chunks = function_args.get("chunks", [])
            results = [self.store_memory(agent_state=self.convo_agent_state, **chunk_args) for chunk_args in chunks]

            aggregated_result = next((res for res, _ in results if res is not None), None)
            aggregated_success = all(success for _, success in results)

        else:
            raise ValueError("Error: Unknown tool function '{function_name}'")

        assistant_message = {
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {"name": function_name, "arguments": tool_call.function.arguments},
                }
            ],
        }
        openai_messages.append(assistant_message)
        in_context_messages.append(
            Message.dict_to_message(
                agent_id=self.agent_id,
                openai_message_dict=assistant_message,
                model=agent_state.llm_config.model,
                name=function_name,
            )
        )
        tool_call_message = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": package_function_response(was_success=aggregated_success, response_string=str(aggregated_result)),
        }
        openai_messages.append(tool_call_message)
        in_context_messages.append(
            Message.dict_to_message(
                agent_id=self.agent_id,
                openai_message_dict=tool_call_message,
                model=agent_state.llm_config.model,
                name=function_name,
                tool_returns=[ToolReturn(status="success" if aggregated_success else "error")],
            )
        )

        # 2. Execute rethink block memory loop
        human_block_content = self.agent_manager.get_block_with_label(
            agent_id=self.agent_id, block_label=self.target_block_label, actor=self.actor
        )
        rethink_command = f"""
        Here is the current memory block created earlier:

### CURRENT MEMORY
{human_block_content}
### END CURRENT MEMORY

Please refine this block:

- Merge in any new facts and remove outdated or contradictory details.
- Organize related information together (e.g., preferences, background, ongoing goals).
- Add any light, supportable inferences that deepen understanding—but do not invent unsupported details.

Use `rethink_user_memory(new_memory)` as many times as you need to iteratively improve the text. When it’s fully polished and complete, call `finish_rethinking_memory()`.
        """
        rethink_command = UserMessage(content=rethink_command)
        openai_messages.append(rethink_command.model_dump())

        for _ in range(max_steps):
            request = self._build_openai_request(openai_messages, agent_state, tools=self._build_sleeptime_tools())
            chat_completion = await self.openai_client.chat.completions.create(**request.model_dump(exclude_unset=True))
            assistant_message = chat_completion.choices[0].message

            # Process tool calls
            tool_call = assistant_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "rethink_user_memory":
                print("Called rethink_user_memory")
                print(function_args)
                result, success = self.rethink_user_memory(agent_state=agent_state, **function_args)
            elif function_name == "finish_rethinking_memory":
                print("Called finish_rethinking_memory")
                result, success = None, True
                break
            else:
                print(f"Error: Unknown tool function '{function_name}'")
                raise ValueError(f"Error: Unknown tool function '{function_name}'", False)
            assistant_message = {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {"name": function_name, "arguments": tool_call.function.arguments},
                    }
                ],
            }
            openai_messages.append(assistant_message)
            in_context_messages.append(
                Message.dict_to_message(
                    agent_id=self.agent_id,
                    openai_message_dict=assistant_message,
                    model=agent_state.llm_config.model,
                    name=function_name,
                )
            )
            tool_call_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": package_function_response(was_success=success, response_string=str(result)),
            }
            openai_messages.append(tool_call_message)
            in_context_messages.append(
                Message.dict_to_message(
                    agent_id=self.agent_id,
                    openai_message_dict=tool_call_message,
                    model=agent_state.llm_config.model,
                    name=function_name,
                    tool_returns=[ToolReturn(status="success" if success else "error")],
                )
            )

        # Actually save the memory:
        target_block = agent_state.memory.get_block(self.target_block_label)
        self.block_manager.update_block(block_id=target_block.id, block_update=BlockUpdate(value=target_block.value), actor=self.actor)

        self.message_manager.create_many_messages(pydantic_msgs=in_context_messages, actor=self.actor)
        return LettaResponse(messages=[msg for m in in_context_messages for msg in m.to_letta_messages()], usage=LettaUsageStatistics())

    def _format_messages_llm_friendly(self):
        messages = self.message_manager.list_messages_for_agent(agent_id=self.agent_id, actor=self.actor)

        llm_friendly_messages = [f"{m.role}: {m.content[0].text}" for m in messages if m.content and isinstance(m.content[0], TextContent)]
        return "\n".join(llm_friendly_messages)

    def _build_openai_request(self, openai_messages: List[Dict], agent_state: AgentState, tools: List[Tool]) -> ChatCompletionRequest:
        openai_request = ChatCompletionRequest(
            model=agent_state.llm_config.model,  # TODO: Separate config for summarizer?
            messages=openai_messages,
            tools=tools,
            tool_choice="required",
            user=self.actor.id,
            max_completion_tokens=agent_state.llm_config.max_tokens,
            temperature=agent_state.llm_config.temperature,
            stream=False,
        )
        return openai_request

    def _build_store_memory_tool_schemas(self) -> List[Tool]:
        """
        Build the schemas for the three memory-related tools.
        """
        tools = [
            Tool(
                type="function",
                function={
                    "name": "store_memories",
                    "description": "Archive coherent chunks of dialogue that will be evicted, preserving raw lines and a brief contextual description.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chunks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start_index": {"type": "integer", "description": "Index of first line in original history."},
                                        "end_index": {"type": "integer", "description": "Index of last line in original history."},
                                        "context": {
                                            "type": "string",
                                            "description": "A high-level description providing context for why this chunk matters.",
                                        },
                                    },
                                    "required": ["start_index", "end_index", "context"],
                                },
                            }
                        },
                        "required": ["chunks"],
                        "additionalProperties": False,
                    },
                },
            ),
        ]

        return tools

    def _build_sleeptime_tools(self) -> List[Tool]:
        tools = [
            Tool(
                type="function",
                function={
                    "name": "rethink_user_memory",
                    "description": (
                        "Rewrite memory block for the main agent, new_memory should contain all current "
                        "information from the block that is not outdated or inconsistent, integrating any "
                        "new information, resulting in a new memory block that is organized, readable, and "
                        "comprehensive."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "new_memory": {
                                "type": "string",
                                "description": (
                                    "The new memory with information integrated from the memory block. "
                                    "If there is no new information, then this should be the same as the "
                                    "content in the source block."
                                ),
                            },
                        },
                        "required": ["new_memory"],
                        "additionalProperties": False,
                    },
                },
            ),
            Tool(
                type="function",
                function={
                    "name": "finish_rethinking_memory",
                    "description": ("This function is called when the agent is done rethinking the memory."),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                },
            ),
        ]

        return tools

    def rethink_user_memory(self, new_memory: str, agent_state: AgentState) -> Tuple[Optional[str], bool]:
        if agent_state.memory.get_block(self.target_block_label) is None:
            agent_state.memory.create_block(label=self.target_block_label, value=new_memory)

        agent_state.memory.update_block_value(label=self.target_block_label, value=new_memory)
        return None, True

    def store_memory(self, start_index: int, end_index: int, context: str, agent_state: AgentState) -> Tuple[Optional[str], bool]:
        """
        Store a memory.
        """
        try:
            messages = self.message_transcripts[start_index : end_index + 1]
            memory = self.serialize(messages, context)
            self.agent_manager.passage_manager.insert_passage(
                agent_state=agent_state,
                agent_id=agent_state.id,
                text=memory,
                actor=self.actor,
            )
            self.agent_manager.rebuild_system_prompt(agent_id=agent_state.id, actor=self.actor, force=True)

            return None, True
        except Exception as e:
            return f"Failed to store memory given start_index {start_index} and end_index {end_index}: {e}", False

    def serialize(self, messages: List[str], context: str) -> str:
        """
        Produce an XML document like:

        <memory>
          <messages>
            <message>…</message>
            <message>…</message>
            …
          </messages>
          <context>…</context>
        </memory>
        """
        root = ET.Element("memory")

        msgs_el = ET.SubElement(root, "messages")
        for msg in messages:
            m = ET.SubElement(msgs_el, "message")
            m.text = msg

        sum_el = ET.SubElement(root, "context")
        sum_el.text = context

        # ET.tostring will escape reserved chars for you
        return ET.tostring(root, encoding="unicode")

    def deserialize(self, xml_str: str) -> Tuple[List[str], str]:
        """
        Parse the XML back into (messages, context). Raises ValueError if tags are missing.
        """
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        msgs_el = root.find("messages")
        if msgs_el is None:
            raise ValueError("Missing <messages> section")

        messages = []
        for m in msgs_el.findall("message"):
            # .text may be None if empty, so coerce to empty string
            messages.append(m.text or "")

        sum_el = root.find("context")
        if sum_el is None:
            raise ValueError("Missing <context> section")
        context = sum_el.text or ""

        return messages, context

    async def step_stream(
        self, input_messages: List[MessageCreate], max_steps: int = 10
    ) -> AsyncGenerator[Union[LettaMessage, LegacyLettaMessage, MessageStreamStatus], None]:
        """
        This agent is synchronous-only. If called in an async context, raise an error.
        """
        raise NotImplementedError("VoiceSleeptimeAgent does not support async step.")
