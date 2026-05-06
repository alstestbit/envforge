"""Export parsed .env data to alternate formats (JSON, YAML, TOML)."""

import json
from typing import Dict, Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

try:
    import tomllib  # Python 3.11+
    import tomli_w
    _TOML_AVAILABLE = True
except ImportError:
    _TOML_AVAILABLE = False


SUPPORTED_FORMATS = ["json", "yaml", "toml"]


def export_to_json(env: Dict[str, str], indent: int = 2) -> str:
    """Serialize env dict to a JSON string."""
    return json.dumps(env, indent=indent, sort_keys=True)


def export_to_yaml(env: Dict[str, str]) -> str:
    """Serialize env dict to a YAML string."""
    if not _YAML_AVAILABLE:
        raise RuntimeError(
            "PyYAML is not installed. Run: pip install pyyaml"
        )
    return yaml.dump(env, default_flow_style=False, sort_keys=True)


def export_to_toml(env: Dict[str, str]) -> str:
    """Serialize env dict to a TOML string."""
    if not _TOML_AVAILABLE:
        raise RuntimeError(
            "tomli-w is not installed. Run: pip install tomli-w"
        )
    return tomli_w.dumps(env)


def export_env(
    env: Dict[str, str],
    fmt: str,
    output_path: Optional[str] = None,
) -> str:
    """Export env dict to the given format. Optionally write to a file.

    Args:
        env: Parsed environment variables.
        fmt: One of 'json', 'yaml', 'toml'.
        output_path: If provided, write the result to this path.

    Returns:
        The serialized string.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}"
        )

    if fmt == "json":
        result = export_to_json(env)
    elif fmt == "yaml":
        result = export_to_yaml(env)
    else:
        result = export_to_toml(env)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(result)

    return result
