#!/usr/bin/env python3
"""
OpenRouter Integration Logic

This module handles integration with OpenRouter.ai for AI-powered tweet analysis,
providing cloud-based AI models for better scalability and deployment compatibility.
"""

# Standard library imports
import ast
import json
import os
import re
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


def generate_with_openrouter(
    model: str, 
    prompt: str, 
    api_key: str = None,
    site_url: str = "https://crypto-scraper.com",
    site_name: str = "Crypto Tweet Analyzer"
) -> str:
    """
    Call OpenRouter API with a prompt and return the response.
    
    Args:
        model: OpenRouter model name (e.g., "mistralai/mistral-small-3.2-24b-instruct:free")
        prompt: Text prompt to send to the model
        api_key: OpenRouter API key (if not provided, will get from env)
        site_url: Optional site URL for rankings
        site_name: Optional site name for rankings
    
    Returns:
        Generated response text from the model
    """
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=120
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the response content
        if "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            return content
        else:
            return ""
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenRouter API request failed: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to decode OpenRouter response: {e}")


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


def generate_with_openrouter_tools(
    model: str, 
    prompt: str, 
    tools: List[Dict[str, Any]] = None,
    api_key: str = None
) -> str:
    """
    Call OpenRouter API with tools support (simulated with prompt engineering).
    
    Note: OpenRouter uses prompt engineering for tool-like functionality,
    providing flexibility for various analysis tasks.
    """
    if tools is None:
        tools = get_available_tools()

    # Add tool information to the prompt
    tools_description = "\n\nAvailable tools:\n"
    for tool in tools:
        func_info = tool.get("function", {})
        tools_description += f"- {func_info.get('name')}: {func_info.get('description')}\n"
    
    enhanced_prompt = prompt + tools_description + "\n\nYOU MUST USE A TOOL FOR EACH POST YOU WILL SEE. If you identify cryptocurrency tickers, list them clearly."
    
    # First call to get the model's response
    response = generate_with_openrouter(model, enhanced_prompt, api_key)
    
    # Simple tool detection - look for ticker patterns in response
    # This provides flexible analysis capabilities
    ticker_pattern = r'\b[A-Z]{2,5}\b'  # Simple pattern for crypto tickers
    potential_tickers = re.findall(ticker_pattern, response)
    
    # Filter common crypto tickers
    crypto_tickers = [t for t in potential_tickers if t in [
        'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'AVAX', 'MATIC', 'LINK', 'UNI', 'AAVE',
        'ATOM', 'ALGO', 'VET', 'XRP', 'LTC', 'BCH', 'ETC', 'XLM', 'TRX', 'EOS'
    ]]
    
    if crypto_tickers:
        print(f"🔧 Tool simulation: detected tickers {crypto_tickers}")
        
        # Execute tool simulation
        tool_result = execute_tool("extract_crypto_tickers", {"text": " ".join(crypto_tickers)})
        
        # Make a second call with the tool result
        follow_up_prompt = f"{enhanced_prompt}\n\nTool call result for extract_crypto_tickers: {tool_result}\n\nBased on this result, provide your final answer:"
        
        return generate_with_openrouter(model, follow_up_prompt, api_key)
    
    return response


def process_tweets_with_openrouter(
    user_or_handle: str, 
    limit: int, 
    model: str, 
    system_instruction: str | None = None, 
    mock: bool = True, 
    use_tools: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch tweets and process each with an OpenRouter model.
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
            prompt_parts.append("\nAnalyze this post and extract cryptocurrency sentiment analysis. Return ONLY a Python list with this exact format: [{'ticker': 'BTC', 'sentiment': 'bullish', 'context': 'mentions adoption and price target'}]. \n\nIMPORTANT: \n- For 'ticker' field: extract ONLY the base cryptocurrency symbol (e.g., 'BTC' not 'BTC/USD', 'ETH' not 'ETH/USDT')\n- For 'sentiment': use 'bullish' (positive/optimistic), 'bearish' (negative/pessimistic), or 'neutral' (no clear direction)\n- For 'context': brief description of why this sentiment was detected (max 10 words)\n\nExtract sentiment for ALL cryptocurrencies mentioned in the post. If no crypto sentiment is detected, return []. Do not add explanations, just the list.")

        prompt = "\n\n".join(prompt_parts)

        try:
            if use_tools:
                analysis = generate_with_openrouter_tools(model=model, prompt=prompt)
            else:
                # Mode sans tools : récupérer la réponse et extraire la liste finale
                raw_response = generate_with_openrouter(model=model, prompt=prompt)
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
                                            context = item.get('context', '')
                                            
                                            print(f"   📊 {ticker}: {sentiment}")
                                            if context:
                                                print(f"      💬 Context: {context}")
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
            analysis = f"<openrouter_error: {e}>"

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
            "total_sentiments": 0,
            "bullish_sentiments": 0,
            "bearish_sentiments": 0,
            "neutral_sentiments": 0
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
                    # Accepter tous les sentiments : bullish, bearish, neutral
                    if sentiment in ["bullish", "bearish", "neutral"]:
                        ticker = crypto.get("ticker", "")
                        context = crypto.get("context", "")
                        
                        crypto_entry = {
                            "tweet_number": i,
                            "timestamp": result.get("created_at", ""),
                            "ticker": ticker,
                            "sentiment": sentiment,
                            "context": context
                        }
                        consolidated_analysis["tweets_analysis"].append(crypto_entry)
                        
                        consolidated_analysis["analysis_summary"]["total_sentiments"] += 1
                        if sentiment == "bullish":
                            consolidated_analysis["analysis_summary"]["bullish_sentiments"] += 1
                        elif sentiment == "bearish":
                            consolidated_analysis["analysis_summary"]["bearish_sentiments"] += 1
                        elif sentiment == "neutral":
                            consolidated_analysis["analysis_summary"]["neutral_sentiments"] += 1
    
    # Ajouter le dictionnaire consolidé au dernier résultat
    if results:
        results.append({
            "consolidated_analysis": consolidated_analysis
        })

    return results
