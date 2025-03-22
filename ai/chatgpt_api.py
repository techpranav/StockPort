import openai
import time
import random
import ollama
import re
from util.Utils import *
from constants.Constants import *

CHATGPT_MODE = "CHATGPT"
OLLAMA_MODE = "OLLAMA"

MODE= OLLAMA_MODE


# Define multiple models for fallback
PRIMARY_MODEL = "gpt-3.5-turbo"
ALTERNATE_MODELS = [ "gpt-4o-mini","gpt-3.5-turbo","o1-mini"]

# Set OpenAI API keys
PAID_KEY = "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"
# FREE_KEY = ["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","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"]
FREE_KEY = "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"

# Start with the free API key
OPENAI_API_KEY = PAID_KEY


def invoke_gpt(prompt, retries=3, delay=5):

    if(MODE == CHATGPT_MODE):
        return invoke_chatgpt(prompt, retries, delay)
    else:
        return invoke_ollama(prompt)



def remove_think_block(text):
    """
    Remove the complete <think>...</think> block from the text.
    """
    # The DOTALL flag makes the dot match newline characters as well.
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()
def invoke_ollama(prompt):
    response = ollama.chat(
        model="deepseek-r1:latest",
        messages=[
            {"role": "system",
             "content": "Only return the final response. Do not include 'thinking','think', intermediate thoughts, or any additional commentary."},
            {"role": "user", "content": prompt}
        ]
    )

    ret_response = remove_think_block(response["message"]["content"])
    print(ret_response)  # Should return only the joke
    return ret_response

def invoke_chatgpt(prompt, retries=3, delay=5):
    """Calls OpenAI GPT API with retries & fallback models."""
    global OPENAI_API_KEY  # Declare global before modifying

    openai.api_key = OPENAI_API_KEY
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    for attempt in range(retries):
        model = PRIMARY_MODEL if attempt == 0 else random.choice(ALTERNATE_MODELS)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except openai.RateLimitError:
            print(f"⚠️ Rate Limit Exceeded (429). Switching to model: {model} and retrying...")
            time.sleep(delay)

        except openai.AuthenticationError:
            print("🚨 Invalid API Key! Switching to paid key...")
            OPENAI_API_KEY = FREE_KEY  # ✅ Correctly modify global variable
            openai.api_key = FREE_KEY
            client = openai.OpenAI(api_key=PAID_KEY)  # Reinitialize client with new key

        except openai.Timeout:
            print("⏳ Request timed out. Retrying...")
            time.sleep(delay)

        except openai.APIError as e:
            print(f"❌ API Error ({e}): Retrying in {delay} seconds...")

        except openai.NotFoundError as e:
            print(f"❌ Model not found Error ({e}): Retrying in {delay} seconds...")
            if model in ALTERNATE_MODELS:
                ALTERNATE_MODELS.remove(model)

        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}. Retrying...")

        time.sleep(delay)  # Wait before retrying

    print("❌ All retries failed.")
    raise ValueError("Error: Unable to fetch response.")


