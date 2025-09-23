#!/usr/bin/env python3
"""
Ollama Integration Logic

This module handles integration with Ollama for AI-powered tweet analysis,
including model management, prompt generation, and tool usage for cryptocurrency
ticker extraction and sentiment analysis.
"""

# Standard library imports
import ast
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List

# Third-party imports
import requests

# Local application imports
try:
    # Try relative imports first (when used as package)
    from .tools import Tools
    from ..utils_scraper import UtilsScraper as us
except ImportError:
    # Fallback to absolute imports (when run directly)
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from tools import Tools
    from utils_scraper import UtilsScraper as us


def ensure_model_present(model: str) -> None:
    """
    Ensure the specified Ollama model is available locally.
    
    Args:
        model: Name of the Ollama model to check/pull
    """
    try:
        # Check if model exists with 'ollama show'
        show = subprocess.run(["ollama", "show", model], capture_output=True, timeout=30, check=False)
        if show.returncode != 0:
            print(f"Model '{model}' not found locally. Pulling...")
            pull = subprocess.run(["ollama", "pull", model], check=False, timeout=300)
            if pull.returncode != 0:
                print(f"Warning: Unable to pull model '{model}'. "
                      "Ensure Ollama is running and the model name is correct.")
    except FileNotFoundError:
        print("Warning: 'ollama' CLI not found. "
              "Assuming Ollama API is reachable at http://localhost:11434.")
    except subprocess.TimeoutExpired:
        print(f"Warning: Timeout while checking/pulling model '{model}'.")


