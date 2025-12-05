# scripts/uttlog_to_m3prime_input.py

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert utt_log.jsonl (1行) → m3prime_input.json (1 utterance)"
    )
    p.add_argument(
        "--utt-log",
        type=str,
        default="out/utt_log.jsonl",
        help="Path to utt_log.jsonl",
    )
    p.add_argument(
        "--session-id",
        type=str,
        required=True,
        help="Target session_id to extract",
    )
    p.add_argument(
        "--utt-id",
        type=str,
        required=True,
        help="Target utt_id to extract",
    )
    p.add_argument(
        "--output",
        type=str,
        default="out/m3prime_input.json",
        help="Output JSON path for M3' input",
    )
    p.add_argument(
        "--step-ms",
        type=int,
        default=40,
        help="step_ms for M3' (default: 40 = 25fps)",
    )
    return p.parse_args()


def load_utt_log_line(
    log_path: Path,
    session_id: str,
    utt_id: str,
) -> Dict[str, Any]:
    if not log_path.exists():
        raise FileNotFoundError(f"utt_log not found: {log_path}")

    with log_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at line {line_no}: {e}") from e

            if (
                obj.get("session_id") == session_id
                and obj.get("utt_id") == utt_id
            ):
                return obj

    raise ValueError(
        f"Entry not found in utt_log: session_id={session_id}, utt_id={utt_id}"
    )


def convert_uttlog_to_m3prime(
    utt_log_entry: Dict[str, Any],
    step_ms: int,
) -> Dict[str, Any]:
    """
    utt_log の 1 行から、M3' ランタイム入力 (text+audio_ms) を構築する。
    contracts_m0_m3prime_pose_IO_revC のパターン(A)に準拠。:contentReference[oaicite:9]{index=9}
    """

    schema_version = utt_log_entry.get("schema_version", "llm_tts_contracts_v0.2")
    session_id = utt_log_entry["session_id"]
    utt_id = utt_log_entry["utt_id"]

    utterance_offset_ms = int(utt_log_entry.get("utterance_offset_ms", 0))

    llm = utt_log_entry.get("llm", {})
    tts = utt_log_entry.get("tts", {})

    text = llm.get("text", "")
    emo_id = llm.get("emo_id", None)

    audio_ms = int(tts["audio_ms"])

    m3_input: Dict[str, Any] = {
        "schema_version": schema_version,
        "session_id": session_id,
        "utt_id": utt_id,
        "text": text,
        "kana": None,  # 必要なら別ETLで text→kana 変換（contracts 4.1方針）:contentReference[oaicite:10]{index=10}
        "audio_ms": audio_ms,
        "step_ms": step_ms,
        "emo_id": emo_id,
        "utterance_offset_ms": utterance_offset_ms,
    }

    return m3_input


def main() -> None:
    args = parse_args()

    log_path = Path(args.utt_log)
    entry = load_utt_log_line(
        log_path=log_path,
        session_id=args.session_id,
        utt_id=args.utt_id,
    )
    m3_input = convert_uttlog_to_m3prime(
        utt_log_entry=entry,
        step_ms=args.step_ms,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(m3_input, f, ensure_ascii=False, indent=2)

    print(f"[OK] Wrote M3' input JSON to: {out_path}")


if __name__ == "__main__":
    main()
