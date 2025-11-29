# src/aituber_llm_tts/config.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class AppPaths:
    out_root: Path
    audio_subdir: str
    utt_log_filename: str

    @property
    def audio_dir(self) -> Path:
        return self.out_root / self.audio_subdir

    @property
    def utt_log_path(self) -> Path:
        return self.out_root / self.utt_log_filename


@dataclass
class LLMConfig:
    max_turns: int
    mode: str


@dataclass
class TTSConfig:
    sample_rate: int
    base_ms_per_char: int
    base_ms_min: int


@dataclass
class SessionConfig:
    id_prefix: str
    seed: int


@dataclass
class AppConfig:
    schema_version: str
    llm: LLMConfig
    tts: TTSConfig
    paths: AppPaths
    session: SessionConfig
    emo_map_path: Path | None = None


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(config_path: str | Path) -> AppConfig:
    config_path = Path(config_path)
    raw = load_yaml(config_path)

    # デフォルト補完（必要に応じて）
    schema_version = raw.get("schema_version", "llm_tts_contracts_v0.2")

    llm_raw = raw.get("llm", {})
    tts_raw = raw.get("tts", {})
    paths_raw = raw.get("paths", {})
    sess_raw = raw.get("session", {})

    llm = LLMConfig(
        max_turns=int(llm_raw.get("max_turns", 5)),
        mode=str(llm_raw.get("mode", "monologue")),
    )
    tts = TTSConfig(
        sample_rate=int(tts_raw.get("sample_rate", 24000)),
        base_ms_per_char=int(tts_raw.get("base_ms_per_char", 90)),
        base_ms_min=int(tts_raw.get("base_ms_min", 600)),
    )

    out_root = Path(paths_raw.get("out_root", "out"))
    paths = AppPaths(
        out_root=out_root,
        audio_subdir=str(paths_raw.get("audio_subdir", "audio")),
        utt_log_filename=str(paths_raw.get("utt_log_filename", "utt_log.jsonl")),
    )

    session = SessionConfig(
        id_prefix=str(sess_raw.get("id_prefix", "sess_")),
        seed=int(sess_raw.get("seed", 12345)),
    )

    emo_map_path = config_path.parent / "emo_tts_map.yaml"
    if not emo_map_path.exists():
        emo_map_path = None

    return AppConfig(
        schema_version=schema_version,
        llm=llm,
        tts=tts,
        paths=paths,
        session=session,
        emo_map_path=emo_map_path,
    )
