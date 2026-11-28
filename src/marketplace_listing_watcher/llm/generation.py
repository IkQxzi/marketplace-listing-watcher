import json
from datetime import datetime

from google import genai
from pydantic import ValidationError

from marketplace_listing_watcher.api import SearchEndpointPayload
from marketplace_listing_watcher.api.searching import ListingSearcher
from marketplace_listing_watcher.config.dirs import LOG_DIR
from marketplace_listing_watcher.llm.prompts import REFINEMENT_PROMPT, SYSTEM_PROMPT


class GeminiClient:
    """
    Client to prompt Gemini for Search Endpoint payload.
    Uses up to max_llm_request requests to Gemini before raising error.
    Uses access token to refine payload by showing LLM a Search Endpoint response,
    so uses 1 API request to Search Endopint also.
    Defaults to Gemini 3.5 Flash Lite.
    """

    def __init__(
        self,
        user_input: str,
        api_key: str,
        access_token: str,
        max_llm_requests: int = 5,
        model="gemini-3.5-flash-lite",
    ) -> None:
        self._MODEL = model
        self._client = genai.Client(api_key=api_key)
        self._interaction_id: str | None = None

        self._access_token = access_token
        self._max_llm_requests = max_llm_requests
        self._reattempt_count = 0
        self._error_json_list = []

        self._user_input = user_input
        self._system_prompt = self._create_system_prompt()

        self._payload: SearchEndpointPayload

    def generate_payload(
        self, _error_prompt: str | None = None
    ) -> SearchEndpointPayload:
        """
        Prompt LLM and return its (hopefully) structured response.
        Re-prompts the number of times defined in max_reattempts (see constructor).
        """

        self._form_payload(self._user_input)
        self._refine_payload()  # Calls _form_payload() also

        if not self._payload:
            raise ValueError(
                "After max reattempts, payload still not formed correctly!"
            )
        return self._payload

    def _form_payload(self, prompt: str) -> SearchEndpointPayload:
        if self._reattempt_count == self._max_llm_requests:
            raise RuntimeError("Exceeded max reattempts.")

        try:
            llm_output = self._prompt_for_payload_json(prompt)
            llm_output = self._remove_json_flag(llm_output)
            payload = SearchEndpointPayload.model_validate_json(llm_output)
        except ValidationError as e:
            self._reattempt_count += 1
            self._error_json_list += e.json()
            prompt = self._create_error_prompt(e.json())
            payload = self._form_payload(prompt)

        self._payload = payload
        return payload

    def _refine_payload(self):
        payload_copy = self._payload.model_copy(deep=True)
        payload_copy.filter.item_start_date = None
        searcher = ListingSearcher(payload_copy, LOG_DIR)
        listings = searcher.get_latest_listings_and_alert(self._access_token)
        if len(listings) == 0:
            raise ValueError("No listings returned by result!")

        listing_titles = [listing.title for listing in listings]
        prompt = self._create_prompt_from_titles(listing_titles)
        self._form_payload(prompt)

    def _prompt_for_payload_json(self, prompt: str) -> str:
        """
        Prompt LLM for json representing payload.
        Automatically strips out the ```json``` flag from the LLM
        Uses the _error_list attribute to see previous errors.
        """

        breakpoint()
        interaction_args = {
            "model": self._MODEL,
            "input": prompt,
            "system_instruction": self._system_prompt,
        }
        if self._interaction_id:
            interaction_args["previous_interaction_id"] = self._interaction_id

        interaction = self._client.interactions.create(**interaction_args)

        if not interaction.output_text:
            raise RuntimeError("LLM did not produce any output!")

        self._interaction_id = interaction.id
        return interaction.output_text

    def _create_system_prompt(self) -> str:
        """
        Create system prompt for LLM using natural language.
        Does not include JSON schema.
        """

        return SYSTEM_PROMPT.replace("<<TODAY>>", datetime.today().isoformat()).replace(
            "<<SCHEMA>>", json.dumps(SearchEndpointPayload.model_json_schema())
        )

    def _create_prompt_from_titles(self, titles: list[str]) -> str:
        """Create prompt for model to refine its payload from list of titles in a response."""
        return REFINEMENT_PROMPT.replace("<<COUNT>>", str(len(titles))).replace(
            "<<TITLES>>", ", ".join(titles)
        )

    def _remove_json_flag(self, llm_output: str) -> str:
        return llm_output.removeprefix("```json").removesuffix("```")

    def _create_error_prompt(self, error_msg: str) -> str:
        """Create new prompt from error message."""
        error_dict = json.loads(error_msg)
        error_dict[0]["user_input"] = (
            "Re-generate the Payload for the same product, taking into account the errors raised by validation."
        )
        return json.dumps(error_dict)
