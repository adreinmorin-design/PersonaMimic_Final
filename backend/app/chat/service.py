import logging
import os

from sqlalchemy.orm import Session

from app.auth.models import User
from app.chat.repository import chat_repo
from app.chat.schemas import ChatMessage, ChatResponse
from app.core.paths import WORKSPACE_DIR
from app.swarm.persona_engine import PersonaEngine
from app.swarm.tools import TOOLS, execute_tool
from app.voice.service import voice_service

logger = logging.getLogger("chat_service")


class ChatService:
    def __init__(self):
        self.engine = PersonaEngine()

    async def execute_chat_loop(
        self,
        db: Session,
        user: User,
        message: str,
        history: list[ChatMessage],
        system_prompt: str,
        persona_type: str,
        voice_id: str | None = None,
    ) -> ChatResponse:
        """Agentic Multi-Step Loop for chat interactions."""
        history_dicts = [{"role": m.role, "content": m.content} for m in history]
        history_dicts.append({"role": "user", "content": message})

        max_steps = 20
        current_step = 0
        final_response_text = ""

        while current_step < max_steps:
            try:
                response = await self.engine.generate_response(
                    prompt=system_prompt,
                    chat_context=history_dicts,
                    tools=TOOLS,
                    persona_type=persona_type,
                )
            except Exception as exc:
                logger.error("Chat inference failed at step %s: %s", current_step + 1, exc)
                final_response_text = (
                    "Inference engine is temporarily unavailable. Please retry in a few moments."
                )
                history_dicts.append({"role": "system", "content": final_response_text})
                break

            message_dict = response
            history_dicts.append(message_dict)

            tool_calls = message_dict.get("tool_calls")
            if tool_calls:
                for tool in tool_calls:
                    tool_name, tool_args = PersonaEngine.unwrap_tool_call(tool)
                    logger.info(f"[CHAT TOOL] {tool_name} | {tool_args}")
                    try:
                        result = (
                            await execute_tool(tool_name, tool_args)
                            if tool_name
                            else "Unknown tool"
                        )
                    except Exception as exc:
                        logger.error("Tool execution failed for %s: %s", tool_name, exc)
                        result = f"Tool execution error: {exc}"

                    history_dicts.append(
                        {
                            "role": "tool",
                            "content": str(result),
                            "name": tool_name or "unknown",
                        }
                    )
                current_step += 1
            else:
                final_response_text = message_dict.get("content", "")
                break

        if not final_response_text:
            final_response_text = "Task partially completed or maximum steps reached."

        # Handle Voice (TTS)
        audio_url = None
        if voice_id and final_response_text:
            audio_url = await voice_service.text_to_speech(final_response_text, voice_id)

        # Persist Interaction
        await self._log_interaction(db, user.id if user else None, message, final_response_text)

        # Get Workspace Files
        files = []
        try:
            files = os.listdir(WORKSPACE_DIR)
        except Exception as exc:
            logger.warning("Failed to list workspace files: %s", exc)

        # Extract logs (tool calls and results)
        logs = [
            item
            for item in history_dicts
            if item["role"] in ["tool", "assistant"]
            and (item.get("tool_calls") or item["role"] == "tool")
        ]

        return ChatResponse(
            response=final_response_text,
            audio_url=audio_url,
            logs=logs,
            files=files,
            role=user.role.name if user and user.role else "system",
        )

    async def _log_interaction(self, db: Session, user_id: int | None, message: str, response: str):
        if user_id is None:
            return
        try:
            await chat_repo.log_interaction(db, user_id, message, response)
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")


chat_service = ChatService()
