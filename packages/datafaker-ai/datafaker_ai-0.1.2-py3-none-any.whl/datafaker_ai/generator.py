from .formatter import format_output
from .edge_case_handler import inject_edge_cases
from .prompts import build_prompt
import google.generativeai as genai

# ✅ Configure Gemini with your API key
genai.configure(api_key="AIzaSyD1noZlQc1lVHs2t4rIG9vC-7g6hnMLztk")

# 🚀 Use Gemini 1.5 Flash for fast, low-cost inference
model = genai.GenerativeModel("models/gemini-1.5-flash")

def call_model(prompt):
    response = model.generate_content(prompt)
    return response.text

def generate_dataset(description, num_samples=100, format='pandas', edge_cases=False, save_as=None):
    prompt = build_prompt(description, num_samples)
    data = call_model(prompt)
    df = format_output(data, fmt=format)

    if edge_cases:
        df = inject_edge_cases(df, description)

    # 🧾 Save output if requested
    if save_as == 'csv':
        df.to_csv("generated_data.csv", index=False)
    elif save_as == 'json':
        df.to_json("generated_data.json", orient="records", indent=2)
    elif save_as == 'both':
        df.to_csv("generated_data.csv", index=False)
        df.to_json("generated_data.json", orient="records", indent=2)

    return df

