from api import SearchEndpointPayload
import logging
import json
from pathlib import Path

logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
Implement:
uv run main simple.yaml --price.lower=300

"""


def main() -> None:

    schema = json.dumps(SearchEndpointPayload.model_json_schema(), indent=2)
    SearchEndpointPayload.from_simple_yaml()

    logging.info(f"{schema}")
    Path("tmp.json").write_text(schema)

    return


if __name__ == "__main__":
    main()
