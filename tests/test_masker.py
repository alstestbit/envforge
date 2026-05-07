import pytest
from envforge.masker import mask_env, MaskResult, DEFAULT_MASK


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "supersecret",
    "API_TOKEN": "tok_abc123",
    "DEBUG": "true",
}


class TestMaskEnv:
    def test_returns_mask_result(self):
        result = mask_env(SAMPLE_ENV, keys=[])
        assert isinstance(result, MaskResult)

    def test_no_keys_leaves_env_unchanged(self):
        result = mask_env(SAMPLE_ENV, keys=[])
        assert result.env == SAMPLE_ENV

    def test_specified_key_is_masked(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD"])
        assert result.env["DB_PASSWORD"] == DEFAULT_MASK

    def test_unspecified_key_is_unchanged(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD"])
        assert result.env["APP_NAME"] == "myapp"

    def test_multiple_keys_masked(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD", "API_TOKEN"])
        assert result.env["DB_PASSWORD"] == DEFAULT_MASK
        assert result.env["API_TOKEN"] == DEFAULT_MASK

    def test_custom_mask_string(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD"], mask="[REDACTED]")
        assert result.env["DB_PASSWORD"] == "[REDACTED]"

    def test_partial_mask_reveals_trailing_chars(self):
        result = mask_env(SAMPLE_ENV, keys=["API_TOKEN"], partial=True, reveal_chars=3)
        assert result.env["API_TOKEN"].endswith("123")
        assert result.env["API_TOKEN"].startswith(DEFAULT_MASK)

    def test_partial_mask_short_value_fully_masked(self):
        env = {"KEY": "ab"}
        result = mask_env(env, keys=["KEY"], partial=True, reveal_chars=4)
        assert result.env["KEY"] == DEFAULT_MASK

    def test_has_masked_true_when_keys_masked(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD"])
        assert result.has_masked() is True

    def test_has_masked_false_when_no_keys(self):
        result = mask_env(SAMPLE_ENV, keys=[])
        assert result.has_masked() is False

    def test_masked_keys_list(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD", "API_TOKEN"])
        assert set(result.masked_keys()) == {"DB_PASSWORD", "API_TOKEN"}

    def test_summary_format(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD", "API_TOKEN"])
        assert result.summary() == f"2/{len(SAMPLE_ENV)} keys masked"

    def test_nonexistent_key_ignored(self):
        result = mask_env(SAMPLE_ENV, keys=["NONEXISTENT"])
        assert result.env == SAMPLE_ENV
        assert result.has_masked() is False

    def test_entry_str_masked(self):
        result = mask_env(SAMPLE_ENV, keys=["DB_PASSWORD"])
        entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
        assert "masked" in str(entry)

    def test_entry_str_unchanged(self):
        result = mask_env(SAMPLE_ENV, keys=[])
        entry = next(e for e in result.entries if e.key == "APP_NAME")
        assert "unchanged" in str(entry)
