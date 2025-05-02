"""voai-client: Python SDK for voai.ai VoiceAPI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

__all__ = [
    "VoiceAPI",
    "APIError",
]


class APIError(requests.exceptions.HTTPError):
    """Raised when the VoiceAPI returns an HTTP error."""


class VoiceAPI:
    """High‑level wrapper around the voai.ai VoiceAPI."""

    def __init__(self, api_key: str, *, base_url: str = "https://connect.voai.ai") -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})

    # ------------------------------------------------------------------
    # Internal REST helpers
    # ------------------------------------------------------------------
    def _get(self, path: str) -> Any:
        resp = self.session.get(f"{self.base_url}{path}")
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:  # pragma: no cover
            raise APIError(str(exc)) from exc
        return resp.json()

    def _post(self, path: str, json: Dict[str, Any], *, output_format: str = "wav") -> bytes:
        headers = {
            "x-output-format": output_format,
            "Content-Type": "application/json",
        }
        resp = self.session.post(f"{self.base_url}{path}", json=json, headers=headers)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:  # pragma: no cover
            raise APIError(str(exc)) from exc
        return resp.content

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------
    def get_speakers(self) -> List[Dict[str, Any]]:
        """Return the list of available speakers."""
        return self._get("/TTS/GetSpeaker")

    # -------------------- TTS /speech (短文本) -------------------------
    def speech(
        self,
        text: str,
        speaker: str,
        *,
        version: str = "Neo",
        style: str = "預設",
        speed: float = 1.0,
        pitch_shift: int = 0,
        style_weight: float = 0.0,
        breath_pause: int = 0,
        output_format: str = "wav",
    ) -> bytes:
        payload: Dict[str, Any] = {
            "version": version,
            "text": text,
            "speaker": speaker,
            "style": style,
            "speed": speed,
            "pitch_shift": pitch_shift,
            "style_weight": style_weight,
            "breath_pause": breath_pause,
        }
        return self._post("/TTS/Speech", payload, output_format=output_format)

    # ----------------- TTS /generate-voice (長文本) --------------------
    def generate_voice(
        self,
        voai_script_text: str,
        name: str,
        *,
        model: str = "Neo",
        style: str = "預設",
        speed: float = 1.0,
        pitch_shift: int = 0,
        style_weight: float = 0.0,
        breath_pause: int = 0,
        output_format: str = "wav",
    ) -> bytes:
        payload: Dict[str, Any] = {
            "input": {"voai_script_text": voai_script_text},
            "voice": {"name": name, "style": style, "model": model},
            "audio_config": {
                "speed": speed,
                "pitch_shift": pitch_shift,
                "style_weight": style_weight,
                "breath_pause": breath_pause,
            },
        }
        return self._post("/TTS/generate-voice", payload, output_format=output_format)

    # --------------- NEW: /generate-dialogue (多角色對話) -------------
    def generate_dialogue(
        self,
        dialogue: List[Dict[str, Any]],
        *,
        preset_speakers: Optional[List[Dict[str, Any]]] = None,
        output_format: str = "wav",
    ) -> bytes:
        """Generate multi‑role dialogue audio.

        Parameters
        ----------
        dialogue : list[dict]
            Each element follows the /generate-dialogue spec, e.g. {
            "voai_script_text": "...", "preset_id": "neo佑希"}.
        preset_speakers : list[dict] | None
            Optional preset speaker definitions.
        output_format : str
            Target audio format (default "wav").
        """
        input_block: Dict[str, Any] = {"dialogue": dialogue}
        if preset_speakers:
            input_block["preset_speakers"] = preset_speakers
        payload: Dict[str, Any] = {"input": input_block}
        return self._post("/TTS/generate-dialogue", payload, output_format=output_format)

    # -------------------- Key usage -----------------------------------
    def get_usage(self) -> Dict[str, Any]:
        """Return your API key usage quota information."""
        return self._get("/Key/Usage")

    # -------------------- Helpers -------------------------------------
    def save_audio(self, audio_bytes: bytes, filepath: str | Path) -> Path:
        path = Path(filepath).expanduser().resolve()
        path.write_bytes(audio_bytes)
        return path