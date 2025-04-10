# Brave Web Search Tool

A Python-based tool that performs web searches using Brave Search and returns summarized results. This tool is designed to integrate with OpenWebUI and provides a user-friendly interface for querying the web.

## Features

- Perform web searches using Brave Search.
- Summarize search results for easy consumption.
- Configurable maximum number of search results.
- Emits status updates and citations for OpenWebUI integration.

## Requirements

The project requires the following Python packages, as specified in [requirements.txt](requirements.txt):

- `requests>=2.31.0`
- `beautifulsoup4>=4.12.2`
- `transformers==4.36.0`
- `torch==2.2.0`
- `argparse==1.4.0`
- `pydantic>=2.0.0`
- `aiohttp>=3.9.0`

Install the dependencies using:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone the repository and navigate to the project directory.
2. Run the tool by integrating it with OpenWebUI or directly invoking the `search_brave` method in [`web_search_tool.py`](web_search_tool.py).

## File Descriptions

- **`web_search_tool.py`**: Contains the main implementation of the Brave Web Search tool.
- **`requirements.txt`**: Lists the required Python dependencies.
- **`request.http`**: Example HTTP request for Brave Search.
- **`curl.txt`**: Example cURL command for Brave Search.
- **`promts.txt`**: Instructions for creating the tool.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.