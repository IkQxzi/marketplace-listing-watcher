import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config.dirs import ACTIVE_DIR
from config.filters import LLMOutputFilters
from utils.io import read_json, write_json


def get_filters(item_name: str) -> LLMOutputFilters:
    """Fetches filters from item name, either from LLM API or file"""

    filter_path = ACTIVE_DIR / item_name / "filters.json"

    if filter_path.exists():
        return LLMOutputFilters.model_validate(read_json(filter_path))
    else:
        return create_active_filters(item_name)


def _has_active_filters(item_name: str) -> bool:
    """Returns whether a specific item has active filters or not."""

    filter_path = ACTIVE_DIR / item_name / "filters.json"

    return filter_path.exists()


def create_active_filters(item_name: str) -> LLMOutputFilters:
    """Creates filters for a specific item using an LLM API call, and saves them."""

    load_dotenv()
    api_key=os.getenv("gemini_api_key")

    if not api_key:
        raise ValueError("Gemini API key not set in .env")

    #create AI client
    client = genai.Client(api_key=api_key)
    prompt = create_filter_prompt(item_name)

    response = client.models.generate_content(
        model="gemini-3.5-flash", #lightest model to ensure low usage
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LLMOutputFilters,
            temperature=0.1, #low temperature = results dont vary much for same item name
        ),
    )

    if not response or response.text == "":
        raise Exception("Filters not returned properly")

    filters = LLMOutputFilters.model_validate_json(response.text)

    #save to file
    save_path = ACTIVE_DIR / item_name / "filters.json"
    write_json(data=filters.model_dump(), path=save_path)

    return filters


def create_filter_prompt(item_name: str) -> str:
    return f"""Target: "{item_name}". Generate strict e-commerce search/cleaning filters in lowercase.
                Rules:
1. required_keywords: Minimal essential terms that uniquely identify the item (e.g. brand + exact model/generation).
2. banned_keywords: Comprehensive lowercase list to isolate this exact SKU/tier. Must include:
   - Sibling variants & tiers (e.g. pro, max, plus, ultra, mini, fe, air, ti, super).
   - Unspaced/hyphenated variations (e.g. promax, 16pro, 128-gb).
   - Conflicting storage/specs (e.g. 64gb, 256gb, 512gb, 1tb, 8gb, 16gb, 24gb).
   - Adjacent generations (both older and newer lines).
   - Accessories, non-device items & packaging (e.g. case, cover, box, dummy, glass, strap, cable, packaging).
   - Faults, locks, parts & non-genuine (e.g. broken, parts, spares, cracked, faulty, icloud, blacklisted, bad esn, replica, mdm, demo).
3. min_reasonable_price: A realistic floor price (currency unit agnostic) to discard accessories and empty boxes.
4. product_name: Clean canonical name of the target product."""