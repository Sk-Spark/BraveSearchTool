"""
title: Brave Web Search with Website Content Processing
author: Assistant
author_url: https://github.com
git_url: https://github.com/username/brave-web-search
description: A tool that performs web searches using Brave Search and returns processed content from websites
version: 0.1.3
licence: MIT
"""

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Optional, List, Callable, Any, Dict
import unicodedata
import re
from urllib.parse import urlparse
from datetime import datetime
import concurrent.futures
import json
from collections import defaultdict

class HelpFunctions:
    def __init__(self):
        pass

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url

    def generate_excerpt(self, content, max_length=200):
        return content[:max_length] + "..." if len(content) > max_length else content

    def format_text(self, original_text):
        soup = BeautifulSoup(original_text, "html.parser")
        formatted_text = soup.get_text(separator=" ", strip=True)
        formatted_text = unicodedata.normalize("NFKC", formatted_text)
        formatted_text = re.sub(r"\s+", " ", formatted_text)
        formatted_text = formatted_text.strip()
        formatted_text = self.remove_emojis(formatted_text)
        return formatted_text

    def remove_emojis(self, text):
        return "".join(c for c in text if not unicodedata.category(c).startswith("So"))

    def truncate_to_n_words(self, text, token_limit):
        tokens = text.split()
        truncated_tokens = tokens[:token_limit]
        return " ".join(truncated_tokens)

    def extract_main_points(self, content: str, max_points: int = 5) -> List[str]:
        """Extract key sentences from the content"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return sentences[:max_points]

    def categorize_content(self, content: str) -> Dict[str, str]:
        """Categorize content into sections based on common patterns"""
        sections = defaultdict(str)
        
        # Try to identify definition or overview
        if match := re.search(r'([^.!?]*(?:is|are|refers to)[^.!?]*[.!?])', content):
            sections["overview"] = match.group(1).strip()
            
        # Look for examples
        examples = re.findall(r'(?:example|instance|case)[^.!?]*[.!?]', content, re.IGNORECASE)
        if examples:
            sections["examples"] = " ".join(examples[:2])
            
        # Look for technical details
        technical = re.findall(r'(?:technical|specification|requirement)[^.!?]*[.!?]', content, re.IGNORECASE)
        if technical:
            sections["technical_details"] = " ".join(technical[:2])
            
        return dict(sections)

    def process_website(self, url, valves):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.8",
            }
            
            if valves.ignored_websites:
                base_url = self.get_base_url(url)
                if any(ignored_site.strip() in base_url 
                      for ignored_site in valves.ignored_websites.split(",")):
                    return None

            response = requests.get(url, headers=headers, timeout=valves.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Get title and description
            title = soup.title.string if soup.title else "No title found"
            title = self.remove_emojis(title.strip())
            
            # Try to get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else ""
            
            # Get main content
            content = self.format_text(soup.get_text())
            content = self.truncate_to_n_words(content, valves.page_content_words_limit)
            
            # Process content
            main_points = self.extract_main_points(content)
            categories = self.categorize_content(content)
            
            return {
                "title": title,
                "url": url,
                "description": description,
                "main_points": main_points,
                "categories": categories,
                "content": content,
                "excerpt": self.generate_excerpt(content)
            }
            
        except Exception as e:
            return None

class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter({
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                }
            })

class Tools:
    class Valves(BaseModel):
        max_results: int = Field(5, description="Maximum number of search results to return")
        page_content_words_limit: int = Field(5000, description="Limit words content for each page")
        timeout: int = Field(20, description="Timeout for HTTP requests in seconds")
        ignored_websites: str = Field("", description="Comma-separated list of websites to ignore")
        citation_links: bool = Field(True, description="If True, send custom citations with links")
        max_concurrent_requests: int = Field(3, description="Maximum number of concurrent website requests")
        summarize_content: bool = Field(True, description="Whether to summarize and categorize content")
        max_main_points: int = Field(5, description="Maximum number of main points to extract per page")

    def __init__(self):
        self.valves = self.Valves()
        self.functions = HelpFunctions()

    async def search_brave(self, query: str, __event_emitter__=None) -> str:
        """
        Search the web using Brave and get the content of the relevant pages. Search for unknown knowledge, news, info, public contact info, weather, etc.
        :params query: Web Query used in search engine.
        :return: The content of the pages in json format.
        """
        emitter = EventEmitter(__event_emitter__)
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.8',
            'Sec-CH-UA': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        url = f'https://search.brave.com/search?q={query}&source=desktop'
        
        try:
            await emitter.emit(f"Initiating Brave search for: {query}")
            
            response = requests.get(url, headers=headers, timeout=self.valves.timeout)
            response.raise_for_status()
            
            await emitter.emit("Parsing search results")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='snippet')
            
            website_urls = []
            for result in results[:self.valves.max_results]:
                if not result.get_text().strip():
                    continue
                    
                url_elem = result.find_previous('a', href=True)
                if url_elem and url_elem['href']:
                    website_urls.append(url_elem['href'])

            await emitter.emit(f"Found {len(website_urls)} websites to process")

            # Process websites in parallel
            processed_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.valves.max_concurrent_requests) as executor:
                futures = [
                    executor.submit(
                        self.functions.process_website, 
                        url, 
                        self.valves
                    ) for url in website_urls
                ]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        processed_results.append(result)
                        
                        if self.valves.citation_links and __event_emitter__:
                            await __event_emitter__({
                                "type": "citation",
                                "data": {
                                    "document": [result["content"]],
                                    "metadata": [{
                                        "date_accessed": datetime.now().isoformat(),
                                        "source": result["url"]
                                    }],
                                    "source": {
                                        "name": result["title"],
                                        "url": result["url"]
                                    }
                                }
                            })
            
            # Format final output
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_results": len(processed_results),
                "results": processed_results
            }
            
            await emitter.emit(
                status="complete",
                description=f"Search completed successfully - Processed {len(processed_results)} websites",
                done=True
            )
            
            return json.dumps(formatted_results, ensure_ascii=False, indent=2)

        except Exception as e:
            error_msg = f"Error performing search: {str(e)}"
            await emitter.emit(
                status="error",
                description=error_msg,
                done=True
            )
            return json.dumps({"error": error_msg}, indent=2)