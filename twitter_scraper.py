from playwright.sync_api import sync_playwright
import json
import argparse
import time


def scrape_user_timeline(url: str, as_json_string: bool = False) -> str:
    """
    Scrape a user's profile and their recent tweets. By default, returns the user's name and tweet texts.
    If as_json_string=True, returns the full scraped data as a JSON string.
    Args:
        url (str): The URL of the user's profile to scrape.
        as_json_string (bool): If True, returns the scraped data as a JSON string.
                               If False (default), returns the user's name and tweet texts.
    Returns:
        str: The user's name and tweet texts, or a JSON string if as_json_string is True.
    """
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
        )
        page = context.new_page()
        page.on("response", intercept_response)

        # Navigate to the profile page with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to load the page...")
                # Use a shorter timeout and less strict condition
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Exiting.")
                    browser.close()
                    if as_json_string:
                        return json.dumps({"error": "Failed to load the page after multiple attempts"})
                    else:
                        return "Failed to load the page after multiple attempts"
                time.sleep(2)  # Wait before retrying

        # Wait for the profile to load with multiple possible selectors
        try:
            # Try to wait for the profile header first
            page.wait_for_selector("[data-testid='UserProfileHeader']", timeout=10000)
        except:
            try:
                # If that fails, try waiting for the timeline container
                page.wait_for_selector("[data-testid='primaryColumn']", timeout=10000)
            except:
                try:
                    # If both fail, try waiting for any tweet or the profile name
                    page.wait_for_selector("[data-testid='tweet'], [data-testid='UserName']", timeout=10000)
                except:
                    print("Warning: Could not find profile elements. Proceeding anyway...")

        # Give some time for XHR calls to complete
        time.sleep(3)

        user_info = {}
        tweets_list = []

        # Capture user profile information
        profile_calls = [f for f in _xhr_calls if "UserBy" in f.url]
        if not profile_calls:
            # Try alternative endpoint names
            profile_calls = [f for f in _xhr_calls if "UserResultByRestId" in f.url]

        if profile_calls:
            try:
                data = profile_calls[0].json()
                user_result = data.get('data', {}).get('user', {}).get('result', {})
                if not user_result:
                    # Try alternative path
                    user_result = data.get('data', {}).get('user_result', {}).get('result', {})

                if user_result:
                    legacy = user_result.get('legacy', {})
                    user_info = {
                        'name': legacy.get('name', ''),
                        'username': legacy.get('screen_name', ''),
                        'description': legacy.get('description', ''),
                        'followers': legacy.get('followers_count', 0),
                        'following': legacy.get('following_count', 0),
                        'profile_image_url': legacy.get('profile_image_url_https', ''),
                        'is_verified': user_result.get('is_blue_verified', False),
                    }
            except Exception as e:
                print(f"Error extracting user info: {e}")

        # Capture user's tweets
        timeline_calls = [f for f in _xhr_calls if "UserTweets" in f.url]
        if not timeline_calls:
            # Try alternative endpoint names
            timeline_calls = [f for f in _xhr_calls if "UserMedia" in f.url]

        if timeline_calls:
            try:
                data = timeline_calls[0].json()
                instructions = data.get('data', {}).get('user', {}).get('result', {}).get('timeline', {}).get(
                    'timeline', {}).get('instructions', [])

                for instruction in instructions:
                    entries = instruction.get('entries', [])
                    for entry in entries:
                        content = entry.get('content', {})
                        if 'itemContent' in content:
                            tweet_result = content.get('itemContent', {}).get('tweet_results', {}).get('result', {})
                            if tweet_result:
                                legacy_tweet = tweet_result.get('legacy', {})
                                tweet_text = legacy_tweet.get('full_text', "")

                                # Extract media URLs
                                media_urls = []
                                extended_entities = legacy_tweet.get('extended_entities', {})
                                if 'media' in extended_entities:
                                    for media_item in extended_entities['media']:
                                        if media_item.get('type') in ['photo', 'video', 'animated_gif']:
                                            media_urls.append(media_item.get('media_url_https'))

                                # Extract external links
                                link_previews = []
                                card = tweet_result.get('card', {}).get('legacy', {}).get('binding_values', [])
                                for item in card:
                                    if item.get('key') == 'unified_card.destination_url' or item.get(
                                            'key') == 'card_url':
                                        link_previews.append(item.get('value', {}).get('string_value'))
                                for url_item in legacy_tweet.get('entities', {}).get('urls', []):
                                    link_previews.append(url_item.get('expanded_url'))
                                external_links = list(set([link for link in link_previews if link]))

                                tweet_data = {
                                    'text': tweet_text,
                                    'post_date': legacy_tweet.get('created_at', ''),
                                    'replies': legacy_tweet.get('reply_count', 0),
                                    'reposts': legacy_tweet.get('retweet_count', 0),
                                    'likes': legacy_tweet.get('favorite_count', 0),
                                    'views': tweet_result.get('views', {}).get('count', 'N/A'),
                                    'media_urls': media_urls,
                                    'external_links': external_links
                                }
                                tweets_list.append(tweet_data)
            except Exception as e:
                print(f"Error extracting tweets: {e}")

        browser.close()

        # Prepare output based on as_json_string flag
        if as_json_string:
            return json.dumps({"user": user_info, "tweets": tweets_list}, indent=4)
        else:
            # Format as plain text: user name and then each tweet text
            output = f"User: {user_info.get('name', 'N/A')} (@{user_info.get('username', 'N/A')})\n"
            output += f"Followers: {user_info.get('followers', 'N/A')}\n\n"
            output += "Recent Tweets:\n"
            for i, tweet in enumerate(tweets_list[:10], 1):  # Limit to first 10 tweets
                output += f"{i}. {tweet['text']}\n\n"
            return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape a user's profile and recent tweets from X (Twitter).")
    parser.add_argument(
        "profile_url",
        type=str,
        help="The URL of the user's profile (e.g., https://x.com/username)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the scraped data as a JSON string instead of plain text."
    )
    args = parser.parse_args()

    # Fix URL if missing protocol
    if not args.profile_url.startswith(('http://', 'https://')):
        args.profile_url = 'https://' + args.profile_url

    # Fix URL if it has a single slash after protocol
    if 'https:/' in args.profile_url and 'https://' not in args.profile_url:
        args.profile_url = args.profile_url.replace('https:/', 'https://')

    if args.json:
        output_data = scrape_user_timeline(args.profile_url, as_json_string=True)
        print(output_data)
    else:
        output_data = scrape_user_timeline(args.profile_url)
        print(output_data)