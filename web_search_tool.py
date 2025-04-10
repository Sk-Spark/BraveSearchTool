"""
title: Brave Web Search
author: Assistant
author_url: https://github.com
git_url: https://github.com/username/brave-web-search
description: A tool that performs web searches using Brave Search and returns the results
required_open_webui_version: 0.4.0
requirements: requests, beautifulsoup4
version: 0.1.0
licence: MIT
"""

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Optional, List

class Tools:
    def __init__(self):
        """Initialize the Tool."""
        self.valves = self.Valves()
        # Disable built-in citations as we'll handle them manually
        self.citation = False

    class Valves(BaseModel):
        max_results: int = Field(5, description="Maximum number of search results to return")

    async def search_brave(self, query: str, __event_emitter__=None) -> str:
        """
        Perform a web search using Brave Search and return the results.
        
        :param query: The search query string
        :return: The search results as a formatted string
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": "Searching Brave...",
                    "done": False,
                    "hidden": False
                }
            })

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
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": "Extracting search results...",
                        "done": False,
                        "hidden": False
                    }
                })

            # Parse and extract results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='snippet')
            extracted_text = []
            
            for result in results[:self.valves.max_results]:
                if result.get_text().strip():
                    extracted_text.append(result.get_text().strip())
            
            results_text = '\n\n'.join(extracted_text)

            # Emit citation for the search
            if __event_emitter__:
                await __event_emitter__({
                    "type": "citation",
                    "data": {
                        "document": [results_text],
                        "metadata": [{
                            "date_accessed": None,  # Will be filled by OpenWebUI
                            "source": "Brave Search",
                        }],
                        "source": {
                            "name": "Brave Search",
                            "url": url
                        }
                    }
                })

                # Final status update
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": "Search completed",
                        "done": True,
                        "hidden": False
                    }
                })

            return results_text

        except Exception as e:
            error_msg = f"Error performing search: {str(e)}"
            if __event_emitter__:
                await __event_emitter__({
                    "type": "message",
                    "data": {"content": f"⚠️ {error_msg}"}
                })
            return error_msg