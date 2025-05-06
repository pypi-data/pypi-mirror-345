import click
import requests
import json
import os
from pathlib import Path

class BitfyTool:
    def __init__(self):
        self.api_key = None
        self._initialize_api_key()
        self.use_bitfy()  # Call the intro message

    def _initialize_api_key(self):
        """Initialize API key from env or config file"""
        self.api_key = os.getenv("BITFY_API_KEY") or self._load_api_key_from_config()
        if not self.api_key:
            self._setup_api_key()

    def _setup_api_key(self):
        """Prompt user for API key and store it"""
        print("API key not found. Let's set it up once.")
        api_key = input("Enter your Gemini API key: ").strip()
        
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        # Store in environment variables (for current session)
        os.environ["BITFY_API_KEY"] = api_key
        
        # Store in config file for persistence
        config_path = Path.home() / ".bitfy_config"
        with open(config_path, "w") as f:
            json.dump({"api_key": api_key}, f)
        
        self.api_key = api_key
        print("API key stored successfully!")

    def _load_api_key_from_config(self):
        """Load API key from config file"""
        config_path = Path.home() / ".bitfy_config"
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("api_key")
        except json.JSONDecodeError:
            print("⚠️ Config file corrupted. Please enter API key again.")
            os.remove(config_path)  # Remove corrupted config
        return None

    def use_bitfy(self):
        print("Hi, I'm Bitfy! 🦋")

    def ask_gemini(self, prompt):
        if not self.api_key:
            raise ValueError("API key not set")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }   

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    def giving_help(self):
        print("Here's some help:")
        print("--bitfy: Show Bitfy intro")
        print("--ask 'question': Ask Gemini a question")
        print("--help: Show help")
        print("--explain 'filepath' 'prompt': Explain a file")
        print("--write 'directory' 'filename' 'prompt': Write to a file")
    
    def explain_this(self, filepath=None, prompt="explain this"):
        if not filepath:
            print("Please provide a file path")
            return
        
        try:
            with open(filepath, "r") as f:
                content = f.read()
            explanation = self.ask_gemini(f"{prompt}: {content}")
            print(explanation)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def write(self, directory=None, filename=None, prompt="write code about calculator"):
        if not directory or not filename:
            print("Please provide both directory and filename")
            return
        
        try:
            # Use pathlib for safe path joining
            filepath = Path(directory) / filename
            content = self.ask_gemini(prompt)
            with open(filepath, "w") as f:
                f.write(content)
            print(f"File written successfully to {filepath}")
        except Exception as e:
            print(f"Error writing file: {str(e)}")

@click.command()
@click.option("--bitfy", is_flag=True, help="Show Bitfy intro")
@click.option("--ask", help="Ask Gemini a question")
@click.option("--help", is_flag=True, help="Show help")
@click.option("--explain", nargs=2, type=str, help="Explain a file (provide filepath and prompt)")
@click.option("--write", nargs=3, type=str, help="Write to a file (provide directory, filename and prompt)")
def main(bitfy, ask, help, explain, write):
    """Bitfy CLI - AI Assistant"""
    tool = BitfyTool()
    
    if bitfy:
        pass  # Already shown in init
    elif ask:
        response = tool.ask_gemini(ask)
        click.echo(f"🦋 Gemini says:\n{response}")
    elif help:
        tool.giving_help()  
    elif explain:
        filepath, prompt = explain
        tool.explain_this(filepath, prompt)
    elif write:
        directory, filename, prompt = write
        tool.write(directory, filename, prompt)
    else:
        tool.giving_help()

if __name__ == "__main__":
    main()