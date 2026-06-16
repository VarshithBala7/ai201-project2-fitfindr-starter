import os
from dotenv import load_dotenv
from groq import Groq
from utils.data_loader import load_listings

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def search_listings(description, size, max_price):
    """
    Searches mock listings and returns matching items.
    
    Args:
        description (str): what the user is looking for e.g. "graphic tee"
        size (str or None): clothing size e.g. "M", "L", or None to skip filter
        max_price (float or None): maximum price, or None to skip filter
    
    Returns:
        list: list of matching listing dicts, empty list if nothing found
    """
    try:
        listings = load_listings()
        results = []

        description_words = description.lower().split()

        for item in listings:
            # Check size filter
            if size is not None:
                if item.get("size", "").upper() != size.upper():
                    continue

            # Check price filter
            if max_price is not None:
                if item.get("price", 9999) > max_price:
                    continue

            # Check description match against title, description, style_tags
            searchable = (
                item.get("title", "").lower() + " " +
                item.get("description", "").lower() + " " +
                " ".join(item.get("style_tags", [])).lower()
            )

            if any(word in searchable for word in description_words):
                results.append(item)

        return results

    except Exception as e:
        print(f"search_listings error: {e}")
        return []


def suggest_outfit(new_item, wardrobe):
    """
    Given a new item and user wardrobe, suggests a complete outfit using LLM.
    
    Args:
        new_item (dict): a listing dict from search_listings
        wardrobe (dict): wardrobe object with an "items" list
    
    Returns:
        str: outfit suggestion text
    """
    try:
        item_title = new_item.get("title", "the item")
        item_desc = new_item.get("description", "")
        item_tags = ", ".join(new_item.get("style_tags", []))

        wardrobe_items = wardrobe.get("items", [])

        if len(wardrobe_items) == 0:
            wardrobe_text = "The user has an empty wardrobe. Give general styling advice for this item."
        else:
            wardrobe_lines = []
            for w in wardrobe_items:
                wardrobe_lines.append(f"- {w.get('title', 'item')} ({w.get('category', '')})")
            wardrobe_text = "User's wardrobe:\n" + "\n".join(wardrobe_lines)

        prompt = f"""You are a fashion stylist helping someone style a thrifted item.

New item: {item_title}
Description: {item_desc}
Style tags: {item_tags}

{wardrobe_text}

Suggest one complete outfit using this new item and pieces from their wardrobe. 
Be specific, casual, and fun. Keep it to 2-3 sentences."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"suggest_outfit error: {e}")
        return f"Could not generate outfit suggestion. Error: {str(e)}"


def create_fit_card(outfit, new_item):
    """
    Generates a short Instagram-style caption for the outfit.
    
    Args:
        outfit (str): the outfit suggestion from suggest_outfit
        new_item (dict): the listing dict
    
    Returns:
        str: a short shareable caption
    """
    try:
        if not outfit or outfit.strip() == "":
            return "Could not generate fit card: outfit description was empty."

        item_title = new_item.get("title", "this piece")
        price = new_item.get("price", "")
        platform = new_item.get("platform", "a thrift store")

        prompt = f"""You are writing an Instagram caption for a thrift outfit post.

Item found: {item_title} for ${price} on {platform}
Outfit: {outfit}

Write a SHORT, casual, lowercase Instagram caption (1-2 sentences max).
Use 1-2 emojis. Sound like a real person, not a brand. 
Make it sound authentic and fun. Do NOT use hashtags."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.9
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"create_fit_card error: {e}")
        return f"Could not generate fit card. Error: {str(e)}"