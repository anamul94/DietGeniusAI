import json
import re

def extract_json_from_response(response_text: str):
    # Try to find the first valid JSON block using regex
    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Try extracting the first JSON object directly
        try:
            decoder = json.JSONDecoder()
            json_str, _ = decoder.raw_decode(response_text)
            return json_str
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not extract valid JSON: {e}")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON block: {e}")