import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path


_MIME_BY_EXT = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
}

def guess_content_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext in _MIME_BY_EXT:
        return _MIME_BY_EXT[ext]
    raise ValueError(f"Unsupported file extension: {ext} (file: {file_path})")


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
