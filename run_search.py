import asyncio
from exampleTool import Tools

async def main():
    tools = Tools()
    
    # Test web search
    print("\nTesting web search:")
    print("-" * 50)
    search_result = await tools.search_web("what is todays weather in Lucknow, UP, India")
    print("Web Search Results:")
    print(search_result)
    
    # # Test website scraping
    # print("\nTesting specific website scraping:")
    # print("-" * 50)
    # website_result = await tools.get_website("https://www.python.org")
    # print("Website Scraping Results:")
    # print(website_result)

if __name__ == "__main__":
    asyncio.run(main())