import json
from datetime import datetime

from google import genai
from pydantic import ValidationError

from marketplace_listing_watcher.api import SearchEndpointPayload
from marketplace_listing_watcher.config.llm import GEMINI_API_KEY
from marketplace_listing_watcher.llm.prompts import RAW_PROMPT


class GeminiClient:
    """
    Client to prompt Gemini for Search Endpoint payload.
    If payload generation fails, will reattempt up to max_reattempts.
    Defaults to Gemini 3.5 Flash Lite.
    """

    def __init__(
        self,
        user_input: str,
        api_key: str,
        max_reattempts: int = 3,
        model="gemini-3.5-flash-lite",
    ) -> None:
        self._model = model
        self._client = genai.Client(api_key=api_key)
        self._interaction_id: str

        self._max_reattempts = max_reattempts
        self._reattempt_count = 0
        self._error_json_list = []

        self._user_input = user_input
        self._system_prompt = self._create_system_prompt()

    def generate_payload(
        self, _error_prompt: str | None = None
    ) -> SearchEndpointPayload:
        """
        Prompt LLM and return its (hopefully) structured response.
        Re-prompts the number of times defined in max_reattempts (see constructor).
        """

        if self._reattempt_count == self._max_reattempts:
            breakpoint()
            raise RuntimeError("Exceeded max reattempts.")

        try:
            llm_output = self._prompt_for_payload_json(_error_prompt)
            llm_output = self._clean_llm_output(llm_output)
            payload = SearchEndpointPayload.model_validate_json(llm_output)
            breakpoint()
        except ValidationError as e:
            breakpoint()
            self._reattempt_count += 1
            self._error_json_list += e.json()
            _error_prompt = self._create_error_prompt(e.json())
            self.generate_payload(_error_prompt)

        if not payload:
            raise ValueError(
                "After max reattempts, payload still not formed correctly!"
            )
        return payload

    def _prompt_for_payload_json(self, prompt: str | None) -> str:
        """
        Prompt LLM for json representing payload.
        Uses the _error_list attribute to see previous errors.
        """

        interaction = self._client.interactions.create(
            model=self._model,
            input=prompt if prompt else self._user_input,
            system_instruction=self._system_prompt,
        )

        if not interaction.output_text:
            raise RuntimeError("LLM did not produce any output!")

        self._interaction_id = interaction.id
        return interaction.output_text

    def _clean_llm_output(self, llm_output: str) -> str:
        return llm_output.removeprefix("```json").removesuffix("```")

    def _create_error_prompt(self, error_msg: str) -> str:
        """Create new prompt from error message."""
        error_dict = json.loads(error_msg)
        error_dict[0]["user_input"] = (
            "Re-generate the Payload for the same product, taking into account the errors raised by validation."
        )

    def _create_system_prompt(self) -> str:
        """
        Create system prompt for LLM using natural language.
        Does not include JSON schema.
        """

        return RAW_PROMPT.replace("<<TODAY>>", datetime.today().isoformat())


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        raise ValueError()
    input_str = "iphone 18 base model"
    client = GeminiClient(input_str, GEMINI_API_KEY)
    payload = client.generate_payload()
    breakpoint()
