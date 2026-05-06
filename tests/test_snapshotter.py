"""Tests for envforge.snapshotter."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from envforge.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "warn"}


class TestTakeSnapshot:
    def test_returns_snapshot_instance(self):
        snap = take_snapshot(ENV_A, label="test")
        assert isinstance(snap, Snapshot)

    def test_label_is_stored(self):
        snap = take_snapshot(ENV_A, label="my-label")
        assert snap.label == "my-label"

    def test_entries_match_env(self):
        snap = take_snapshot(ENV_A, label="x")
        assert snap.entries == ENV_A

    def test_timestamp_is_set(self):
        snap = take_snapshot(ENV_A, label="x")
        assert snap.timestamp is not None
        assert "T" in snap.timestamp  # ISO format


class TestSaveAndLoadSnapshot:
    def test_round_trip(self):
        snap = take_snapshot(ENV_A, label="round-trip")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_snapshot(snap, path)
            loaded = load_snapshot(path)
            assert loaded.label == snap.label
            assert loaded.entries == snap.entries
            assert loaded.timestamp == snap.timestamp
        finally:
            os.unlink(path)

    def test_saved_file_is_valid_json(self):
        snap = take_snapshot(ENV_A, label="json-check")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            save_snapshot(snap, path)
            with open(path) as f:
                data = json.load(f)
            assert "entries" in data
            assert "label" in data
        finally:
            os.unlink(path)


class TestDiffSnapshots:
    def _make(self, env, label="snap"):
        return take_snapshot(env, label=label)

    def test_no_diff_when_identical(self):
        a = self._make(ENV_A)
        b = self._make(ENV_A)
        result = diff_snapshots(a, b)
        assert not result.has_differences

    def test_added_keys_detected(self):
        a = self._make({"X": "1"})
        b = self._make({"X": "1", "Y": "2"})
        result = diff_snapshots(a, b)
        assert "Y" in result.added

    def test_removed_keys_detected(self):
        a = self._make({"X": "1", "Y": "2"})
        b = self._make({"X": "1"})
        result = diff_snapshots(a, b)
        assert "Y" in result.removed

    def test_changed_keys_detected(self):
        a = self._make({"HOST": "localhost"})
        b = self._make({"HOST": "prod.example.com"})
        result = diff_snapshots(a, b)
        assert "HOST" in result.changed
        assert result.changed["HOST"] == ("localhost", "prod.example.com")

    def test_summary_reflects_changes(self):
        a = self._make(ENV_A)
        b = self._make(ENV_B)
        result = diff_snapshots(a, b)
        summary = result.summary()
        assert "added" in summary or "removed" in summary or "changed" in summary

    def test_summary_no_differences(self):
        a = self._make(ENV_A)
        b = self._make(ENV_A)
        result = diff_snapshots(a, b)
        assert result.summary() == "no differences"
