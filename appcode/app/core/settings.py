import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Settings:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[2]
        cfg_path = root / "config" / "config.yaml"
        if cfg_path.exists():
            data: Dict[str, Any] = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        else:
            data = {}

        app_cfg = data.get("app", {})
        models_cfg = data.get("models", {})
        history_cfg = data.get("history", {})

        self.project_id: str = os.getenv(
            "GCP_PROJECT_ID",
            app_cfg.get("project_id", "johneysadminproject"),
        )
        self.firestore_collection: str = app_cfg.get(
            "firestore_collection",
            "messages",
        )

        self.openai_model: str = os.getenv(
            "OPENAI_MODEL",
            models_cfg.get("openai", "gpt-4.1-mini"),
        )
        self.perplexity_model: str = os.getenv(
            "PPLX_MODEL",
            models_cfg.get("perplexity", "sonar"),
        )
        self.gemini_model: str = os.getenv(
            "GEMINI_MODEL",
            models_cfg.get("gemini", "gemini-2.5-flash"),
        )

        self.history_limit: int = int(
            os.getenv("HISTORY_LIMIT", history_cfg.get("max_messages", 30)),
        )


settings = Settings()
