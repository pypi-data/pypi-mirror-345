import pytest
import json
import base64
import pandas as pd
from pathlib import Path
from io import BytesIO
from unittest.mock import patch, MagicMock, mock_open
from survivorpy import sync

# ----------------------
# Test: _has_cache
# ----------------------

@patch("survivorpy.sync._CACHE_DIR")
@patch("survivorpy.sync._CACHE_DATA_DIR")
@patch("survivorpy.sync._CACHE_TABLE_NAMES_PATH")
@patch("survivorpy.sync._CACHE_LAST_SYNCED_PATH")
def test_has_cache(mock_last_synced_path, mock_table_names_path, mock_cache_data_dir, mock_cache_dir):
    # Case 1: Cache is set up properly
    mock_cache_dir.exists.return_value = True
    mock_cache_dir.is_dir.return_value = True
    mock_cache_data_dir.exists.return_value = True
    mock_cache_data_dir.is_dir.return_value = True
    mock_cache_data_dir.iterdir.return_value = [Path("fake_file")]  # Non-empty directory
    mock_table_names_path.exists.return_value = True
    mock_table_names_path.is_file.return_value = True
    mock_last_synced_path.exists.return_value = True
    mock_last_synced_path.is_file.return_value = True

    assert sync._has_cache() is True

    # Case 2: _CACHE_DIR does not exist
    mock_cache_dir.exists.return_value = False
    assert sync._has_cache() is False
    mock_cache_dir.exists.return_value = True

    # Case 3: _CACHE_DIR is not a directory
    mock_cache_dir.is_dir.return_value = False
    assert sync._has_cache() is False
    mock_cache_dir.is_dir.return_value = True

    # Case 4: _CACHE_DATA_DIR is empty
    mock_cache_data_dir.iterdir.return_value = []
    assert sync._has_cache() is False
    mock_cache_data_dir.iterdir.return_value = [Path("fake_file")]

    # Case 5: _CACHE_TABLE_NAMES_PATH does not exist
    mock_table_names_path.exists.return_value = False
    assert sync._has_cache() is False
    mock_table_names_path.exists.return_value = True

    # Case 6: _CACHE_LAST_SYNCED_PATH does not exist
    mock_last_synced_path.exists.return_value = False
    assert sync._has_cache() is False
    mock_last_synced_path.exists.return_value = True

# ------------------------------
# Test: _update_last_synced
# ------------------------------

@patch("builtins.open", new_callable=mock_open)
@patch("survivorpy.sync.datetime")
def test_update_last_synced_writes_json(mock_datetime, mock_open_file):
    mock_datetime.utcnow.return_value.isoformat.return_value = "2024-01-01T00:00:00"

    with patch("survivorpy.sync._CACHE_LAST_SYNCED_PATH", Path("/tmp/last_synced.json")):
        sync._update_last_synced()

    handle = mock_open_file()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    assert written == '{"timestamp": "2024-01-01T00:00:00Z"}'

# --------------------------------------
# Test: _cache_data_from_api (Success)
# --------------------------------------

@patch("survivorpy.sync.requests.post")
@patch("survivorpy.sync._CACHE_DATA_DIR")
@patch("survivorpy.sync._CACHE_TABLE_NAMES_PATH")
@patch("survivorpy.sync.zipfile.ZipFile")
@patch("builtins.open", new_callable=mock_open)
def test_cache_data_from_api_success(mock_open_file, mock_zipfile_cls, mock_table_names_path, mock_data_dir, mock_post):
    # Simulate successful API response with base64-encoded zip
    fake_zip_content = b"Fake zipped content"
    encoded_content = base64.b64encode(fake_zip_content).decode("utf-8")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = encoded_content
    mock_post.return_value = mock_response

    # Mock zipfile behavior
    fake_zip = MagicMock()
    fake_zip.namelist.return_value = ["one.parquet", "two.parquet"]
    mock_zipfile_cls.return_value.__enter__.return_value = fake_zip

    sync._cache_data_from_api()

    # Confirm API was called
    mock_post.assert_called_once_with(sync._RATE_LIMITED_API_URL)

    # Confirm zip was decoded and extracted
    mock_zipfile_cls.assert_called_once()
    fake_zip.extractall.assert_called_once_with(mock_data_dir)

    # Confirm table names were written correctly
    handle = mock_open_file()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    assert json.loads(written) == ["one", "two"]

# ---------------------------------------------
# Test: _cache_data_from_api (Rate Limited 429)
# ---------------------------------------------

@patch("survivorpy.sync.requests.post")
def test_cache_data_from_api_rate_limit(mock_post):
    mock_post.return_value.status_code = 429
    mock_post.return_value.json.return_value = {"message": "Rate limit exceeded"}

    with pytest.raises(Exception, match="Rate limit exceeded"):
        sync._cache_data_from_api()

# ---------------------------------------------------
# Test: _cache_data_from_api (Other HTTP Error 500)
# ---------------------------------------------------

@patch("survivorpy.sync.requests.post")
def test_cache_data_from_api_other_http_error(mock_post):
    mock_post.return_value.status_code = 500

    with pytest.raises(Exception, match="API call failed with status code 500"):
        sync._cache_data_from_api()
