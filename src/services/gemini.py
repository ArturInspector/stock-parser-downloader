import google.generativeai as genai
from typing import List

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_prompts(self, scenario: str) -> List[str]:
        if not self.api_key:
            raise ValueError("Gemini API key is missing")
            
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Create 5 search queries in English for finding stock videos based on the following scenario/description:
        {scenario}
        
        Queries should be:
        1. Specific and detailed
        2. Suitable for stock video search
        3. Using professional terms
        4. Copyright free context
        5. Original
        
        Format response as a simple list:
        1. [query 1]
        2. [query 2]
        etc.
        """
        
        response = model.generate_content(prompt)
        prompts = []
        for line in response.text.split('\n'):
            clean_line = line.strip()
            if clean_line and clean_line[0].isdigit():
                # Remove "1. " prefix
                parts = clean_line.split('. ', 1)
                if len(parts) > 1:
                    prompts.append(parts[1])
                    
        return prompts
