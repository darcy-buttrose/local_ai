"""Conversation platform for Local AI (Ollama)."""
from __future__ import annotations

from homeassistant.components.conversation import ConversationEntity, ConversationInput, ConversationResult
from homeassistant.components.conversation import intent as conv_intent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .ollama_client import ollama_chat


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([LocalAIConversationEntity(entry)])


class LocalAIConversationEntity(ConversationEntity):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def supported_languages(self) -> list[str]:
        return ["*"]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        data = self._entry.data
        try:
            response_text = await ollama_chat(
                data["url"].rstrip("/"),
                data["model"],
                [{"role": "user", "content": user_input.text}],
            )
        except Exception as err:
            raise HomeAssistantError(f"Ollama request failed: {err}") from err

        intent_response = conv_intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response_text)
        return ConversationResult(response=intent_response, conversation_id=user_input.conversation_id)