def generate_with_ollama(
    model: str, 
    prompt: str, 
    url: str = "http://localhost:11434/api/generate"
) -> str:
    """
    Call Ollama generate API with a prompt and return the response.
    
    Args:
        model: Ollama model name
        prompt: Text prompt to send to the model
        url: Ollama API endpoint URL
    
    Returns:
        Generated response text from the model
    """
    payload = {
        "model": model, 
        "prompt": prompt, 
        "stream": False, 
        "think": False
    }
    headers = {"Content-Type": "application/json"}
    
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Get the list of available tools for the AI model.
    
    Returns:
        List of tool definitions for cryptocurrency analysis
    """
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
    """
    Execute a tool function and return the result.
    
    Args:
        tool_name: Name of the tool to execute
        parameters: Parameters to pass to the tool
    
    Returns:
        JSON string result from tool execution
    """
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
    for i, tw in enumerate(tweets, start=1):
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
            prompt_parts.append("\nAnalyze this post and extract cryptocurrency information. Return ONLY a Python list with this exact format: [{'ticker': 'BTC', 'sentiment': 'long', 'leverage': '10', 'take_profits': [50000, 52000, 55000], 'stop_loss': 45000, 'entry_price': 48000}]. \n\nIMPORTANT: For ticker field, extract ONLY the base cryptocurrency symbol (e.g., 'XRP' not 'XRP/USDT', 'BTC' not 'BTC/USD', 'ETH' not 'ETH/USDT'). Remove any trading pairs or suffixes.\n\nSentiment must be 'long', 'short', or 'neutral'. Leverage should be extracted as a number only (like '2', '10', '50') or 'none' if not specified. Extract all Take Profit targets as a list of numbers, Stop Loss as a single number, and Entry price as a single number. If any price is not found, use null. If no crypto found, return []. Do not add explanations, just the list.")

        prompt = "\n\n".join(prompt_parts)

        try:
            if use_tools:
                analysis = generate_with_ollama_tools(model=model, prompt=prompt)
            else:
                # Mode sans tools : récupérer la réponse et extraire la liste finale
                raw_response = generate_with_ollama(model=model, prompt=prompt)
                print("🔍 RÉPONSE BRUTE DU MODÈLE:")
                print(f"'{raw_response}'")
                print("─" * 60)
                
                try:
                    # Extract all lists from the response with improved regex
                    # This regex handles lists with nested objects
                    list_pattern = r'\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]'
                    matches = re.findall(list_pattern, raw_response, re.DOTALL)
                    
                    # Si pas de correspondance avec la regex complexe, essayer la simple
                    if not matches:
                        list_pattern = r'\[.*\]'
                        matches = re.findall(list_pattern, raw_response, re.DOTALL)
                    
                    if matches:
                        # Prendre la dernière liste trouvée (réponse finale)
                        last_list_str = matches[-1]
                        print(f"🔧 Liste extraite: {last_list_str}")
                        
                        try:
                            # Essayer d'abord avec json.loads, puis ast.literal_eval en fallback
                            try:
                                # Nettoyer la chaîne pour JSON
                                json_str = last_list_str.replace("'", '"')
                                parsed_data = json.loads(json_str)
                            except json.JSONDecodeError:
                                # Fallback vers ast.literal_eval
                                parsed_data = ast.literal_eval(last_list_str)
                            
                            if isinstance(parsed_data, list):
                                if parsed_data:
                                    # Format attendu : [{'ticker': 'BTC', 'sentiment': 'long'}]
                                    analysis = {
                                        'cryptos': parsed_data,
                                        'timestamp': created,
                                        'tweet_id': tid
                                    }
                                    print(f"💰 {len(parsed_data)} crypto(s) analysée(s):")
                                    for item in parsed_data:
                                        if isinstance(item, dict):
                                            ticker = item.get('ticker', 'N/A')
                                            sentiment = item.get('sentiment', 'neutral')
                                            leverage = item.get('leverage', 'none')
                                            take_profits = item.get('take_profits', [])
                                            stop_loss = item.get('stop_loss')
                                            entry_price = item.get('entry_price')
                                            
                                            print(f"   📊 {ticker}: {sentiment} (levier: {leverage})")
                                            if entry_price:
                                                print(f"      🎯 Entry: {entry_price}")
                                            if take_profits:
                                                tp_str = ", ".join([str(tp) for tp in take_profits])
                                                print(f"      📈 Take Profits: [{tp_str}]")
                                            if stop_loss:
                                                print(f"      ⛔ Stop Loss: {stop_loss}")
                                        else:
                                            print(f"   📊 {item}")
                                else:
                                    # Liste vide
                                    analysis = {
                                        'cryptos': [],
                                        'timestamp': created,
                                        'tweet_id': tid
                                    }
                                    print("💰 Aucune crypto détectée dans ce tweet")
                            else:
                                analysis = {
                                    'cryptos': [],
                                    'timestamp': created,
                                    'tweet_id': tid,
                                    'raw_response': raw_response
                                }
                                print("⚠️  Réponse non-liste du modèle")
                        except (ValueError, SyntaxError) as e:
                            print(f"⚠️  Erreur de parsing: {e}")
                            analysis = {
                                'cryptos': [],
                                'timestamp': created,
                                'tweet_id': tid,
                                'raw_response': raw_response
                            }
                    else:
                        print("⚠️  Aucune liste trouvée dans la réponse")
                        analysis = {
                            'cryptos': [],
                            'timestamp': created,
                            'tweet_id': tid,
                            'raw_response': raw_response
                        }

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

    # Créer un dictionnaire consolidé avec toutes les analyses
    consolidated_analysis = {
        "account": user_or_handle,
        "total_tweets": len(results),
        "analysis_summary": {
            "total_positions": 0,
            "long_positions": 0,
            "short_positions": 0
        },
        "tweets_analysis": []
    }
    
    for i, result in enumerate(results, 1):
        analysis = result.get("analysis", {})
        if isinstance(analysis, dict) and "cryptos" in analysis:
            cryptos = analysis.get("cryptos", [])
            # Filtrer uniquement les cryptos avec des positions définies (long/short)
            for crypto in cryptos:
                if isinstance(crypto, dict):
                    sentiment = crypto.get("sentiment", "neutral")
                    if sentiment in ["long", "short"]:  # Exclure "neutral"
                        ticker = crypto.get("ticker", "")
                        leverage = crypto.get("leverage", "none")
                        take_profits = crypto.get("take_profits", [])
                        stop_loss = crypto.get("stop_loss")
                        entry_price = crypto.get("entry_price")
                        
                        crypto_entry = {
                            "tweet_number": i,
                            "timestamp": result.get("created_at", ""),
                            "ticker": ticker,
                            "sentiment": sentiment,
                            "leverage": leverage,
                            "take_profits": take_profits if take_profits else [],
                            "stop_loss": stop_loss,
                            "entry_price": entry_price
                        }
                        consolidated_analysis["tweets_analysis"].append(crypto_entry)
                        
                        consolidated_analysis["analysis_summary"]["total_positions"] += 1
                        if sentiment == "long":
                            consolidated_analysis["analysis_summary"]["long_positions"] += 1
                        elif sentiment == "short":
                            consolidated_analysis["analysis_summary"]["short_positions"] += 1
    
    # Ajouter le dictionnaire consolidé au dernier résultat
    if results:
        results.append({
            "consolidated_analysis": consolidated_analysis
        })

    return results
