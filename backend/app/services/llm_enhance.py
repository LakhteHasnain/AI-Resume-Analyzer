import requests
from typing import Optional

HF_API_KEY = "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"  # Free tier available

class LLMEnhancer:
    @staticmethod
    def improve_resume(text: str, job_desc: Optional[str] = None) -> str:
        """Use Mistral-7B via Hugging Face API for suggestions."""
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
        prompt = f"""
        Analyze this resume and suggest 3 improvements:
        Resume: {text[:2000]}
        Job Description: {job_desc or "Not provided"}
        """
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            return response.json()[0]["generated_text"]
        except Exception as e:
            return f"AI suggestion disabled (enable API key): {str(e)}"