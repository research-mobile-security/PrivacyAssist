import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def ask_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"]

def parse_response(response):
    response = response.strip()
    try:
        parsed = json.loads(response)
        compliance = parsed.get("is_compliant", "Undetermined")
        reason = parsed.get("reason", "")
        return compliance, reason
    except Exception:
        return "Undetermined", response[:300] + ("..." if len(response) > 300 else "")

def build_llm_prompt(device_id, package_name, granted, collected, shared):
    prompt = f"""
You are a mobile security analyst.

Your task is to assess whether an Android application complies with its declared privacy practices on the Google Play Store.  
To do this, compare the **actual permissions granted on the device** with the **data the app claims to collect and share**.

---

 **App Information**
- Package name: `{package_name}`
- Device ID: `{device_id}`

 **Granted Permissions on Device**
{json.dumps(granted, indent=2)}

 **Declared Data Collected**
{json.dumps(collected, indent=2)}

 **Declared Data Shared**
{json.dumps(shared, indent=2)}

---

 Provide your privacy compliance evaluation in **pure JSON**, using this format only:

{{
  "is_compliant": true | false,
  "reason": "<concise explanation in English (max 2 lines)>"
}}

Do not add anything else outside the JSON block.
"""
    return prompt

