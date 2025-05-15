import re
from typing import List, Dict, Any, Optional

class LayoutPostprocessor:
    """
    Post-processes layout analysis results to enhance region classification
    based on content and positioning heuristics.
    """
    
    def __init__(self):
        # Compile regex patterns for better performance
        self.figure_patterns = re.compile(r'fig\.?|figure|diagram|plot|image|graph', re.IGNORECASE)
        self.table_patterns = re.compile(r'table|tabular|\|\s+\||\+\-+\+', re.IGNORECASE)
        self.list_patterns = re.compile(r'^(\d+\.|•|\*|\-)\s', re.MULTILINE)
        self.equation_patterns = re.compile(r'equation|=|\+|\-|\*|\/|\sum|\int|\prod|\div|\approx', re.IGNORECASE)
        self.title_patterns = re.compile(r'^[A-Z0-9][\w\s\.\:]{0,100}$', re.MULTILINE)
        
    def process_regions(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes all regions in all pages to enhance their classifications.
        
        Args:
            pages: A list of page dictionaries with layout analysis results
            
        Returns:
            A new list of page dictionaries with updated region types
        """
        enhanced_pages = []
        
        for page in pages:
            enhanced_results = []
            
            for region in page.get("results", []):
                # Apply enhancements to each region
                enhanced_region = self._enhance_region(region)
                enhanced_results.append(enhanced_region)
            
            # Create a new page dict with enhanced results
            enhanced_page = {
                "page": page.get("page", 1),
                "results": enhanced_results
            }
            enhanced_pages.append(enhanced_page)
            
        return enhanced_pages
    
    def _enhance_region(self, region: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhances a single region's classification based on its content and properties.
        
        Args:
            region: A region dictionary from the layout analysis
            
        Returns:
            An enhanced copy of the region dictionary
        """
        # Create a copy of the region to avoid modifying the original
        enhanced_region = region.copy()
        
        # Get the text content if available
        text = region.get("content", {}).get("text", "")
        
        # Skip empty regions or already specific classifications
        if not text or region.get("region_type") not in ["text", "unknown"]:
            return enhanced_region
        
        # Check for potential figures
        if self._is_figure(text, region):
            enhanced_region["region_type"] = "figure"
            return enhanced_region
        
        # Check for potential tables
        if self._is_table(text, region):
            enhanced_region["region_type"] = "table"
            return enhanced_region
        
        # Check for potential lists
        if self._is_list(text):
            enhanced_region["region_type"] = "list"
            return enhanced_region
        
        # Check for potential equations
        if self._is_equation(text):
            enhanced_region["region_type"] = "equation"
            return enhanced_region
        
        # Check for potential titles (short, capitalized text)
        if self._is_title(text, region):
            enhanced_region["region_type"] = "title"
            return enhanced_region
        
        # If we reach here, keep the original classification
        return enhanced_region
    
    def _is_figure(self, text: str, region: Dict[str, Any]) -> bool:
        """Determines if a region is likely a figure caption."""
        # Check for common figure indicators in text
        if self.figure_patterns.search(text):
            return True
        
        # Check for figure caption patterns (e.g., "Fig. 1")
        figure_caption = re.search(r'(^|\n)Fig(\.|ure)\s+\d+', text)
        if figure_caption:
            return True
        
        # Check if the region is likely a figure based on shape
        bbox = region.get("bbox_raw", [])
        if len(bbox) == 4:
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            aspect_ratio = width / height if height > 0 else 0
            
            # Figures often have width > height
            if aspect_ratio > 1.5 and len(text) < 200:
                return True
        
        return False
    
    def _is_table(self, text: str, region: Dict[str, Any]) -> bool:
        """Determines if a region is likely a table."""
        # Check for common table indicators
        if self.table_patterns.search(text):
            return True
        
        # Check for table caption patterns
        table_caption = re.search(r'(^|\n)Table\s+\d+', text)
        if table_caption:
            return True
        
        # Check for grid-like patterns in text
        lines = text.strip().split('\n')
        if len(lines) > 3:  # Tables usually have multiple rows
            # Check if lines have similar structures (potential table rows)
            spaces_in_lines = [len(re.findall(r'\s{2,}', line)) for line in lines]
            # If most lines have multiple double-spaces (potential column separators)
            if sum(1 for count in spaces_in_lines if count > 1) / len(spaces_in_lines) > 0.5:
                return True
        
        return False
    
    def _is_list(self, text: str) -> bool:
        """Determines if a region is likely a list."""
        # Check for list item patterns (numbered lists, bullet points)
        list_items = self.list_patterns.findall(text)
        # If multiple list items are found
        return len(list_items) > 1
    
    def _is_equation(self, text: str) -> bool:
        """Determines if a region is likely an equation."""
        # Check for equation indicators
        if self.equation_patterns.search(text):
            # Look for a higher density of mathematical symbols compared to words
            math_symbols = len(re.findall(r'[+\-*/=\(\){}[\]^]', text))
            word_count = len(re.findall(r'\b\w+\b', text))
            
            # If the ratio of math symbols to words is high
            return math_symbols > 0 and (math_symbols / (word_count + 1)) > 0.3
        
        return False
    
    def _is_title(self, text: str, region: Dict[str, Any]) -> bool:
        """Determines if a region is likely a title or heading."""
        # Skip long text - titles are usually short
        if len(text) > 100:
            return False
        
        # Check if the text matches title patterns
        if self.title_patterns.search(text):
            # Check if the region is near the top of the page
            bbox_norm = region.get("bbox_norm", [])
            if len(bbox_norm) == 4 and bbox_norm[1] < 0.3:  # Top 30% of page
                return True
            
            # Check for section numbering patterns
            section_pattern = re.search(r'^[A-Z]\.|\d+\.\d+|\d+\)', text)
            if section_pattern:
                return True
            
            # Check if the text is bold (often titles)
            # This would require font information, which we don't have here
            
        return False
