import ast
import json
import subprocess
import requests
import sys
import os
from typing import List, Dict, Any

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_scraper import UtilsScraper as us
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import Tools

def ensure_model_present(model: str) -> None:
    """Pull the Ollama model if not present locally."""
    try:
        # 'ollama show' returns non-zero if model not present
        show = subprocess.run(["ollama", "show", model], capture_output=True)
        if show.returncode != 0:
            pull = subprocess.run(["ollama", "pull", model], check=False)
            if pull.returncode != 0:
                print(f"Warn: unable to pull model '{model}'. Ensure Ollama is running and the model name is correct.")
    except FileNotFoundError:
        print("Warn: 'ollama' CLI not found. Assuming Ollama API is reachable at http://localhost:11434.")

def generate_with_ollama(model: str, prompt: str, url: str = "http://localhost:11434/api/generate") -> str:
    """Call Ollama generate API with a simple prompt and return the full response text."""
    payload = {"model": model, "prompt": prompt, "stream": False, "think": False}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # standard response has key 'response'
    return data.get("response", "")


def get_available_tools() -> List[Dict[str, Any]]:
    """Returns the list of available tools that can be used by the model."""
    return [
        {
            "type": "function",
            "function": {
                "name": "extract_crypto_tickers",
                "description": "Get from a list of ticker a list of unique tickers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tickers_list": {
                            "type": "list",
                            "description": "List of cryptocurrency tickers only found in the text, e.g., ['BTC', 'ETH']"
                        }
                    },
                    "required": ["tickers_list"]
                }
            }
        }
    ]


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool function and return the result."""
    if tool_name == "extract_crypto_tickers":
        text = parameters.get("text", "")
        result = Tools.extract_unique_tickers(text)
        return json.dumps(result)
    else:
        return f"Unknown tool: {tool_name}"


def generate_with_ollama_tools(model: str, prompt: str, tools: List[Dict[str, Any]] = None, url: str = "http://localhost:11434/api/generate") -> str:
    """Call Ollama generate API with tools support and handle tool calls."""
    if tools is None:
        tools = get_available_tools()

    prompt = prompt + "YOU MUST USE A TOOL FOR EACH POST YOU WILL SEE."

    
    # First call to get the model's response
    payload = {"model": model, "prompt": prompt, "stream": False, "tools": tools}
    headers = {"Content-Type": "application/json"}
    # print("Payload:", payload)
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    data = resp.json()
    
    # # Afficher la réponse brute complète d'Ollama
    # print("🔍 RÉPONSE BRUTE OLLAMA:")
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    # print("=" * 50)
    
    response = data.get("response", "")
    
    # Check if the response contains tool calls (Ollama format)
    message = data.get("message", {})
    tool_calls = message.get("tool_calls", [])
    
    if tool_calls:
        # Process the first tool call
        tool_call = tool_calls[0]
        function_info = tool_call.get("function", {})
        tool_name = function_info.get("name")
        tool_arguments = function_info.get("arguments", {})
        
        if tool_name:
            print(f"🔧 Tool détecté: {tool_name} avec arguments: {tool_arguments}")
            
            # Execute the tool
            tool_result = execute_tool(tool_name, tool_arguments)
            
            # Make a second call with the tool result
            follow_up_prompt = f"{prompt}\n\nTool call result for {tool_name}: {tool_result}\n\nBased on this result, provide your final answer:"
            
            payload = {"model": model, "prompt": follow_up_prompt, "stream": False, "tools": tools}
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
    
    return response

def process_tweets_with_ollama(user_or_handle: str, limit: int, model: str, system_instruction: str | None = None, mock: bool = True, use_tools: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch tweets and process each with an Ollama model.
    Returns a list of { created_at, id_str, full_text, analysis }.
    """
    # get_user_tweets returns either pretty-printed JSON (when as_json=True) or text; we need JSON
    raw = us.get_user_tweets(user_or_handle, limit=limit, as_json=True, mock=mock)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: wrap raw text as one pseudo tweet
        data = {"tweets": [{"full_text": raw}]}

    tweets = data.get("tweets", [])
    ensure_model_present(model)

    results: List[Dict[str, Any]] = []
    for idx, tw in enumerate(tweets, start=1):
        text = tw.get("full_text", "").strip()
        created = tw.get("created_at", "")
        tid = tw.get("id_str", "")
        if not text:
            continue

        prompt_parts = []
        if system_instruction:
            prompt_parts.append(system_instruction.strip())
        prompt_parts.append("Post:\n" + text)
        
        if use_tools:
            prompt_parts.append("\nAnalyze this post and extract any cryptocurrency tickers mentioned. Use the extract_crypto_tickers tool if you find any crypto-related content.")
        else:
            prompt_parts.append("\nRecover the crypto and tickers. Give me back only a list in python format. Only like following: ['BTC', 'ETH'] but do not add them if they are not present in the post. Do not give any other explanation, do not write sentences, do not show your thinking process. Be very precise and don't forget a crypto ticker in the post. Final answer must be only the list.")

        prompt = "\n\n".join(prompt_parts)

        try:
            if use_tools:
                analysis = generate_with_ollama_tools(model=model, prompt=prompt)
            else:
                # Mode sans tools : récupérer la réponse et extraire la liste finale
                raw_response = generate_with_ollama(model=model, prompt=prompt)
                
                try:
                    # Extraire toutes les listes de la réponse avec regex
                    import re
                    list_pattern = r'\[([^\[\]]*)\]'
                    matches = re.findall(list_pattern, raw_response)
                    
                    if matches:
                        # Prendre la dernière liste trouvée (réponse finale)
                        last_list_content = matches[-1]
                        
                        # Parser la liste
                        if last_list_content.strip():
                            # Séparer par virgule et nettoyer chaque élément
                            items = [item.strip().strip("'\"") for item in last_list_content.split(',') if item.strip()]
                            tickers_list = [item for item in items if item]  # Supprimer les éléments vides
                        else:
                            tickers_list = []
                        
                        # Convertir les tickers en noms de cryptos
                        if tickers_list:
                            analysis = Tools.get_crypto_names_from_tickers(tickers_list)
                            print(f"💰 Cryptos trouvées: {tickers_list} → {analysis}")
                        else:
                            analysis = []
                            print("💰 Aucune crypto détectée dans ce tweet")
                    else:
                        print("⚠️  Format de réponse inattendu du modèle")
                        analysis = raw_response

                except Exception as e:
                    print(f"❌ Erreur lors du parsing de la liste : {e}")
                    analysis = raw_response
        except Exception as e:
            analysis = f"<ollama_error: {e}>"

        results.append({
            "created_at": created,
            "id_str": tid,
            "full_text": text,
            "analysis": analysis,
        })

    return results
