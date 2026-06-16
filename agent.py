import os
from dotenv import load_dotenv
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

load_dotenv()


def run_agent(description, size, max_price, wardrobe=None):
    """
    Planning loop that runs the FitFindr agent.
    
    Args:
        description (str): what the user is looking for
        size (str or None): clothing size
        max_price (float or None): maximum price
        wardrobe (dict or None): user's wardrobe, defaults to example wardrobe
    
    Returns:
        dict: session state with results or error
    """
    # Initialize session state
    session = {
        "description": description,
        "size": size,
        "max_price": max_price,
        "selected_item": None,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None
    }

    # Use example wardrobe if none provided
    if wardrobe is None:
        wardrobe = get_example_wardrobe()

    # STEP 1: Search listings
    print(f"[Agent] Searching for: {description}, size={size}, max_price={max_price}")
    results = search_listings(description, size, max_price)

    # STEP 2: Check if results are empty — stop early if so
    if not results:
        session["error"] = (
            f"No listings found for '{description}'"
            + (f" in size {size}" if size else "")
            + (f" under ${max_price}" if max_price else "")
            + ". Try broader keywords, a different size, or a higher budget."
        )
        print(f"[Agent] No results found. Stopping early.")
        return session

    # STEP 3: Store the top result in session
    session["selected_item"] = results[0]
    print(f"[Agent] Found item: {results[0].get('title')} — ${results[0].get('price')}")

    # STEP 4: Suggest outfit using the found item and wardrobe
    print(f"[Agent] Generating outfit suggestion...")
    outfit = suggest_outfit(session["selected_item"], wardrobe)
    session["outfit_suggestion"] = outfit
    print(f"[Agent] Outfit suggestion: {outfit[:60]}...")

    # STEP 5: Create fit card using outfit and item
    print(f"[Agent] Generating fit card...")
    fit_card = create_fit_card(session["outfit_suggestion"], session["selected_item"])
    session["fit_card"] = fit_card
    print(f"[Agent] Fit card: {fit_card}")

    return session


# Test the agent directly
if __name__ == "__main__":
    print("=== TEST 1: Happy path ===")
    result = run_agent("graphic tee", size="M", max_price=50)
    print("\nFinal session:")
    for key, val in result.items():
        print(f"  {key}: {val}")

    print("\n=== TEST 2: No results path ===")
    result2 = run_agent("designer ballgown", size="XXS", max_price=5)
    print("\nFinal session:")
    for key, val in result2.items():
        print(f"  {key}: {val}")