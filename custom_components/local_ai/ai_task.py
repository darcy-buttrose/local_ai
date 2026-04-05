"""AI Task platform for Local AI (Ollama)."""
from __future__ import annotations

from json import JSONDecodeError
import logging

from homeassistant.components import ai_task, conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.json import json_loads

from .ollama_client import ollama_chat

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([LocalAITaskEntity(entry)])


class LocalAITaskEntity(ai_task.AITaskEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = ai_task.AITaskEntityFeature.GENERATE_DATA

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_ai_task"

    async def _async_generate_data(
        self,
        task: ai_task.GenDataTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenDataTaskResult:
        data = self._entry.data
        prompt = task.instructions
        if task.structure:
            prompt += "\n\nRespond with valid JSON only."

        try:
            text = await ollama_chat(
                data["url"].rstrip("/"),
                data["model"],
                [{"role": "user", "content": prompt}],
                **({"format": "json"} if task.structure else {}),
            )
        except Exception as err:
            raise HomeAssistantError(f"Ollama request failed: {err}") from err

        if not task.structure:
            return ai_task.GenDataTaskResult(conversation_id=chat_log.conversation_id, data=text)

        try:
            return ai_task.GenDataTaskResult(conversation_id=chat_log.conversation_id, data=json_loads(text))
        except JSONDecodeError as err:
            _LOGGER.error("Failed to parse JSON response: %s. Response: %s", err, text)
            raise HomeAssistantError("Error with Ollama structured response") from err
