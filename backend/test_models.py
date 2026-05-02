from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
import glob
upload_files = glob.glob(r"C:\games\DocuVerify\backend\uploads\*.jpeg")
if not upload_files:
    print("File not found")
else:
    file_path = upload_files[0]
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    for model_name in ["gemini-2.5-flash", "models/gemini-2.5-flash", "gemini-2.0-flash", "models/gemini-2.0-flash", "gemini-flash-latest"]:
        try:
            print(f"Testing {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg"),
                    "Extract name",
                ],
            )
            print(f"Success with {model_name}: {response.text[:50]}")
            break
        except Exception as e:
            print(f"Failed with {model_name}: {e}")
