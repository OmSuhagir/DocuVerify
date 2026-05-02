import json
import os
from pathlib import Path
from typing import Dict, Any
from ..config import settings


def extract_with_gemini(file_path: str, category: str = None) -> Dict[str, Any]:
    if not settings.GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY is not configured.")

    # Import the Google Gemini client. Support multiple import paths to
    # handle different package layouts and avoid confusing ImportErrors
    # caused by other `google` packages shadowing the generative client.
    try:
        # Preferred import for the official package: `google-generativeai`
        import google.generativeai as genai
        try:
            from google.generativeai import types
        except Exception:
            types = getattr(genai, "types", None)
    except Exception:
        try:
            # Fallback for older layouts or alternate installs
            from google import genai
            from google.genai import types
        except Exception as e:
            raise ImportError(
                "Google Generative AI client not found. Install 'google-generativeai'"
            ) from e

    # Support either the newer `google.genai.Client` API or the older
    # `google.generativeai` helpers. Decide at runtime which to use.
    using_client_api = hasattr(genai, "Client")

    if using_client_api:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    else:
        # Configure the older package which exposes `GenerativeModel`
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        except Exception:
            # Some installs expose `configure` at module level, others may not.
            pass

    # Resolve to absolute path so file reads always work
    abs_path = os.path.abspath(file_path)

    with open(abs_path, "rb") as f:
        file_bytes = f.read()

    ext = Path(abs_path).suffix.lower()
    mime_type = "image/jpeg"
    if ext == ".png":
        mime_type = "image/png"
    elif ext == ".pdf":
        mime_type = "application/pdf"

    prompt = (
        'Extract all the available fields from this document and return ONLY valid JSON '
        'with no markdown formatting or extra text: '
        '{"name": "...", "dob": "...", "address": "...", "city": "...", "degree_title": "...", "candidate_name": "...", "date_year": "..."}. '
        'Use exactly these keys. If a field is not found or not applicable to this document, use null. '
        'For dob use format DD/MM/YYYY if possible. '
        'RULES: '
        '1. If this is a Birth Certificate and the child\'s name is only a first name, '
        'construct the full name by combining the child\'s name with the father\'s name and surname (if present) to form the full "name" field. '
        'For example, if the child is ANCHIT and the father is JAYANT S. CHEDGE, extract ANCHIT JAYANT CHEDGE. '
        '2. For Address extraction, do NOT include prefixes like S/O, C/O, W/O, D/O, or the guardian\'s name in the "address" field. '
        'The address must only contain physical location details (street, area, city, pincode, etc.).'
    )

    # Try a few model names. Use the correct API depending on the installed package.
    for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
        try:
            if using_client_api:
                # Newer `google.genai.Client` style
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            else:
                # Older `google.generativeai` style
                model = genai.GenerativeModel(model_name)
                gen_config = types.GenerationConfig(response_mime_type="application/json")
                response = model.generate_content(
                    [types.Part.from_bytes(data=file_bytes, mime_type=mime_type), prompt],
                    generation_config=gen_config,
                )

            print(f"[Gemini] Used model: {model_name}")
            break
        except Exception as e:
            print(f"[Gemini] Model {model_name} failed: {e}")
            response = None
            continue

    if response is None:
        raise Exception("All Gemini models failed.")

    text = response.text.strip()
    print(f"[Gemini] Raw response: {text[:300]}")

    # Strip markdown code fences if present
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                parsed = json.loads(part)
                return parsed
            except Exception:
                continue
    
    try:
        parsed = json.loads(text)
        return parsed
    except json.JSONDecodeError as e:
        print(f"[Gemini] Failed to parse JSON response: {e}\nResponse was: {text}")
        raise
