import json
from doc2json.schema import invoice_labels
from doc2json.envelope import ExtractionEnvelope, FieldResult


def test_envelope_serialization_to_json():
    labels = invoice_labels()
    env = ExtractionEnvelope(
        ok=True,
        doc_type=labels.doc_type,
        model_id="test-model",
        labels=labels.model_dump(),
        data={
            "date": FieldResult(value="2024-01-31", confidence=0.99),
            "total": FieldResult(value=123.45, confidence=0.88),
            "company_name": FieldResult(value="ACME", confidence=0.77),
        },
        errors=[],
        meta={"documents": 1},
    )

    payload = env.model_dump(mode="json")
    # must be JSON serializable
    json.dumps(payload)

    assert payload["ok"] is True
    assert payload["data"]["total"]["value"] == 123.45
