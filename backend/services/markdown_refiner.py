import os
from typing import Optional
import requests
import json

class MarkdownRefiner:
    """
    Refines raw markdown from OCR/layout processing to create clean, display-ready markdown.
    Uses LLM to improve formatting, fix OCR errors, and standardize document structure.
    """
    
    def __init__(self, llm_api_key: Optional[str] = None):
        self.api_key = llm_api_key or os.environ.get("OPENAI_API_KEY")
        
    def refine_markdown(self, raw_markdown: str) -> str:
        """
        Refines raw markdown using LLM to create clean, structured output
        that's ready for display and rendering.
        
        Args:
            raw_markdown: The raw markdown string from initial processing
            
        Returns:
            Refined, cleaned markdown with consistent structure
        """
        if not self.api_key:
            raise ValueError("No API key provided for LLM markdown refinement.")
            
        # Load the refinement prompt
        prompt_path = os.path.join("prompts", "markdown_refinement.txt")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = (
                "You are an expert Markdown formatter.\n"
                "Refine the given markdown to be clean, consistent, and free of OCR errors.\n"
                "Fix formatting, clean up tables, and ensure proper document structure."
            )
            
        try:
            print("Sending markdown for refinement...")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": raw_markdown
                        }
                    ],
                    "temperature": 0.1  # Low temperature for consistent formatting
                }
            )
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Error in LLM response: {json.dumps(response_data)}"
                
        except Exception as e:
            return f"Failed to refine markdown: {str(e)}" 