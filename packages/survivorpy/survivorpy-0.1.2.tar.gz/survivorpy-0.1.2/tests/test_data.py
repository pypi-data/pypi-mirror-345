import pytest
import pandas as pd
import json
import base64
from unittest.mock import patch, MagicMock
from survivorpy import data

# ----------------------
# Test: get_table_names
# ----------------------

def test_get_table_names_reads_from_cache(tmp_path):
    expected_tables = ["castaways", "seasons"]
    table_path = tmp_path / "mock_table_names.json"
    table_path.write_text(json.dumps(expected_tables))

    with patch("survivorpy.data._CACHE_TABLE_NAMES_PATH", table_path):
        result = data.get_table_names()
        assert result == expected_tables


# ----------------------
# Test: get_last_synced
# ----------------------

def test_get_last_synced_reads_timestamp(tmp_path):
    timestamp = "2024-12-01T08:00:00"
    path = tmp_path / "mock_last_synced.json"
    path.write_text(json.dumps({"timestamp": timestamp}))

    with patch("survivorpy.data._CACHE_LAST_SYNCED_PATH", path):
        assert data.get_last_synced() == timestamp


# ----------------------
# Test: load
# ----------------------

@patch("survivorpy.data.get_table_names", return_value=["castaways"])
@patch("survivorpy.data.pd.read_parquet")
def test_load_valid_table(mock_read_parquet, mock_get_names):
    df_mock = pd.DataFrame({"name": ["Parvati", "Ozzy"]})
    mock_read_parquet.return_value = df_mock
    result = data.load("castaways")
    pd.testing.assert_frame_equal(result, df_mock)

@patch("survivorpy.data.get_table_names", return_value=["castaways"])
def test_load_invalid_table_raises_value_error(mock_get_names):
    with pytest.raises(ValueError, match="Unknown table: 'alliances'"):
        data.load("alliances")


# ----------------------
# Test: refresh_data
# ----------------------

@patch("survivorpy.data._has_cache", return_value=False)
@patch("survivorpy.data._update_last_synced")
@patch("survivorpy.data._cache_data_from_api")
@patch("survivorpy.data.get_last_synced", return_value="2024-01-01T00:00:00")
@patch("survivorpy.data._get_data_update_info")
def test_refresh_data_when_no_cache_triggers_download(
    mock_info, mock_synced, mock_cache, mock_update, mock_has_cache, capsys
):
    mock_info.return_value = {"timestamp": "2025-01-01T00:00:00"}

    data.refresh_data(verbose=True)
    captured = capsys.readouterr()
    assert "Local data cache was last synced on" in captured.out
    assert mock_cache.called
    assert mock_update.called


@patch("survivorpy.data._has_cache", return_value=True)
@patch("survivorpy.data.get_last_synced", return_value="2025-04-01T00:00:00")
@patch("survivorpy.data._get_data_update_info", return_value={"timestamp": "2025-04-01T00:00:00"})
def test_refresh_data_up_to_date_prints_message(mock_info, mock_synced, mock_has_cache, capsys):
    data.refresh_data(verbose=True)
    captured = capsys.readouterr()
    assert "Local data cache is already up to date." in captured.out


# ----------------------
# Test: _get_data_update_info
# ----------------------

@patch("requests.get")
def test_get_data_update_info_success(mock_get):
    test_dict = {
        "timestamp": "2025-01-01T00:00:00",
        "added": ["votes"],
        "modified": [],
        "deleted": [],
        "hashes": {"votes": "abc123"}  # should be ignored
    }
    encoded = base64.b64encode(str(test_dict).encode("utf-8")).decode("utf-8")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"content": encoded}

    result = data._get_data_update_info()
    assert "timestamp" in result
    assert "hashes" not in result
    assert result["added"] == ["votes"]

@patch("requests.get")
def test_get_data_update_info_bad_status(mock_get):
    mock_get.return_value.status_code = 500
    with pytest.raises(Exception, match="GitHub API request failed"):
        data._get_data_update_info()

@patch("requests.get")
def test_get_data_update_info_parse_error(mock_get):
    # invalid base64
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"content": "!!!bad_base64!!!"}

    with pytest.raises(Exception, match="Failed to parse GitHub API content"):
        data._get_data_update_info()
