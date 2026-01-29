from pydantic import BaseModel, Field
from typing import Literal, Optional, List

FieldType = Literal["string", "number", "date", "currency", "email", "phone"]

class LabelField(BaseModel):
    name: str
    type: FieldType = "string"
    required: bool = False
    hints: Optional[List[str]] = None
    description: Optional[str] = None

class LabelSchema(BaseModel):
    doc_type: str
    version: str = "1.0"
    fields: List[LabelField]


#Schema labels for invoice documents
def invoice_labels() -> LabelSchema:
    return LabelSchema(
        doc_type="invoice",
        fields=[
            LabelField(name="date", type="date", required=True),
            LabelField(name="total", type="currency", required=True),
            LabelField(name="company_name", type="string", required=True),
        ],
    )
