# src/aituber_llm_tts/tts_client.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any

import math
import wave
import struct

from .config import AppConfig
from .llm_client import M1Output


@dataclass
class M2Output:
    schema_version: str
    session_id: str
    utt_id: str
    wav_path: str
    audio_ms: int
    sample_rate: int
    num_channels: int
    fmt: str
    tts_engine: str
    tts_preset: str | None
    tts_kana: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DummyTTSClient:
    """
    本番では Gemini TTS などに差し替える。
    今は text 長から audio_ms を近似し、簡易トーンの wav を生成する。
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def _estimate_audio_ms(self, text: str) -> int:
        base = self._config.tts.base_ms_min
        per_char = self._config.tts.base_ms_per_char
        return base + per_char * max(len(text), 1)

    def _write_sine_wave(
        self,
        out_path: Path,
        duration_ms: int,
        sample_rate: int,
        freq_hz: float = 440.0,
    ) -> None:
        num_channels = 1
        sampwidth = 2  # 16bit
        n_samples = int(sample_rate * (duration_ms / 1000.0))
        amplitude = 8000

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out_path), "w") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)

            for i in range(n_samples):
                t = i / sample_rate
                value = int(amplitude * math.sin(2 * math.pi * freq_hz * t))
                wf.writeframes(struct.pack("<h", value))

    def synthesize(
        self,
        m1: M1Output,
        audio_path: Path,
        tts_style_prompt: str,
    ) -> M2Output:
        audio_ms = self._estimate_audio_ms(m1.text)
        sample_rate = self._config.tts.sample_rate

        self._write_sine_wave(
            out_path=audio_path,
            duration_ms=audio_ms,
            sample_rate=sample_rate,
            freq_hz=440.0,
        )

        return M2Output(
            schema_version=self._config.schema_version,
            session_id=m1.session_id,
            utt_id=m1.utt_id,
            wav_path=str(audio_path),
            audio_ms=audio_ms,
            sample_rate=sample_rate,
            num_channels=1,
            fmt="wav",
            tts_engine="dummy-tts",
            tts_preset=tts_style_prompt,
            tts_kana=None,
        )
