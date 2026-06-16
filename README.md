# FitFindr 👗

A fashion assistant agent that helps users find secondhand clothing and style it instantly.
Given a search query, FitFindr searches mock thrift listings, suggests a complete outfit,
and generates a shareable Instagram-style caption.

---

## How to Run

1. Clone the repo and activate the virtual environment:
```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
   pip install groq gradio python-dotenv
```

3. Create a `.env` file in the project root:
GROQ_API_KEY=your_key_here

4. Run the app:
```bash
   python app.py
```

5. Open http://127.0.0.1:7860 in your browser.

---

## Tool Inventory

### 1. `search_listings(description, size, max_price)`
- **Inputs:**
  - `description` (str): what the user is looking for e.g. "vintage graphic tee"
  - `size` (str or None): clothing size e.g. "M", "L", or None to skip
  - `max_price` (float or None): maximum price in dollars, or None to skip
- **Output:** List of matching listing dicts. Empty list `[]` if nothing found.
- **Purpose:** Searches the mock listings dataset and returns items matching all provided filters.

### 2. `suggest_outfit(new_item, wardrobe)`
- **Inputs:**
  - `new_item` (dict): a single listing dict returned by search_listings
  - `wardrobe` (dict): wardrobe object with an "items" list
- **Output:** String describing a complete outfit combination.
- **Purpose:** Uses the Groq LLM to suggest how to style the new item with existing wardrobe pieces.

### 3. `create_fit_card(outfit, new_item)`
- **Inputs:**
  - `outfit` (str): the outfit suggestion string from suggest_outfit
  - `new_item` (dict): the listing dict
- **Output:** A short, casual, Instagram-style caption string.
- **Purpose:** Generates a shareable fit card caption using the Groq LLM.

---

## How the Planning Loop Works

The planning loop in `agent.py` runs as follows:

1. Call `search_listings(description, size, max_price)`
2. **If results is empty:** set `session["error"]` with a helpful message and return early. `suggest_outfit` is never called with empty input.
3. **If results exist:** set `session["selected_item"] = results[0]`
4. Call `suggest_outfit(selected_item, wardrobe)` → store in `session["outfit_suggestion"]`
5. Call `create_fit_card(outfit_suggestion, selected_item)` → store in `session["fit_card"]`
6. Return session

The agent behaves differently based on what `search_listings` returns — it does not call all three tools unconditionally every time.

---

## State Management

All state is stored in a `session` dictionary that persists across tool calls within one interaction:

| Key | Set when | Used by |
|-----|----------|---------|
| `session["selected_item"]` | After search_listings succeeds | suggest_outfit |
| `session["outfit_suggestion"]` | After suggest_outfit runs | create_fit_card |
| `session["fit_card"]` | After create_fit_card runs | Displayed to user |
| `session["error"]` | When any tool fails | Displayed to user instead of results |

The user never has to re-enter information between steps — it flows automatically through the session.

---

## Error Handling

| Tool | Failure Mode | Agent Response |
|------|-------------|----------------|
| `search_listings` | No matches found | Returns `[]`, agent sets `session["error"]` = "No listings found for '...'. Try broader keywords, a different size, or a higher budget." Stops early, never calls suggest_outfit. |
| `suggest_outfit` | Empty wardrobe | LLM is prompted to give general styling advice for the item alone. Returns a useful string, never crashes. |
| `create_fit_card` | Empty outfit string | Returns `"Could not generate fit card: outfit description was empty."` instead of crashing. |

**Concrete example from testing:**
Running `search_listings("designer ballgown", size="XXS", max_price=5)` returns `[]`.
The agent responds: *"No listings found for 'designer ballgown' in size XXS under $5. Try broader keywords, a different size, or a higher budget."*
`suggest_outfit` is never called.

---

## Spec Reflection

**One way the spec helped:** Writing the planning loop in planning.md before coding made it very clear where the early-return branch needed to go. Without that upfront design, it would have been easy to accidentally call suggest_outfit with an empty item and crash the agent.

**One way implementation diverged:** The spec assumed the wardrobe would always come from user input. In practice, I used the pre-built `get_example_wardrobe()` from the data loader and added a checkbox in the UI to toggle between a full and empty wardrobe. This made testing error handling much easier during development.

---

## AI Tool Usage

**Instance 1 — tools.py implementation:**
I used Claude to get a starting point for `search_listings` by sharing the Tool 1 spec from planning.md. Claude generated a basic structure but I did not use it as-is. The description matching logic it produced used exact string matching which returned poor results, so I rewrote that part myself to split the description into individual words and check each one against the listing title, description, and style tags. I also wrote the size and price filter logic myself after testing showed the generated version had edge cases.

**Instance 2 — agent.py planning loop:**
I shared the architecture diagram from planning.md with Claude and asked for help scaffolding `run_agent()`. The output gave me the general shape of the function but it called all three tools unconditionally without checking whether search_listings returned results. I rewrote the conditional logic myself so the agent stops early and sets a proper error message when no results are found. The final implementation follows my own planning.md design rather than what Claude generated.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All 8 tests pass, covering happy paths and all three failure modes.