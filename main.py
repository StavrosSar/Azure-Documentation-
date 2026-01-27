from dotenv import load_dotenv
import os

load_dotenv()

print("main.py is running")
print("AZURE_DOCINTEL_ENDPOINT:", os.getenv("AZURE_DOCINTEL_ENDPOINT"))
print("AZURE_DOCINTEL_MODEL_ID:", os.getenv("AZURE_DOCINTEL_MODEL_ID"))
