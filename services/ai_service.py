from typing import Dict, Any, Optional
import openai
import time
import random
from core.config import (
    CHATGPT,
    OLLAMA,
    OPENAI_API_KEY
)

class AIService:
    def __init__(self, ai_mode: Optional[str] = None):
        """Initialize AI service with specified mode."""
        self.ai_mode = ai_mode
        if self.ai_mode == CHATGPT:
            openai.api_key = OPENAI_API_KEY
        self.primary_model = "gpt-3.5-turbo"
        self.alternate_models = ["gpt-4o-mini", "gpt-3.5-turbo", "o1-mini"]

    def get_stock_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Generate a summary of stock analysis using AI."""
        if not self.ai_mode:
            return None
            
        try:
            if self.ai_mode == CHATGPT:
                return self._get_chatgpt_summary(symbol, data)
            elif self.ai_mode == OLLAMA:
                return self._get_ollama_summary(symbol, data)
            else:
                return None
        except Exception as e:
            print(f"Error generating AI summary: {str(e)}")
            return None
    
    def _get_chatgpt_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Get summary using ChatGPT."""
        if not OPENAI_API_KEY:
            return "OpenAI API key not configured."
            
        try:
            # Prepare the prompt
            prompt = self._create_analysis_prompt(symbol, data)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing stock analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating ChatGPT summary: {str(e)}"
    
    def _get_ollama_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Get summary using Ollama."""
        try:
            # Implement Ollama API call here if needed
            return "Ollama integration not implemented yet."
        except Exception as e:
            return f"Error generating Ollama summary: {str(e)}"
    
    def _create_analysis_prompt(self, symbol: str, data: Dict[str, Any]) -> str:
        """Create a prompt for AI analysis."""
        metrics = data.get("metrics", {})
        
        prompt = f"""Analyze the stock {symbol} based on the following financial metrics:

Financial Metrics:
- Revenue: ${metrics.get('Revenue', 'N/A')}
- Gross Profit: ${metrics.get('Gross Profit', 'N/A')}
- Operating Income: ${metrics.get('Operating Income', 'N/A')}
- Net Income: ${metrics.get('Net Income', 'N/A')}
- Total Assets: ${metrics.get('Total Assets', 'N/A')}
- Total Liabilities: ${metrics.get('Total Liabilities', 'N/A')}
- Total Equity: ${metrics.get('Total Equity', 'N/A')}
- Operating Cash Flow: ${metrics.get('Operating Cash Flow', 'N/A')}
- Investing Cash Flow: ${metrics.get('Investing Cash Flow', 'N/A')}
- Financing Cash Flow: ${metrics.get('Financing Cash Flow', 'N/A')}

Please provide a comprehensive analysis including:
1. Financial Health Assessment
2. Profitability Analysis
3. Cash Flow Analysis
4. Key Risks and Opportunities
5. Investment Recommendation

Keep the analysis concise but thorough."""
        
        return prompt

    def _invoke_ai(self, prompt: str, retries: int = 3, delay: int = 5) -> str:
        """Invoke AI model with retries and fallback."""
        if self.ai_mode == CHATGPT:
            return self._invoke_chatgpt(prompt, retries, delay)
        else:
            return self._invoke_ollama(prompt)

    def _invoke_chatgpt(self, prompt: str, retries: int, delay: int) -> str:
        """Call OpenAI GPT API with retries & fallback models."""
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        for attempt in range(retries):
            model = self.primary_model if attempt == 0 else random.choice(self.alternate_models)

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
                print("🚨 Invalid API Key!")
                raise

            except Exception as e:
                print(f"⚠️ Error: {e}. Retrying...")
                time.sleep(delay)

        raise ValueError("Error: Unable to fetch response after all retries.")

    def _invoke_ollama(self, prompt: str) -> str:
        """Call Ollama API for analysis."""
        import ollama
        response = ollama.chat(
            model="deepseek-r1:latest",
            messages=[
                {
                    "role": "system",
                    "content": "Only return the final response. Do not include 'thinking','think', intermediate thoughts, or any additional commentary."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response["message"]["content"] 