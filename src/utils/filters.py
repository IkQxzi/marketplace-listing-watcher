import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config.dirs import FILTERS_DIR
from config.filters import LLMOutputFilters
from utils.io import read_json, write_json


def get_filters(item_name: str) -> LLMOutputFilters:
    """Fetches filters from item name, either from LLM API or file"""

    filter_path = FILTERS_DIR / f"{item_name}.json"

    if filter_path.exists():
        return LLMOutputFilters.model_validate(read_json(filter_path))
    else:
        return create_active_filters(item_name)


def _has_active_filters(item_name: str) -> bool:
    """Returns whether a specific item has active filters or not."""

    filter_path = FILTERS_DIR / f"{item_name}.json"

    return filter_path.exists()


def create_active_filters(item_name: str) -> LLMOutputFilters:
    """Creates filters for a specific item using an LLM API call, and saves them."""

    load_dotenv()

    #create AI client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = create_filter_prompt(item_name)

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite", #lightest model to ensure low usage
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LLMOutputFilters,
            temperature=0.1, #low temperature = results doesnt vary much for same item name
        ),
    )

    filters = LLMOutputFilters.model_validate_json(response.text)

    #save to file
    save_path = FILTERS_DIR / f"{item_name}.json"
    write_json(data=filters, path=save_path)

    return filters


def create_filter_prompt(item_name: str) -> str:
    return f"""Target: "{item_name}". Generate strict e-commerce search/cleaning filters in lowercase.
                Rules:
                1. required_keywords: essential brand/model terms identifying this exact item.
                2. banned_keywords: all wrong variants/sizes/models, accessories/cases/boxes, damaged/faulty/parts/locked states, and non-genuine listings.
                3. min_reasonable_price: realistic floor price dropping cheap accessories/parts.
                4. product_name: clean canonical name."""
