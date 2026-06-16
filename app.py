import gradio as gr
from agent import run_agent
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


def handle_query(description, size, max_price, use_empty_wardrobe):
    """
    Handles user input from the Gradio UI and runs the agent.
    """
    # Clean up inputs
    size = size.strip() if size and size.strip() != "" else None
    try:
        max_price = float(max_price) if max_price and str(max_price).strip() != "" else None
    except ValueError:
        max_price = None

    # Choose wardrobe
    wardrobe = get_empty_wardrobe() if use_empty_wardrobe else get_example_wardrobe()

    # Run the agent
    session = run_agent(description, size, max_price, wardrobe)

    # Map session to output panels
    if session["error"]:
        return session["error"], "", ""

    item = session["selected_item"]
    item_display = (
        f"✅ Found: {item.get('title')}\n"
        f"💰 Price: ${item.get('price')}\n"
        f"📦 Platform: {item.get('platform')}\n"
        f"📏 Size: {item.get('size')}\n"
        f"🏷️ Condition: {item.get('condition')}\n"
        f"🎨 Colors: {', '.join(item.get('colors', []))}\n"
        f"🏷️ Tags: {', '.join(item.get('style_tags', []))}"
    )

    outfit_display = session["outfit_suggestion"] or ""
    fit_card_display = session["fit_card"] or ""

    return item_display, outfit_display, fit_card_display


# Build the Gradio UI
with gr.Blocks(title="FitFindr") as demo:
    gr.Markdown("# 👗 FitFindr\nFind thrifted pieces and style them instantly.")

    with gr.Row():
        with gr.Column():
            description_input = gr.Textbox(
                label="What are you looking for?",
                placeholder="e.g. vintage graphic tee, floral dress, leather jacket"
            )
            size_input = gr.Textbox(
                label="Size (optional)",
                placeholder="e.g. M, L, XS"
            )
            price_input = gr.Number(
                label="Max Price in $ (optional)",
                value=None
            )
            empty_wardrobe_checkbox = gr.Checkbox(
                label="I have an empty wardrobe (test mode)",
                value=False
            )
            search_btn = gr.Button("Find My Fit 🔍", variant="primary")

    with gr.Row():
        item_output = gr.Textbox(label="🛍️ Item Found", lines=7)
        outfit_output = gr.Textbox(label="👚 Outfit Suggestion", lines=7)
        fitcard_output = gr.Textbox(label="📸 Fit Card Caption", lines=7)

    search_btn.click(
        fn=handle_query,
        inputs=[description_input, size_input, price_input, empty_wardrobe_checkbox],
        outputs=[item_output, outfit_output, fitcard_output]
    )

demo.launch()