def get_stock_summary(stock, company_info, financials_csv):
    """Generates stock summary using GPT."""

    pre_prompt=f"""
Analyze the given penny stock in detail, covering its financial health, competitive positioning, valuation, and investment potential. Your response should be well-structured with clear **headings, subheadings, financial insights, and formatted for documentation purposes**.   

---  

### **1. Company Overview & Business Model**  
- **Core Business & Industry Overview**: Describe the company's focus, sector, and overall industry trends.  
- **Company Background & History**: Summarize its founding, evolution, and key milestones.  
- **Products, Services & Revenue Streams**: Outline its offerings and how it generates revenue.  
- **Unique Selling Proposition (USP)**: Identify factors that differentiate it from competitors.  
- **Management & Insider Holdings**: Assess the leadership team and insider ownership levels.  

### **2. Market Position & Competitive Landscape**  
- **Industry Trends**: Key market movements affecting the company.  
- **Competitor Benchmarking**: Compare the company to similar penny stocks and small-cap players.  
- **Market Share & Growth Potential**: Evaluate its position and future expansion opportunities.  

### **3. Financial Performance & Key Metrics (Latest Quarter & Full Year)**  
- **Revenue Growth (YoY & QoQ)**: Assess sales trends and sustainability.  
- **Net Profit/Loss & Long-Term Trend**: Analyze profitability over the past 3-5 years.  
- **Profit Margins**: Examine Gross, Operating, and Net margins.  
- **Cash Flow Strength**: Evaluate Operating Cash Flow & Free Cash Flow stability.  
- **Balance Sheet Overview**: Breakdown of Total Assets, Liabilities, and Debt/Equity position.  
- **Liquidity Metrics**: Current Ratio & Quick Ratio to assess short-term financial health.  
- **Earnings Per Share (EPS) Trend**: Monitor EPS performance over time.  

### **4. Valuation & Comparative Analysis**  
- **Price-to-Earnings (P/E) vs. Industry Benchmark**  
- **Price-to-Free Cash Flow (P/FCF) & Sustainability**  
- **Enterprise Value-to-EBITDA (EV/EBITDA) Comparison**  
- **Price-to-Sales (P/S) & Price-to-Book (P/B) Multiples**  
- **Discounted Cash Flow (DCF) Fair Value Estimate** (If available)  

### **5. Technical Analysis & Trading Trends**  
- **Stock Performance Analysis:**  
  - Year-to-Date (YTD) Return, 1-Year, 3-Year, and 5-Year Performance  
  - 3-Year Maximum Drawdown  
- **Momentum & Volatility Indicators:**  
  - 52-Week High/Low  
  - Relative Strength Index (RSI) for trend assessment  
  - 50-Day & 200-Day Moving Averages  
  - Trading Volume & Liquidity Considerations  

### **6. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)**  
- **Strengths:** Competitive advantages & business resilience.  
- **Weaknesses:** Operational, financial, or strategic limitations.  
- **Opportunities:** Growth drivers, new market entry, M&A potential.  
- **Threats:** Industry disruptions, regulatory concerns, economic risks.  

### **7. Future Growth Prospects & Strategic Direction (2025 & Beyond)**  
- **Expansion Strategies & Market Entry Plans**  
- **Innovation & R&D Impact on Growth**  
- **Potential Mergers, Acquisitions, or Partnerships**  
- **Projected Revenue & Profitability Trends**  

### **8. Investment Risks & Key Concerns**  
- **Liquidity & Volatility Risks:** Assess tradability and market fluctuations.  
- **Financial Health Risks:** Potential insolvency, dilution risks, debt concerns.  
- **Regulatory & Compliance Issues:** Legal red flags or pending investigations.  
- **Macroeconomic Risks:** Impact of interest rates, inflation, and economic downturns.  

### **9. Final Investment Decision: BUY / HOLD / SELL**  
- **Investment Recommendation:** Categorize the stock as:  
  - **BUY** – Strong upside potential, backed by financials & growth outlook.  
  - **HOLD** – Balanced risk-reward scenario, awaiting further catalysts.  
  - **SELL** – Overvalued, weak fundamentals, or high risk.  
- **Key Justifications:** Support the decision with **quantitative and qualitative insights**.  

### **10. References & Additional Insights**  
- Provide credible links to **Yahoo Finance**, company filings, and relevant news reports.  
- Ensure the analysis is based on **recent data** and reflects the current market conditions.  

---  
"""

    prompt = f"""
    
**Action:** Perform the analysis using the stock details provided below. Ensure structured formatting suitable for documentation.
    {company_info}
    
    Use Below Financials for reference : 
    {financials_csv}
    """

    # Store the prompt in a file
    with open(f"{getSymbolOutputDirectory(stock)}\\{stock}_analysis_prompt.txt", "w", encoding="utf-8") as file:
        file.write(prompt)

    print(f"\n\n ################################################# \n {prompt} \n\n ############################################# \n")
    # return invoke_gpt(prompt)
    return " "

def getOverallShortSummary(gptSummary):
    prompt = f"Summarize the stock analysis briefly in a natural tone. {gptSummary}"
    return invoke_gpt(prompt)

def getShortSummary(gptSummary):
    prompt = f"Summarize key investment factors in one paragraph. Final Investment Decision: BUY / HOLD / SELL  {gptSummary}"
    return invoke_gpt(prompt)
