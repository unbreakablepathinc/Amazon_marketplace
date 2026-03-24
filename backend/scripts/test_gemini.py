"""
Manual test: verify Gemini API key and try generateContent with free-tier models.
Run from backend: python scripts/test_gemini.py

See https://ai.google.dev/gemini-api/docs/models and .../rate-limits.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings

MODELS = (
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-3-flash-preview",
)


def main():
    api_key = settings.gemini_api_key
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in backend/.env")
        return 1
    print("GEMINI_API_KEY: loaded (len=%d)" % len(api_key))

    from google import genai
    client = genai.Client(api_key=api_key)

    print("\n--- Testing generateContent (free-tier models) ---")
    for model in MODELS:
        print("\n  %s ..." % model, end=" ")
        try:
            r = client.models.generate_content(
                model=model,
                contents="Reply with exactly: OK",
            )
            text = (getattr(r, "text", None) or "").strip()
            print("SUCCESS ->", repr(text[:60]))
            print("\n  -> Use this model; cluster will try the same list.")
            return 0
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                print("429 QUOTA EXCEEDED (free tier limit; wait or new key)")
            elif "404" in err or "NOT_FOUND" in err:
                print("404 MODEL NOT FOUND")
            elif "400" in err or "FAILED_PRECONDITION" in err or "location" in err.lower():
                print("400 LOCATION NOT SUPPORTED (API not available in your region)")
            else:
                print("ERROR:", err[:120])

    print("\n--- All models failed ---")
    print("  429 = quota exceeded: wait or create new key at https://aistudio.google.com/apikey")
    print("  400 = location not supported: Gemini API may not be available in your country")
    return 1


if __name__ == "__main__":
    sys.exit(main())
