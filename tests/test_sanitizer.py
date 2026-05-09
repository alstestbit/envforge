import pytest
from envforge.sanitizer import sanitize_env, SanitizeResult, SanitizeEntry


class TestSanitizeEnv:
    def test_returns_sanitize_result(self):
        result = sanitize_env({"KEY": "value"})
        assert isinstance(result, SanitizeResult)

    def test_clean_env_has_no_changes(self):
        env = {"KEY": "value", "OTHER": "clean"}
        result = sanitize_env(env)
        assert not result.has_changes
        assert result.env == env

    def test_strips_leading_trailing_whitespace(self):
        result = sanitize_env({"KEY": "  hello  "})
        assert result.env["KEY"] == "hello"
        assert result.has_changes
        assert "KEY" in result.changed_keys

    def test_strips_double_quotes(self):
        result = sanitize_env({"KEY": '"quoted"'})
        assert result.env["KEY"] == "quoted"
        assert result.has_changes

    def test_strips_single_quotes(self):
        result = sanitize_env({"KEY": "'single'"})
        assert result.env["KEY"] == "single"
        assert result.has_changes

    def test_no_strip_quotes_when_disabled(self):
        result = sanitize_env({"KEY": '"quoted"'}, strip_quotes=False)
        assert result.env["KEY"] == '"quoted"'

    def test_no_strip_whitespace_when_disabled(self):
        result = sanitize_env({"KEY": "  val  "}, strip_whitespace=False)
        assert result.env["KEY"] == "  val  "

    def test_removes_control_characters(self):
        result = sanitize_env({"KEY": "val\x00ue"})
        assert result.env["KEY"] == "value"
        assert result.has_changes

    def test_no_remove_control_chars_when_disabled(self):
        result = sanitize_env({"KEY": "val\x00ue"}, remove_control_chars=False)
        assert "\x00" in result.env["KEY"]

    def test_normalizes_carriage_return_newlines(self):
        result = sanitize_env({"KEY": "line1\r\nline2"})
        assert result.env["KEY"] == "line1\nline2"
        assert result.has_changes

    def test_normalizes_bare_carriage_return(self):
        result = sanitize_env({"KEY": "line1\rline2"})
        assert result.env["KEY"] == "line1\nline2"
        assert result.has_changes

    def test_multiple_keys_some_changed(self):
        env = {"CLEAN": "ok", "DIRTY": "  spaces  ", "QUOTED": '"val"'}
        result = sanitize_env(env)
        assert result.env["CLEAN"] == "ok"
        assert result.env["DIRTY"] == "spaces"
        assert result.env["QUOTED"] == "val"
        assert len(result.changes) == 2
        assert "CLEAN" not in result.changed_keys

    def test_entry_has_correct_fields(self):
        result = sanitize_env({"KEY": "  trimmed  "})
        entry = result.changes[0]
        assert isinstance(entry, SanitizeEntry)
        assert entry.key == "KEY"
        assert entry.original == "  trimmed  "
        assert entry.sanitized == "trimmed"
        assert len(entry.reason) > 0

    def test_str_entry(self):
        result = sanitize_env({"KEY": "  val  "})
        s = str(result.changes[0])
        assert "KEY" in s
        assert "->" in s

    def test_summary_no_changes(self):
        result = sanitize_env({"KEY": "clean"})
        assert "No sanitization" in result.summary()

    def test_summary_with_changes(self):
        result = sanitize_env({"KEY": "  val  "})
        summary = result.summary()
        assert "1 key(s)" in summary
        assert "KEY" in summary
