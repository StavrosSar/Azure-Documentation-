import os
import pytest
from doc2json.schema import invoice_labels
from doc2json.extract import extract_document_to_json

@pytest.mark.azure
def test_azure_extraction_smoke():
    # Requires env vars set locally
    assert os.getenv("AZURE_DOCINTEL_ENDPOINT")
    assert os.getenv("AZURE_DOCINTEL_KEY")

    labels = invoice_labels()
    env = extract_document_to_json("samples/input/invoice1.pdf", labels)
    assert env.doc_type == "invoice"
