from google import genai
import os
import json
import re

# 🔑 Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_diagram(user_input: str):
    text = ""

    try:
        # 🧠 Proper structured prompt (NO nesting issues)
        structured_prompt = f"""
Convert the following user input into a process diagram JSON.

STRICT RULES:
- Use ONLY these component types:
  - compressor
  - dryer
  - feeder

- DO NOT use: pump, tank, heat exchanger

- Always return valid JSON ONLY (no explanation, no text)

Return format:
{{
  "components": [
    {{ "id": "c1", "type": "compressor", "x": 100, "y": 100 }}
  ],
  "connections": [
    {{ "from": "c1", "to": "c2" }}
  ]
}}

User input:
{user_input}
"""

        # 📡 Call Gemini API
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=structured_prompt
        )

        # 🧾 Get response text
        text = response.text.strip()

        # 🧹 Remove markdown (```json)
        text = re.sub(r"```json|```", "", text).strip()

        # 🔍 Extract JSON safely
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

        # 🧠 Parse JSON
        parsed = json.loads(text)

        # ✅ Extra safety validation
        if "components" not in parsed or "connections" not in parsed:
            raise ValueError("Invalid response format from AI")

        return parsed

    except Exception as e:
        return {
            "error": str(e),
            "raw": text
        }