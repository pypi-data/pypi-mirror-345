from .formatter import format_output
from .edge_case_handler import inject_edge_cases
from .prompts import build_prompt
import google.generativeai as genai
from dotenv import load_dotenv
import os

def configure_gemini(api_key=None):
    """
    Configures the Gemini API client.
    Priority: passed `api_key` > .env (GEMINI_API_KEY)
    """
    if api_key:
        final_key = api_key
    else:
        load_dotenv()
        final_key = os.getenv("GEMINI_API_KEY")

    if not final_key:
        raise ValueError(
            "❌ Gemini API key not found.\n"
            "Please pass it directly as `api_key='...'` or set it in a `.env` file."
        )

    genai.configure(api_key=final_key)
    return genai.GenerativeModel("models/gemini-1.5-flash")


def generate_dataset(description, num_samples=100, format='pandas', edge_cases=False, save_as=None, api_key=None):
    """
    Generates a dataset using Google's Gemini 1.5 Flash.

    Args:
        description (str): Dataset description in plain English.
        num_samples (int): Number of rows to generate.
        format (str): Output format ('pandas' by default).
        edge_cases (bool): Whether to inject edge cases.
        save_as (str): One of ['csv', 'json', 'both', None].
        api_key (str): Direct Gemini API key (overrides .env).
    """
    model = configure_gemini(api_key)
    prompt = build_prompt(description, num_samples)
    response = model.generate_content(prompt)
    data = response.text
    df = format_output(data, fmt=format)

    if edge_cases:
        df = inject_edge_cases(df, description)

    if save_as == 'csv':
        df.to_csv("generated_data.csv", index=False)
    elif save_as == 'json':
        df.to_json("generated_data.json", orient="records", indent=2)
    elif save_as == 'both':
        df.to_csv("generated_data.csv", index=False)
        df.to_json("generated_data.json", orient="records", indent=2)

    return df
