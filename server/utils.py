import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API client setup
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def generate_budget_tip(summary, income):
    try:
        # Format summary to show % of income
        income = float(income)
        breakdown = []
        for category, amount in summary.items():
            percent = (amount / income) * 100 if income > 0 else 0
            breakdown.append(f"{category}: ₹{amount} ({percent:.1f}%)")

        breakdown_str = "\n".join(breakdown)
        prompt = (
            f"My total monthly income is ₹{income}.\n"
            f"Here is my spending breakdown:\n{breakdown_str}\n\n"
            f"Based on this, give 2-3 short, specific tips to improve my budgeting."
        )

        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful financial budgeting assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"💡 AI Tip: Error generating tip: {str(e)}"
