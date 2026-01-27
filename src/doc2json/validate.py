import re
from datetime import datetime
from .schema import LabelSchema
from .envelope import ExtractionEnvelope, ExtractionError

def _is_empty(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def _parse_date(value: object) -> bool:
    s = str(value).strip()
    s10 = s[:10]  # handle "2020-12-20T00:00:00" etc.
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            datetime.strptime(s10, fmt)
            return True
        except Exception:
            pass
    return False


def _parse_number(value: object) -> bool:
    # Accept ints/floats directly
    if isinstance(value, (int, float)):
        return True

    s = str(value).strip()
    if s == "":
        return False

    # Remove currency symbols/spaces etc.
    s = re.sub(r"[^\d.,\-]", "", s)

    # Handle thousands separators:
    # If both ',' and '.' exist, assume the last one is decimal separator
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            # "1.234,56" -> "1234.56"
            s = s.replace(".", "").replace(",", ".")
        else:
            # "1,234.56" -> "1234.56"
            s = s.replace(",", "")
    else:
        # Only commas: treat comma as decimal separator if single comma
        if s.count(",") == 1 and s.count(".") == 0:
            s = s.replace(",", ".")

    try:
        float(s)
        return True
    except Exception:
        return False


def validate(envelope: ExtractionEnvelope, labels: LabelSchema) -> ExtractionEnvelope:
    # 1) Required field validation
    for f in labels.fields:
        fr = envelope.data.get(f.name)
        if f.required:
            if fr is None or _is_empty(getattr(fr, "value", None)):
                envelope.errors.append(
                    ExtractionError(
                        code="MISSING_REQUIRED_FIELD",
                        message="Required field not found",
                        field=f.name,
                    )
                )

    # 2) Type validation (only when value exists)
    for f in labels.fields:
        fr = envelope.data.get(f.name)
        if not fr:
            continue

        v = fr.value
        if _is_empty(v):
            continue

        if f.type == "email":
            if not re.search(r"[^@]+@[^@]+\.[^@]+", str(v)):
                envelope.errors.append(
                    ExtractionError(code="INVALID_EMAIL", message="Not a valid email", field=f.name)
                )

        elif f.type == "date":
            if not _parse_date(v):
                envelope.errors.append(
                    ExtractionError(code="INVALID_DATE", message="Not a valid date", field=f.name)
                )

        elif f.type in ("number", "currency"):
            if not _parse_number(v):
                envelope.errors.append(
                    ExtractionError(code="INVALID_NUMBER", message="Not numeric", field=f.name)
                )

    envelope.ok = len(envelope.errors) == 0
    return envelope