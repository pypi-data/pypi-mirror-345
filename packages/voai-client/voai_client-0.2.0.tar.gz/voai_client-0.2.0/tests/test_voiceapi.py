"""Unit tests for :class:`voai_client.VoiceAPI`."""

from pathlib import Path

import pytest

from voai_client import VoiceAPI


@pytest.fixture()
def api(fake_session):  # noqa: D401, reusing fixture
    return VoiceAPI("FAKE_KEY", base_url="https://connect.voai.ai")


def test_get_speakers(api):
    speakers = api.get_speakers()
    assert speakers and speakers[0]["name"] == "佑希"


def test_speech(api, tmp_path):
    wav = api.speech("Hello", speaker="佑希")
    assert wav == b"WAVDATA"

    out = tmp_path / "hello.wav"
    api.save_audio(wav, out)
    assert out.exists() and out.read_bytes() == b"WAVDATA"


def test_generate_voice(api):
    wav = api.generate_voice("長文本", name="佑希")
    assert wav == b"WAVDATA"


def test_generate_dialogue(api):
    dlg = [{"voai_script_text": "hi", "preset_id": "p1"}]
    wav = api.generate_dialogue(dlg)
    assert wav == b"WAVDATA"


def test_get_usage(api):
    usage = api.get_usage()
    assert usage["quota"] == 100 and usage["remaining"] == 99