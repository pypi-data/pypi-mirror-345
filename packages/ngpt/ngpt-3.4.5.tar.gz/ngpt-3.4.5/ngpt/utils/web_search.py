"""
Web search utilities for nGPT using duckduckgo-search and trafilatura.

This module provides functionality to search the web and extract
information from search results to enhance AI prompts.
"""

import re
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import requests
import sys
import datetime

# Get actual logger from global context instead of using standard logging
from . import log

# Use a global variable to store the logger provided during runtime
_logger = None

def set_logger(logger):
    """Set the logger to use for this module."""
    global _logger
    _logger = logger

def get_logger():
    """Get the current logger or use a default."""
    if _logger is not None:
        return _logger
    else:
        # Default logging to stderr if no logger provided, but only for errors
        class DefaultLogger:
            def info(self, msg): pass  # Suppress INFO messages
            def error(self, msg): print(f"ERROR: {msg}", file=sys.stderr)
            def warning(self, msg): pass  # Suppress WARNING messages
            def debug(self, msg): pass
        return DefaultLogger()

def perform_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo and return relevant results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results (title, url, snippet)
    """
    logger = get_logger()
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        logger.error(f"Error performing web search: {str(e)}")
        logger.info("Web search encountered an issue, but will continue with available results")
        return []

def extract_article_content(url: str, max_chars: int = 2000) -> Optional[str]:
    """
    Extract and clean content from a webpage URL.
    
    Args:
        url: The URL to extract content from
        max_chars: Maximum number of characters to extract
        
    Returns:
        Cleaned article text or None if extraction failed
    """
    logger = get_logger()
    try:
        # Skip non-http URLs or suspicious domains
        parsed_url = urlparse(url)
        if not parsed_url.scheme.startswith('http'):
            return None
        
        # Browser-like user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info(f"Fetching content from {url}")
        
        try:
            # Try using trafilatura
            import trafilatura
            
            # Download with correct parameters
            # trafilatura handles user-agent internally
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                # Extract main content
                content = trafilatura.extract(downloaded, include_comments=False, 
                                             include_tables=False, 
                                             no_fallback=False)
                
                if content:
                    # Clean up content if needed
                    content = content.strip()
                    
                    # Truncate if needed
                    if len(content) > max_chars:
                        content = content[:max_chars] + "..."
                        
                    return content
            
            # If trafilatura failed, try direct requests
            logger.info(f"Trafilatura extraction failed for {url}, trying fallback method")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Very basic HTML cleaning
                html_content = response.text
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', ' ', html_content)
                # Remove excess whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                if text:
                    if len(text) > max_chars:
                        text = text[:max_chars] + "..."
                    return text
                
            else:
                logger.error(f"Request to {url} returned status code {response.status_code}")
                
        except ImportError:
            logger.error("Trafilatura not installed. Install with 'pip install trafilatura'")
            # Try direct requests only
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Very basic HTML cleaning
                    html_content = response.text
                    text = re.sub(r'<[^>]+>', ' ', html_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        return text
            except Exception as req_error:
                logger.error(f"Direct request fallback failed: {str(req_error)}")
                
        except Exception as e:
            logger.error(f"Error extracting content with trafilatura: {str(e)}")
            # Try the requests fallback
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    html_content = response.text
                    text = re.sub(r'<[^>]+>', ' ', html_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        return text
            except Exception as req_error:
                logger.error(f"Direct request fallback failed: {str(req_error)}")
            
        return None
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return None

def get_web_search_results(query: str, max_results: int = 3, max_chars_per_result: int = 2000) -> Dict[str, Any]:
    """
    Get formatted web search results ready to be included in AI prompts.
    
    Args:
        query: The search query
        max_results: Maximum number of results to include
        max_chars_per_result: Maximum characters to include per result
        
    Returns:
        Dictionary containing search results and metadata
    """
    logger = get_logger()
    search_results = perform_web_search(query, max_results)
    enhanced_results = []
    success_count = 0
    failure_count = 0
    
    for result in search_results:
        content = extract_article_content(result['href'], max_chars_per_result)
        
        enhanced_results.append({
            'title': result.get('title', ''),
            'url': result.get('href', ''),
            'snippet': result.get('body', ''),
            'content': content if content else result.get('body', '')
        })
        
        if content:
            success_count += 1
        else:
            failure_count += 1
    
    # Log a user-friendly summary
    if search_results:
        if failure_count > 0:
            logger.info(f"Retrieved content from {success_count} out of {len(search_results)} sources")
        else:
            logger.info(f"Successfully retrieved content from all {success_count} sources")
    else:
        logger.error("No search results were found")
    
    # Add current timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    return {
        'query': query,
        'timestamp': current_time,
        'results': enhanced_results
    }

def format_web_search_results_for_prompt(search_results: Dict[str, Any]) -> str:
    """
    Format web search results into a string to include in AI prompts.
    
    Args:
        search_results: Dictionary of search results from get_web_search_results()
        
    Returns:
        Formatted string to include in prompts
    """
    query = search_results['query']
    results = search_results['results']
    timestamp = search_results['timestamp']
    
    formatted_text = f"[Web Search Results for: {query} (searched at {timestamp})]\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_text += f"RESULT {i}: {result['title']}\n"
        formatted_text += f"URL: {result['url']}\n"
        formatted_text += f"CONTENT:\n{result['content']}\n\n"
    
    formatted_text += f"[End of Web Search Results]\n\n"
    formatted_text += "Use the above web search information to help answer the user's question. When using this information:\n"
    formatted_text += "1. Use numbered citations in square brackets [1], [2], etc. when presenting information from search results\n"
    formatted_text += "2. Include a numbered reference list at the end of your response with the source URLs\n"
    formatted_text += "3. Format citations like 'According to [1]...' or 'Research indicates [2]...' or add citations at the end of sentences or paragraphs\n"
    formatted_text += "4. If search results contain conflicting information, acknowledge the differences and explain them with citations\n"
    formatted_text += "5. If the search results don't provide sufficient information, acknowledge the limitations\n"
    formatted_text += "6. Balance information from multiple sources when appropriate\n"
    formatted_text += "7. YOU MUST include an empty blockquote line ('>') between each reference in the reference list\n"
    formatted_text += "8. YOU MUST include ALL available references (between 2-7 sources) in your reference list\n\n"
    formatted_text += "Example citation format in text:\n"
    formatted_text += "Today is Thursday [1] and it's expected to rain tomorrow [2].\n\n"
    formatted_text += "Example reference format (YOU MUST FOLLOW THIS EXACT FORMAT WITH EMPTY LINES BETWEEN REFERENCES):\n"
    formatted_text += "> [1] https://example.com/date\n"
    formatted_text += ">\n"
    formatted_text += "> [2] https://weather.com/forecast\n"
    formatted_text += ">\n"
    formatted_text += "> [3] https://www.timeanddate.com\n\n"
    
    return formatted_text

def enhance_prompt_with_web_search(prompt: str, max_results: int = 5, logger=None, disable_citations: bool = False) -> str:
    """
    Enhance a prompt with web search results.
    
    Args:
        prompt: The original user prompt
        max_results: Maximum number of search results to include
        logger: Optional logger to use
        disable_citations: If True, disables citation instructions (used for code and shell modes)
        
    Returns:
        Enhanced prompt with web search results prepended
    """
    # Set the logger for this module
    if logger is not None:
        set_logger(logger)
        
    logger = get_logger()
    search_results = get_web_search_results(prompt, max_results)
    
    if disable_citations:
        # Modified version without citation instructions for code/shell modes
        query = search_results['query']
        results = search_results['results']
        timestamp = search_results['timestamp']
        
        formatted_text = f"[Web Search Results for: {query} (searched at {timestamp})]\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_text += f"RESULT {i}: {result['title']}\n"
            formatted_text += f"URL: {result['url']}\n"
            formatted_text += f"CONTENT:\n{result['content']}\n\n"
        
        formatted_text += f"[End of Web Search Results]\n\n"
        formatted_text += "Use the above web search information to help you, but do not include citations or references in your response.\n\n"
    else:
        # Standard version with citation instructions
        formatted_text = format_web_search_results_for_prompt(search_results)
    
    # Combine results with original prompt
    enhanced_prompt = formatted_text + prompt
    
    logger.info("Enhanced input with web search results")
    return enhanced_prompt 