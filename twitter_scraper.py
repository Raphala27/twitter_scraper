from playwright.sync_api import sync_playwright
import json
import argparse  # Import the argparse module


def scrape_tweet(url: str, as_json_string: bool = False) -> str:
    """
    Scrape a single tweet page. By default, returns the plain text of the tweet.
    If as_json_string=True, returns the full scraped data as a JSON string.

    Args:
        url (str): The URL of the tweet to scrape.
        as_json_string (bool): If True, returns the scraped data as a JSON string.
                               If False (default), returns only the plain text of the tweet.

    Returns:
        str: The plain text of the tweet, or a JSON string if as_json_string is True.
    """
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.on("response", intercept_response)
        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")

        tweet_text = ""
        visible_tweet_data = {}  # Still needed to construct JSON if requested

        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]

        for xhr in tweet_calls:
            try:
                data = xhr.json()
                raw_tweet = data.get('data', {}).get('tweetResult', {}).get('result', {})
                if not raw_tweet:
                    continue

                legacy_tweet = raw_tweet.get('legacy', {})
                tweet_text = legacy_tweet.get('full_text', "")

                # Only construct the full JSON data if it's actually requested
                if as_json_string:
                    user_result = raw_tweet.get('core', {}).get('user_results', {}).get('result', {})
                    user_legacy = user_result.get('legacy', {})
                    user_core = user_result.get('core', {})

                    visible_tweet_data['user'] = {
                        'name': user_core.get('name'),
                        'username': user_core.get('screen_name'),
                        'profile_image_url': user_core.get('avatar', {}).get('image_url'),
                        'is_verified': user_result.get('is_blue_verified', False),
                    }

                    visible_tweet_data['tweet'] = {
                        'text': tweet_text,
                        'post_date': legacy_tweet.get('created_at'),
                        'replies': legacy_tweet.get('reply_count', 0),
                        'reposts': legacy_tweet.get('retweet_count', 0),
                        'likes': legacy_tweet.get('favorite_count', 0),
                        'views': raw_tweet.get('views', {}).get('count', 'N/A'),
                    }

                    media_urls = []
                    extended_entities = legacy_tweet.get('extended_entities', {})
                    if 'media' in extended_entities:
                        for media_item in extended_entities['media']:
                            if media_item.get('type') in ['photo', 'video', 'animated_gif']:
                                media_urls.append(media_item.get('media_url_https'))
                    visible_tweet_data['tweet']['media_urls'] = media_urls

                    link_previews = []
                    card = raw_tweet.get('card', {}).get('legacy', {}).get('binding_values', [])
                    for item in card:
                        if item.get('key') == 'unified_card.destination_url' or item.get('key') == 'card_url':
                            link_previews.append(item.get('value', {}).get('string_value'))

                    for url_item in legacy_tweet.get('entities', {}).get('urls', []):
                        link_previews.append(url_item.get('expanded_url'))

                    visible_tweet_data['tweet']['external_links'] = list(set([link for link in link_previews if link]))

                # Return immediately after finding the main tweet data
                if as_json_string:
                    return json.dumps(visible_tweet_data, indent=4)
                else:
                    return tweet_text

            except json.JSONDecodeError:
                print(f"Could not decode JSON from XHR call: {xhr.url}")
            except Exception as e:
                print(f"An error occurred during data extraction: {e}")

        browser.close()

        # If no data is found after checking all calls
        if as_json_string:
            return json.dumps({})
        else:
            return ""


if __name__ == "__main__":
    # --- Command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Scrape a single tweet.")
    parser.add_argument(
        "tweet_url",
        type=str,
        help="The URL of the tweet to scrape (e.g., https://x.com/user/status/123...)"
    )
    parser.add_argument(
        "--json",
        action="store_true",  # This makes it a flag; if present, it's True
        help="Output the scraped data as a JSON string instead of plain text."
    )
    args = parser.parse_args()

    # --- Use the parsed arguments ---
    tweet_url = args.tweet_url

    # Call scrape_tweet based on whether --json was provided
    if args.json:
        # print("--- JSON String Output (as_json_string=True) ---") # Removed this line as requested
        output_data = scrape_tweet(tweet_url, as_json_string=True)
        print(output_data)
    else:
        # print("--- Plain Text Output (Default) ---") # Removed this line as requested
        output_data = scrape_tweet(tweet_url)
        print(output_data)