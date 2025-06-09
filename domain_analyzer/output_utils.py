import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_json(data: dict[str, Any], output_file: str) -> None:
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving JSON to {output_file}: {e}")
