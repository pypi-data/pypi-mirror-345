# 🧬Dataset Generator

Generate synthetic datasets from natural language descriptions using Google's Gemini 1.5 Flash model. Ideal for data science, machine learning prototyping, and testing workflows with customizable, structured synthetic data.

---

## ✨ Features

- ⚡ Powered by Gemini 1.5 Flash (fast + cost-effective)
- 🧠 Natural language prompt → structured data
- 📦 Output in `pandas`, `CSV`, and `JSON`
- 🧪 Optional edge case injection for testing
- 🧾 Save datasets to local disk
- 🔐 Easy API key setup using `.env`

---

## 📦 Installation

Install from PyPI:

```bash
pip install datafaker-ai 0.1.5



git clone https://github.com/ahsanraza1457/deepfaker_ai.git
cd deepfaker_ai
pip install -r requirements.txt

🔐 Setup
Option 1: Using .env (for GitHub users)
Create a .env file in the root directory:
GEMINI_API_KEY=your_google_generativeai_api_key
from generator import generate_dataset

df = generate_dataset(
    description="Customer name, email, age, and signup date",
    num_samples=50
)

print(df.head())
Option 2: Pass Directly (for PyPI users)
df = generate_dataset(
    description="user profile data",
    num_samples=10,
    api_key="your_google_generativeai_api_key"
)



Save Output as CSV or JSON
generate_dataset(
    description="IoT device logs with timestamp, device_id, temperature",
    num_samples=100,
    save_as='csv'  # Options: 'csv', 'json', 'both'
)



🗂 Project Structure
├── generator/
│   ├── __init__.py
│   ├── generator.py           # Main interface
│   ├── formatter.py           # Formats model output
│   ├── prompts.py             # Builds prompt from description
│   ├── edge_case_handler.py   # Injects edge cases
│
├── .env                      
├── README.md
├── requirements.txt
└── setup.py / pyproject.toml  
