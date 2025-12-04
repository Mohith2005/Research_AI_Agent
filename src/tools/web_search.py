# src/tools/web_search.py
import aiohttp
import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class WebSearchTool:
    def __init__(self, settings):
        self.settings = settings
        self.session = None
    
    async def search_async(self, query: str, max_results: int = 5) -> List[Dict]:
        """Perform web search and content extraction"""
        
        # Use SerpAPI or similar service for search results
        search_results = await self._perform_search(query, max_results)
        
        # Extract and clean content from top results
        content_tasks = []
        for result in search_results[:max_results]:
            content_tasks.append(self._extract_content(result['url']))
        
        contents = await asyncio.gather(*content_tasks, return_exceptions=True)
        
        # Combine results with content
        for i, content in enumerate(contents):
            if not isinstance(content, Exception):
                search_results[i]['content'] = content
        
        return search_results
    
    async def _perform_search(self, query: str, max_results: int) -> List[Dict]:
        """Perform search using search API"""
        
        # Implementation using SerpAPI or similar
        # This is a simplified version
        async with aiohttp.ClientSession() as session:
            params = {
                'q': query,
                'api_key': self.settings.serpapi_key,
                'engine': 'google',
                'num': max_results
            }
            
            async with session.get('https://serpapi.com/search', params=params) as response:
                data = await response.json()
                return [{
                    'title': result.get('title'),
                    'url': result.get('link'),
                    'snippet': result.get('snippet')
                } for result in data.get('organic_results', [])]
    
    async def _extract_content(self, url: str) -> str:
        """Extract main content from a webpage"""
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                
                # Extract main content using various strategies
                content = await self._extract_main_content(page)
                
                await browser.close()
                return content
                
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    async def _extract_main_content(self, page) -> str:
        """Extract main content using multiple strategies"""
        
        # Strategy 1: Try common content selectors
        content_selectors = [
            'article',
            '.content',
            '.main-content',
            '#content',
            '.post-content',
            '[role="main"]'
        ]
        
        for selector in content_selectors:
            element = await page.query_selector(selector)
            if element:
                content = await element.text_content()
                if content and len(content) > 200:  # Reasonable content length
                    return content.strip()
        
        # Strategy 2: Fallback to body content
        body = await page.query_selector('body')
        if body:
            return (await body.text_content()).strip()
        
        return "No content extracted"