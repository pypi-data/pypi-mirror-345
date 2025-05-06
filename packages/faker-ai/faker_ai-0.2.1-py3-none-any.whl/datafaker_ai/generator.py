from .formatter import format_output
from .edge_case_handler import inject_edge_cases
from .prompts import build_prompt
import google.generativeai as genai
import os
import pandas as pd


API_KEY = ""
# ✅ Configure Gemini with your API key
genai.configure(api_key=API_KEY)

# 🚀 Use Gemini 1.5 Flash for fast, low-cost inference
model = genai.GenerativeModel("models/gemini-1.5-flash")

def call_model(prompt):
    response = model.generate_content(prompt)
    return response.text

def enforce_sample_count(df: pd.DataFrame, expected: int) -> pd.DataFrame:
    actual = len(df)
    if actual > expected:
        return df.iloc[:expected]
    elif actual < expected:
        padding = pd.DataFrame([df.iloc[-1].to_dict()] * (expected - actual))
        return pd.concat([df, padding], ignore_index=True)
    return df

def define_API_KEY(api_key):
    global API_KEY
    API_KEY = api_key

    
def generate_dataset(description, num_samples=100, format='pandas', edge_cases=False, save_as=None, save_dir=None):
    """
    Generate synthetic dataset using Gemini model.

    Parameters:
    - description: str
    - num_samples: int
    - format: str, either 'pandas' or 'json'
    - edge_cases: bool, if True will inject edge cases
    - save_as: str, 'csv', 'json', or 'both'
    - save_dir: str, custom directory to save output files

    Returns:
    - df: pandas.DataFrame
    """
   

    if not API_KEY:
        raise ValueError("API key is not set. Please call define_API_KEY() with your API key.")
    
    prompt = build_prompt(description, num_samples)
    raw_output = call_model(prompt)
    df = format_output(raw_output, fmt=format)

    # 🔄 Ensure the dataset has exactly `num_samples`
    df = enforce_sample_count(df, num_samples)

    if edge_cases:
        df = inject_edge_cases(df, description)

    # Set default save_dir to current working directory
    save_dir = save_dir or os.getcwd()
    os.makedirs(save_dir, exist_ok=True)

    if save_as == 'csv' or save_as == 'both':
        csv_path = os.path.join(save_dir, "generated_data.csv")
        df.to_csv(csv_path, index=False)

    if save_as == 'json' or save_as == 'both':
        json_path = os.path.join(save_dir, "generated_data.json")
        df.to_json(json_path, orient="records", indent=2)

    return df
