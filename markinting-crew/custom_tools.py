import os
import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from typing import Optional
import json

class CustomScrapeWebsiteTool(BaseTool):
    name: str = "Website Scraper"
    description: str = "Scrapes content from a website URL and returns the text content."

    def _run(self, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid token limits
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return f"Content from {url}:\n\n{text}"
            
        except requests.RequestException as e:
            return f"Error scraping website {url}: {str(e)}"
        except Exception as e:
            return f"Error processing website content: {str(e)}"

class CustomDirectoryReadTool(BaseTool):
    name: str = "Directory Reader"
    description: str = "Lists files and directories in a specified directory path. Usage: provide directory path as argument."

    def _run(self, path: str = ".") -> str:
        try:
            target_path = path
            
            if not os.path.exists(target_path):
                return f"Directory '{target_path}' does not exist."
            
            if not os.path.isdir(target_path):
                return f"'{target_path}' is not a directory."
            
            items = []
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    # Get file size
                    try:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({size} bytes)")
                    except:
                        items.append(f"📄 {item}")
            
            if not items:
                return f"Directory '{target_path}' is empty."
            
            return f"Contents of directory '{target_path}':\n" + "\n".join(sorted(items))
            
        except PermissionError:
            return f"Permission denied accessing directory '{target_path}'."
        except Exception as e:
            return f"Error reading directory: {str(e)}"

class CustomFileReadTool(BaseTool):
    name: str = "File Reader"
    description: str = "Reads the content of a text file and returns its contents."

    def _run(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return f"File '{file_path}' does not exist."
            
            if not os.path.isfile(file_path):
                return f"'{file_path}' is not a file."
            
            # Try to detect file encoding
            encodings = ['utf-8', 'utf-16', 'cp1252', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return f"Could not decode file '{file_path}' with supported encodings."
            
            # Limit content length to avoid token limits
            if len(content) > 8000:
                content = content[:8000] + "\n... (content truncated)"
            
            return f"Content of file '{file_path}':\n\n{content}"
            
        except PermissionError:
            return f"Permission denied reading file '{file_path}'."
        except Exception as e:
            return f"Error reading file: {str(e)}"

class CustomFileWriterTool(BaseTool):
    name: str = "File Writer"
    description: str = "Writes content to a file. Can create new files or overwrite existing ones."

    def _run(self, filename: str, content: str, overwrite: bool = True) -> str:
        try:
            # Check if file exists and handle overwrite logic
            if os.path.exists(filename) and not overwrite:
                return f"File '{filename}' already exists and overwrite is disabled."
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write content to file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            
            file_size = os.path.getsize(filename)
            return f"Successfully wrote {len(content)} characters ({file_size} bytes) to '{filename}'."
            
        except PermissionError:
            return f"Permission denied writing to file '{filename}'."
        except Exception as e:
            return f"Error writing to file: {str(e)}"

class CustomJSONFileWriterTool(BaseTool):
    name: str = "JSON File Writer"
    description: str = "Writes JSON data to a file with proper formatting."

    def _run(self, filename: str, data: dict, indent: int = 2) -> str:
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write JSON data to file
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            
            file_size = os.path.getsize(filename)
            return f"Successfully wrote JSON data to '{filename}' ({file_size} bytes)."
            
        except PermissionError:
            return f"Permission denied writing to file '{filename}'."
        except TypeError as e:
            return f"Error serializing data to JSON: {str(e)}"
        except Exception as e:
            return f"Error writing JSON file: {str(e)}"

class CustomDirectoryReadToolWithDefault(BaseTool):
    name: str = "Directory Reader with Default"
    description: str = "Lists files and directories in the 'resources/drafts' directory or a specified path."

    def _run(self, path: str = "resources/drafts") -> str:
        try:
            target_path = path
            
            if not os.path.exists(target_path):
                return f"Directory '{target_path}' does not exist."
            
            if not os.path.isdir(target_path):
                return f"'{target_path}' is not a directory."
            
            items = []
            for item in os.listdir(target_path):
                item_path = os.path.join(target_path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    # Get file size
                    try:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({size} bytes)")
                    except:
                        items.append(f"📄 {item}")
            
            if not items:
                return f"Directory '{target_path}' is empty."
            
            return f"Contents of directory '{target_path}':\n" + "\n".join(sorted(items))
            
        except PermissionError:
            return f"Permission denied accessing directory '{target_path}'."
        except Exception as e:
            return f"Error reading directory: {str(e)}"

# Enhanced DuckDuckGo tool with better formatting
class EnhancedDDGTool(BaseTool):
    name: str = "Enhanced DuckDuckGo Search"
    description: str = "Performs web search using DuckDuckGo with detailed results including snippets."

    def _run(self, query: str, max_results: int = 5) -> str:
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddg:
                results = ddg.text(query, max_results=max_results)
                
                if not results:
                    return f"No results found for query: '{query}'"
                
                formatted_results = [f"Search results for: '{query}'\n"]
                
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    url = result.get('href', 'No URL')
                    snippet = result.get('body', 'No description')
                    
                    formatted_results.append(f"{i}. **{title}**")
                    formatted_results.append(f"   URL: {url}")
                    formatted_results.append(f"   Summary: {snippet[:200]}...")
                    formatted_results.append("")
                
                return "\n".join(formatted_results)
                
        except ImportError:
            return "DuckDuckGo search library not available. Please install: pip install duckduckgo-search"
        except Exception as e:
            return f"Error performing search: {str(e)}"