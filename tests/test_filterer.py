import pytest
from envforge.filterer import filter_env, FilterResult


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "abc123",
}


class TestFilterEnv:
    def test_returns_filter_result(self):
        result = filter_env(SAMPLE_ENV)
        assert isinstance(result, FilterResult)

    def test_no_criteria_returns_full_env(self):
        result = filter_env(SAMPLE_ENV)
        assert result.filtered == SAMPLE_ENV
        assert result.excluded == []

    def test_filter_by_keys(self):
        result = filter_env(SAMPLE_ENV, keys=["APP_NAME", "DB_HOST"])
        assert "APP_NAME" in result.filtered
        assert "DB_HOST" in result.filtered
        assert "DB_PORT" not in result.filtered

    def test_filter_by_prefix(self):
        result = filter_env(SAMPLE_ENV, prefix="APP_")
        assert "APP_NAME" in result.filtered
        assert "APP_ENV" in result.filtered
        assert "DB_HOST" not in result.filtered

    def test_filter_by_pattern(self):
        result = filter_env(SAMPLE_ENV, pattern=r"^DB_")
        assert "DB_HOST" in result.filtered
        assert "DB_PORT" in result.filtered
        assert "APP_NAME" not in result.filtered

    def test_invert_excludes_matched_keys(self):
        result = filter_env(SAMPLE_ENV, prefix="DB_", invert=True)
        assert "DB_HOST" not in result.filtered
        assert "DB_PORT" not in result.filtered
        assert "APP_NAME" in result.filtered

    def test_excluded_list_populated(self):
        result = filter_env(SAMPLE_ENV, keys=["APP_NAME"])
        assert len(result.excluded) == len(SAMPLE_ENV) - 1
        assert "APP_NAME" not in result.excluded

    def test_has_exclusions_true_when_keys_dropped(self):
        result = filter_env(SAMPLE_ENV, keys=["APP_NAME"])
        assert result.has_exclusions() is True

    def test_has_exclusions_false_when_all_kept(self):
        result = filter_env(SAMPLE_ENV)
        assert result.has_exclusions() is False

    def test_summary_no_exclusions(self):
        result = filter_env(SAMPLE_ENV)
        assert result.summary() == "No keys excluded."

    def test_summary_with_exclusions(self):
        result = filter_env(SAMPLE_ENV, keys=["APP_NAME"])
        assert "Excluded" in result.summary()
        assert str(len(SAMPLE_ENV) - 1) in result.summary()

    def test_pattern_and_prefix_combined(self):
        result = filter_env(SAMPLE_ENV, pattern=r"SECRET", prefix="APP_")
        assert "SECRET_KEY" in result.filtered
        assert "APP_NAME" in result.filtered
        assert "DB_HOST" not in result.filtered
