import json
import re

def extract_json(text):
    try:
        # Look for the first JSON array in the text
        match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON array found.")
        json_text = match.group(0)
        return json.loads(json_text)
    except Exception as e:
        raise ValueError("Model output could not be parsed as JSON.") from e

def format_output(model_output, fmt='pandas'):
    data = extract_json(model_output)
    if fmt == 'pandas':
        import pandas as pd
        return pd.DataFrame(data)
    return data
