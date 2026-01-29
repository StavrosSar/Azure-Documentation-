from doc2json.schema import invoice_labels
from doc2json.envelope import ExtractionEnvelope, FieldResult
from doc2json.validate import validate


def make_env(date=None, total=None, company=None):
    labels = invoice_labels()
    return ExtractionEnvelope(
        ok=True,
        doc_type=labels.doc_type,
        model_id="test-model",
        labels=labels.model_dump(),
        data={
            "date": FieldResult(value=date),
            "total": FieldResult(value=total),
            "company_name": FieldResult(value=company),
        },
        errors=[],
        meta={},
    )


def test_validate_required_fields_missing():
    labels = invoice_labels()
    env = make_env(date=None, total=None, company="ACME")

    out = validate(env, labels)

    assert out.ok is False
    # should include missing errors for date + total (and NOT duplicated)
    codes = [(e.code, e.field) for e in out.errors]
    assert ("MISSING_REQUIRED_FIELD", "date") in codes
    assert ("MISSING_REQUIRED_FIELD", "total") in codes
    assert ("MISSING_REQUIRED_FIELD", "company_name") not in codes


def test_validate_parsing_date_and_currency():
    labels = invoice_labels()
    # Accept common date formats + number parsing
    env = make_env(date="2024-01-31", total="1.234,56", company="ACME")

    out = validate(env, labels)

    assert out.ok is True
    assert out.errors == []
