# FitFindr Planning Document

## What FitFindr Does
FitFindr is a fashion assistant agent that helps users find secondhand clothing items and style them. The user describes what they're looking for, and the agent searches mock listings, suggests an outfit using their wardrobe, and generates a shareable fit card caption. If no listings are found, the agent stops early and tells the user what to try differently.

## A Complete Interaction
User: "I'm looking for a vintage graphic tee under $30, size M. I mostly wear baggy jeans and chunky sneakers."

1. search_listings("vintage graphic tee", size="M", max_price=30) → returns 3 matches, top result: "Faded Band Tee — $22"
2. suggest_outfit(new_item=<band tee>, wardrobe=<user wardrobe>) → "Pair with wide-leg jeans and platform sneakers for a 90s grunge look"
3. create_fit_card(outfit=<suggestion>, new_item=<band tee>) → "thrifted this faded band tee for $22 and it was made for my wide-legs 🖤"

Error path: If search_listings returns [], agent sets error message and stops. suggest_outfit is never called with empty input.

## Tool Specs

### Tool 1: search_listings
- **What it does:** Searches the listings dataset and returns items matching description, size, and price
- **Inputs:**
  - description (str): what the user is looking for e.g. "graphic tee"
  - size (str or None): clothing size e.g. "M", "L"
  - max_price (float or None): maximum price in dollars
- **Returns:** List of matching listing dicts, each with fields: id, title, price, size, platform, condition, style_tags
- **Failure mode:** Returns empty list [] if nothing matches. Agent tells user no results found and suggests loosening filters.

### Tool 2: suggest_outfit
- **What it does:** Given a new item and the user's wardrobe, uses LLM to suggest a complete outfit
- **Inputs:**
  - new_item (dict): a single listing dict from search_listings
  - wardrobe (dict): wardrobe object from data_loader with an "items" list
- **Returns:** String describing a complete outfit combination
- **Failure mode:** If wardrobe is empty, LLM gives general styling advice for the item alone. Never crashes.

### Tool 3: create_fit_card
- **What it does:** Uses LLM to generate a short, Instagram-style caption for the outfit
- **Inputs:**
  - outfit (str): the outfit suggestion string from suggest_outfit
  - new_item (dict): the listing dict
- **Returns:** A short, casual, shareable caption string
- **Failure mode:** If outfit string is empty, returns error message string instead of crashing.

## Planning Loop