import json
from pathlib import Path

import typer
from rich import print

from .schema import invoice_labels
from .extract import extract_pdf_to_json
from .validate import validate

app = typer.Typer(add_completion=False)

SUPPORTED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"]


def resolve_input_file(name: str) -> str:
    """
    Resolve an input path that may be given either:
      - with extension: samples/input/invoice_01.pdf
      - without extension: samples/input/invoice_01  (auto-tries common extensions)
    """
    p = Path(name)

    # If the user already passed a real existing file path, use it
    if p.exists() and p.is_file():
        return str(p)

    # Try adding extensions
    for ext in SUPPORTED_EXTS:
        candidate = p.with_suffix(ext)
        if candidate.exists() and candidate.is_file():
            return str(candidate)

    raise FileNotFoundError(
        f"Input file not found. Tried: {name} and extensions {SUPPORTED_EXTS}"
    )


@app.command()
def main(name: str, out: str = "samples/output/result.json"):
    labels = invoice_labels()

    input_path = resolve_input_file(name)

    env = extract_pdf_to_json(input_path, labels)
    env = validate(env, labels)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(env.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    print(f"[bold]ok:[/bold] {env.ok} → wrote {out}")
    if env.errors:
        print("[red]errors:[/red]")
        for e in env.errors:
            print(f" - {e.code} field={e.field}: {e.message}")


if __name__ == "__main__":
    app()