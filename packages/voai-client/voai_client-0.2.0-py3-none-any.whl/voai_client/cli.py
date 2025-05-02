"""Command‑line interface for voai‑client."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import VoiceAPI, __version__  # type: ignore[attr-defined]


def _positive_float(value: str) -> float:  # noqa: D401
    f = float(value)
    if f <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return f


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voai-cli", description="voai.ai VoiceAPI CLI")
    p.add_argument("--api-key", required=True, help="Your voai.ai API key")

    sub = p.add_subparsers(dest="cmd", required=True)

    # get_speakers
    sub.add_parser("speakers", help="List available speakers")

    # speech (短文本)
    sp = sub.add_parser("speech", help="Generate speech (短文本)")
    sp.add_argument("text", help="Text to synthesize")
    sp.add_argument("speaker", help="Speaker name")
    sp.add_argument("--outfile", default="speech.wav", help="Output WAV path")
    sp.add_argument("--version", default="Neo")
    sp.add_argument("--style", default="預設")
    sp.add_argument("--speed", type=_positive_float, default=1.0)
    sp.add_argument("--pitch-shift", type=int, default=0)
    sp.add_argument("--style-weight", type=float, default=0.0)
    sp.add_argument("--breath-pause", type=int, default=0)

    # generate‑voice (長文本)
    gv = sub.add_parser("generate", help="Generate speech (長文本)")
    gv.add_argument("script", help="Path to text file with voai_script_text")
    gv.add_argument("speaker", help="Speaker name")
    gv.add_argument("--outfile", default="generate.wav", help="Output WAV path")
    gv.add_argument("--model", default="Neo")
    gv.add_argument("--style", default="預設")
    gv.add_argument("--speed", type=_positive_float, default=1.0)
    gv.add_argument("--pitch-shift", type=int, default=0)
    gv.add_argument("--style-weight", type=float, default=0.0)
    gv.add_argument("--breath-pause", type=int, default=0)

    # generate-dialogue (多角色)
    dlg = sub.add_parser("dialogue", help="Generate dialogue (多角色)")
    dlg.add_argument("jsonfile", help="Path to JSON file containing dialogue payload (input block)")
    dlg.add_argument("--outfile", default="dialogue.wav", help="Output WAV path")

    # usage
    sub.add_parser("usage", help="Show API usage quota")

    return p


def main(argv: Optional[List[str]] | None = None) -> None:  # noqa: D401
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)

    api = VoiceAPI(args.api_key)

    if args.cmd == "speakers":
        print(json.dumps(api.get_speakers(), ensure_ascii=False, indent=2))
    elif args.cmd == "speech":
        audio = api.speech(
            text=args.text,
            speaker=args.speaker,
            version=args.version,
            style=args.style,
            speed=args.speed,
            pitch_shift=args.pitch_shift,
            style_weight=args.style_weight,
            breath_pause=args.breath_pause,
        )
        path = api.save_audio(audio, args.outfile)
        print(f"Saved {path}")
    elif args.cmd == "generate":
        script_text = Path(args.script).read_text(encoding="utf-8")
        audio = api.generate_voice(
            voai_script_text=script_text,
            name=args.speaker,
            model=args.model,
            style=args.style,
            speed=args.speed,
            pitch_shift=args.pitch_shift,
            style_weight=args.style_weight,
            breath_pause=args.breath_pause,
        )
        path = api.save_audio(audio, args.outfile)
        print(f"Saved {path}")
    elif args.cmd == "dialogue":
        input_block = json.loads(Path(args.jsonfile).read_text(encoding="utf-8"))
        if "input" in input_block:  # full payload provided
            dialogue = input_block["input"].get("dialogue", [])
            preset_speakers = input_block["input"].get("preset_speakers")
        else:  # assume user gave the inner blocks directly
            dialogue = input_block.get("dialogue", [])
            preset_speakers = input_block.get("preset_speakers")

        audio = api.generate_dialogue(dialogue, preset_speakers=preset_speakers)
        path = api.save_audio(audio, args.outfile)
        print(f"Saved {path}")
    elif args.cmd == "usage":
        print(json.dumps(api.get_usage(), ensure_ascii=False, indent=2))
    else:  # pragma: no cover
        raise SystemExit("Unknown command")


if __name__ == "__main__":  # pragma: no cover
    main()
