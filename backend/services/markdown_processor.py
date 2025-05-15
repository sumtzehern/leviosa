import os
from typing import List, Optional, Dict, Any, AsyncGenerator
import requests
import json
import asyncio
import aiohttp
from models.schema import OCRResponse, OCRPageResult, OCRResult, LayoutAnalysisResponse, LayoutPageResult, LayoutResult

class MarkdownProcessor:
    """
    Converts layout-annotated OCR results into Markdown using OpenAI LLM.
    Includes streaming support for long PDFs and token-efficient batching.
    """
    def __init__(self, llm_api_key: Optional[str] = None):
        """Initialize with optional API key for LLM service"""
        self.api_key = llm_api_key or os.environ.get("OPENAI_API_KEY")
    
    async def convert_layout_json_to_markdown(self, layout_result: LayoutAnalysisResponse) -> str:
        """
        Converts layout-aware OCR JSON directly into Markdown using LLM.
        Processes all pages, not just the first one.
        """
        if not self.api_key:
            raise ValueError("No API key provided for LLM markdown conversion.")

        # Load prompt
        prompt_path = os.path.join("prompts", "markdown_conversion.txt")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = (
                "You are an expert document formatter.\n"
                "Convert layout-aware OCR regions into structured Markdown.\n"
                "Use the region type to choose the right formatting: headings, paragraphs, lists, tables, etc."
            )

        # Process all pages, not just the first one
        structured_document = {
            "pages": [
                {
                    "page": page_data.page,
                    "regions": [
                        {
                            "type": r.region_type,
                            "bbox": r.bbox_norm,
                            "content": r.content
                        }
                        for r in sorted(page_data.results, key=lambda r: r.bbox_norm[1])  # top to bottom
                    ]
                }
                for page_data in layout_result.pages
            ]
        }

        try:
            print("Sending multi-page layout JSON to OpenAI...")

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
                            "content": f"Convert the following multi-page document layout into clean Markdown:\n\n{json.dumps(structured_document, indent=2)}"
                        }
                    ],
                    "temperature": 0.2
                }
            )

            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Error in LLM response: {json.dumps(response_data)}"

        except Exception as e:
            return f"Failed to call LLM: {str(e)}"
            
    async def direct_layout_to_markdown(self, layout_json: Dict[str, Any]) -> str:
        """
        Sends the full layout JSON directly to LLM without any pre-processing.
        This method allows sending the complete structured document to the LLM.
        
        Args:
            layout_json: The complete layout analysis result as a dictionary
            
        Returns:
            The markdown formatted document as returned by the LLM
        """
        if not self.api_key:
            raise ValueError("No API key provided for LLM markdown conversion.")

        # Load prompt
        prompt_path = os.path.join("prompts", "markdown_conversion.txt")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = (
                "You are an expert document formatter.\n"
                "Convert layout-aware OCR regions into structured Markdown.\n"
                "Use the region type to choose the right formatting: headings, paragraphs, lists, tables, etc."
            )

        try:
            print("Sending full layout JSON to OpenAI...")

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
                            "content": f"Convert the following complete document layout into clean Markdown:\n\n{json.dumps(layout_json, indent=2)}"
                        }
                    ],
                    "temperature": 0.2
                }
            )

            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                return f"Error in LLM response: {json.dumps(response_data)}"

        except Exception as e:
            return f"Failed to call LLM: {str(e)}"
            
    async def process_layout_incrementally(self, layout_result: LayoutAnalysisResponse) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process layout pages incrementally and yield results as they're ready.
        This is used for streaming responses.
        
        Args:
            layout_result: The complete layout analysis result
            
        Yields:
            A dictionary with page number and markdown content for each page
        """
        for page_data in layout_result.pages:
            structured_page = {
                "page": page_data.page,
                "regions": [
                    {
                        "type": r.region_type,
                        "bbox": r.bbox_norm,
                        "content": r.content
                    }
                    for r in sorted(page_data.results, key=lambda r: r.bbox_norm[1])  # top to bottom
                ]
            }
            
            markdown = await self._process_single_page(structured_page)
            
            yield {
                "page": page_data.page,
                "markdown": markdown
            }
            
    async def _process_single_page(self, page_data: Dict[str, Any]) -> str:
        """
        Process a single page of layout data.
        
        Args:
            page_data: Structured page data with region information
            
        Returns:
            Markdown representation of the page
        """
        prompt_path = os.path.join("prompts", "markdown_conversion.txt")
        try:
            with open(prompt_path, "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = (
                "You are an expert document formatter.\n"
                "Convert layout-aware OCR regions into structured Markdown.\n"
                "Use the region type to choose the right formatting: headings, paragraphs, lists, tables, etc."
            )
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
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
                                "content": f"Convert the following page layout into clean Markdown:\n\n{json.dumps(page_data, indent=2)}"
                            }
                        ],
                        "temperature": 0.2
                    }
                ) as response:
                    response_data = await response.json()
                    
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        return response_data["choices"][0]["message"]["content"]
                    else:
                        return f"Error in LLM response: {json.dumps(response_data)}"
        except Exception as e:
            return f"Failed to process page: {str(e)}"
            
    async def layout_to_markdown(self, layout_result: LayoutAnalysisResponse) -> str:
        """
        Process all pages and combine into a single markdown document.
        
        Args:
            layout_result: The complete layout analysis result
            
        Returns:
            Complete markdown document
        """
        markdown_parts = []
        
        async for page_result in self.process_layout_incrementally(layout_result):
            markdown_parts.append(page_result["markdown"])
            
        return "\n\n".join(markdown_parts)