import re
from typing import Dict
from .azure_client import make_client
from .config import Settings, guess_content_type
from .schema import LabelSchema
from .envelope import ExtractionEnvelope, FieldResult, ExtractionError


def _extract_value(field_obj):
    """Best-effort extraction for Azure DocumentField across SDK variants."""
    if field_obj is None:
        return None

    # Most common
    v = getattr(field_obj, "value", None)
    if v is not None:
        return v

    # Some SDKs expose typed values
    for attr in (
        "value_string",
        "value_date",
        "value_number",
        "value_integer",
        "value_currency",
        "value_phone_number",
        "value_address",
    ):
        v = getattr(field_obj, attr, None)
        if v is not None:
            return v

    # Fallback: raw recognized text
    v = getattr(field_obj, "content", None)
    if v is not None:
        return v

    return None


def _pick_field(fields: dict, candidates: list[str]):
    """Return (value, confidence, matched_key) from Azure fields dict."""
    for k in candidates:
        if k in fields and fields[k] is not None:
            f = fields[k]
            val = _extract_value(f)
            conf = getattr(f, "confidence", None)
            if val is not None:
                return val, conf, k
    return None, None, None


def _currency_to_jsonable(v):
    """
    Convert Azure CurrencyValue (or dict-like currency) into:
      - amount (float) for validation
      - raw_currency (plain dict) for JSON
    """
    if v is None:
        return None, None

    # Case 1: already a dict from some SDK versions
    if isinstance(v, dict) and "amount" in v:
        return v.get("amount"), {
            "amount": v.get("amount"),
            "currencyCode": v.get("currencyCode"),
            "currencySymbol": v.get("currencySymbol"),
        }

    # Case 2: Azure CurrencyValue object (not JSON serializable)
    amount = getattr(v, "amount", None)
    code = getattr(v, "currency_code", None) or getattr(v, "currencyCode", None)
    symbol = getattr(v, "currency_symbol", None) or getattr(v, "currencySymbol", None)

    # If it doesn't look like currency, return it as-is (best effort)
    if amount is None and code is None and symbol is None:
        return v, None

    return amount, {
        "amount": amount,
        "currencyCode": code,
        "currencySymbol": symbol,
    }


def _flatten_read_result(result) -> str:
    chunks = []
    if getattr(result, "pages", None):
        for p in result.pages:
            if getattr(p, "lines", None):
                for line in p.lines:
                    if getattr(line, "content", None):
                        chunks.append(line.content)
    if not chunks and getattr(result, "content", None):
        return result.content
    return "\n".join(chunks)


def _heuristic_find_field(text: str, hints: list[str]) -> str | None:
    for h in hints:
        pattern = rf"{re.escape(h)}\s*[:#]?\s*(.+)"
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_document_to_json(file_path: str, labels: LabelSchema, settings: Settings | None = None) -> ExtractionEnvelope:
    """Extract structured data from a supported document (PDF or image)."""
    settings = settings or Settings()
    client = make_client(settings)

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id=settings.model_id,
            body=f,
            content_type=guess_content_type(file_path),
        )

    result = poller.result()
    print("MODEL:", settings.model_id)
    print("HAS_PAGES:", bool(getattr(result, "pages", None)))
    print("DOC_COUNT:", len(getattr(result, "documents", []) or []))
    if getattr(result, "documents", None) and result.documents:
        print("FIELD_KEYS:", list(getattr(result.documents[0], "fields", {}).keys()))

    doc = None
    if getattr(result, "documents", None):
        doc = result.documents[0] if result.documents else None

    azure_fields = getattr(doc, "fields", {}) if doc else {}

    text = _flatten_read_result(result)

    # Extract fields based on labels
    date_val, date_conf, date_key = _pick_field(
        azure_fields,
        ["InvoiceDate"],
    )

    total_val, total_conf, total_key = _pick_field(
        azure_fields,
        ["InvoiceTotal"],
    )

    # Make invoice total JSON-serializable + validator-friendly
    total_amount, total_currency_raw = _currency_to_jsonable(total_val)
    if total_currency_raw is not None:
        total_val = total_amount  # float for validation

    company_val, company_conf, company_key = _pick_field(
        azure_fields,
        ["VendorName", "CustomerName"],
    )

    data = {
        "date": FieldResult(
            value=date_val,
            confidence=date_conf,
            source="prebuilt-invoice",
            raw={"azure_key": date_key},
        ),
        "total": FieldResult(
            value=total_val,  # float now (e.g., 144.0)
            confidence=total_conf,
            source="prebuilt-invoice",
            raw={"azure_key": total_key, "currency": total_currency_raw},
        ),
        "company_name": FieldResult(
            value=company_val,
            confidence=company_conf,
            source="prebuilt-invoice",
            raw={"azure_key": company_key},
        ),
    }

    return ExtractionEnvelope(
        ok=True,                       
        doc_type=labels.doc_type,
        model_id=settings.model_id,
        labels=labels.model_dump(),
        data=data,
        errors=[],                     
        meta={"documents": len(getattr(result, "documents", []) or [])},
    )
