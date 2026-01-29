#  Document Extraction with Azure Document Intelligence

## Overview
This project implements a **document extraction pipeline** for invoices using  
**Azure Document Intelligence (prebuilt-invoice model)**.

The system:
- processes invoice documents (PDF / PNG / JPG / TIFF),
- extracts structured information,
- validates it against a **custom schema**,
- and outputs a normalized JSON file with an explicit success/error envelope.

The implementation satisfies the Week 4 requirements:
- single document type
- explicit schema definition
- text-first extraction (cloud-based OCR)
- validation + error handling
- evaluation on 10 sample documents
- runnable demo via CLI

---

## Selected Document Type
**Invoice**

Azure model:
- `prebuilt-invoice`

Azure semantic fields used internally include (not limited to):
- `InvoiceDate`
- `InvoiceTotal`
- `VendorName`
- `Items`

These fields are mapped into a **custom schema** independent of Azure’s output format.

---

## Custom Schema Definition
The project defines a minimal, normalized schema for invoices.

**Schema fields:**
- `date` — invoice date (`date`, required)
- `total` — invoice total (`currency`, required)
- `company_name` — vendor/company name (`string`, required)

Example (from `schema.py`):


```python
def invoice_labels() -> LabelSchema:
    return LabelSchema(
        doc_type="invoice",
        version="1.0",
        fields=[
            LabelField(name="date", type="date", required=True),
            LabelField(name="total", type="currency", required=True),
            LabelField(name="company_name", type="string", required=True),
        ],
    )
```

## Environment Setup

### 1. Create and activate virtual environment (Windows CMD)
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -U pip
pip install -e .

```

### 2. Install dependencies
```cmd
pip install -r requirements.txt
```

### 3. Environment variables
```
AZURE_DOCINTEL_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_DOCINTEL_KEY=<your-azure-key>
AZURE_DOCINTEL_MODEL_ID=prebuilt-invoice
```

## Demo
```cmd
python -m doc2json.cli invoice6 --out ..\output\invoice6.json
python -m doc2json.cli invoice7 --out ..\output\invoice7.json
python -m doc2json.cli invoice10 --out ..\output\invoice10.json
```
