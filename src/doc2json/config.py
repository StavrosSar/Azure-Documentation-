import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    endpoint: str = os.getenv("AZURE_DOCINTEL_ENDPOINT", "").strip()
    key: str = os.getenv("AZURE_DOCINTEL_KEY", "").strip()
    model_id: str = os.getenv("AZURE_DOCINTEL_MODEL_ID", "prebuilt-read").strip()

    def assert_valid(self) -> None:
        missing = []
        if not self.endpoint:
            missing.append("AZURE_DOCINTEL_ENDPOINT")
        if not self.key:
            missing.append("AZURE_DOCINTEL_KEY")
        if missing:
            raise RuntimeError(f"Missing env vars: {', '.join(missing)}")