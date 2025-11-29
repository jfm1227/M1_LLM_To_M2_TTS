# src/aituber_llm_tts/llm_client.py

from __future__ import annotations

from dataclasses import dataclass, asdict
import itertools
import random
from typing import Dict, Any

from .config import AppConfig


@dataclass
class M1Output:
    # contracts 2.2 を簡略化した形（必要なものだけ）:contentReference[oaicite:10]{index=10}
    schema_version: str
    session_id: str
    utt_id: str
    mode: str
    text: str
    emo_id: str
    tts_style_prompt: str | None
    next_wait_ms: int
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DummyLLMClient:
    """
    本番ではここを実際の LLM クライアント（OpenAI / Gemini など）に置き換える。
    """

    def __init__(self, config: AppConfig, emo_ids: list[str] | None = None) -> None:
        self._config = config
        self._rng = random.Random(config.session.seed)
        self._utt_counter = 0

        if emo_ids is None:
            # LLM が生成対象とする emo_id のサンプル（1_0 と 1_1, 2_1 など）
            emo_ids = ["1_0", "1_1", "2_1", "3_1", "7_1", "9_1"]
        self._emo_cycle = itertools.cycle(emo_ids)

        self._text_candidates = [
            "今日はいい天気だね！",
            "見て見て、このリボンかわいいでしょ？",
            "ちょっと緊張してきたかも……。",
            "ねむくなってきちゃった……。",
            "びっくりした！今のコメント面白いね！",
        ]

    def _next_utt_id(self) -> str:
        self._utt_counter += 1
        return f"utt_{self._utt_counter:06d}"

    def next_utterance(self, session_id: str) -> M1Output:
        utt_id = self._next_utt_id()
        text = self._rng.choice(self._text_candidates)
        emo_id = next(self._emo_cycle)
        next_wait_ms = self._rng.randint(1000, 3000)

        return M1Output(
            schema_version=self._config.schema_version,
            session_id=session_id,
            utt_id=utt_id,
            mode=self._config.llm.mode,
            text=text,
            emo_id=emo_id,
            tts_style_prompt=None,  # 後でオーケストレータが補完
            next_wait_ms=next_wait_ms,
            meta={
                "source": "dummy_llm",
            },
        )
