import os
from typing import List, Optional
import requests
import json
from models.schema import OCRResponse, OCRPageResult, OCRResult

class MarkdownProcessor:
    """
    Process OCR results into Markdown format
    """
    
    def __init__(self, llm_api_key: Optional[str] = None):
        """Initialize with optional API key for LLM service"""
        self.api_key = llm_api_key or os.environ.get("OPENAI_API_KEY")
        
    def ocr_to_raw_text(self, ocr_response: OCRResponse) -> str:
        """
        Convert OCR results to raw text, preserving page structure
        - Maintains page breaks with markers
        - Preserves reading order (top to bottom)
        """
        raw_text = ""
        
        for page_result in ocr_response.pages:
            page_num = page_result.page
            
            # Add page marker
            if raw_text:  # Not the first page
                raw_text += f"\n\n--- Page {page_num} ---\n\n"
            else:
                raw_text += f"--- Page {page_num} ---\n\n"
            
            for result in page_result.results:
                raw_text += f"{result.text}\n"
        
        return raw_text
    
    def convert_to_markdown(self, ocr_response: OCRResponse) -> str:
        """
        Process OCR results into markdown using LLM
        """
        # First convert to raw text
        raw_text = self.ocr_to_raw_text(ocr_response)
        
        # If no API key, just return the raw text
        if not self.api_key:
            return raw_text

        # Load the prompt from the file
        prompt_path = os.path.join("prompts", "markdown_conversion.txt")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            # Fallback to default prompt if file not found
            system_prompt = "You are an expert at converting raw OCR text into well-structured Markdown. Preserve the document structure, identify headers, lists, tables, and other elements. Use appropriate Markdown formatting for each element type."
                
        # Use OpenAI to convert to markdown
        try:
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
                            "content": f"Convert this OCR text to well-formatted Markdown:\n\n{raw_text}"
                        }
                    ],
                    "temperature": 0.3
                }
            )
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Error processing markdown: {json.dumps(response_data)}"
                
        except Exception as e:
            return f"Error converting to markdown: {str(e)}\n\nRaw text:\n{raw_text}"