from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from .config import Settings

def make_client(settings: Settings) -> DocumentIntelligenceClient:
    settings.assert_valid()
    return DocumentIntelligenceClient(
        endpoint=settings.endpoint,
        credential=AzureKeyCredential(settings.key),
    )