import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------
# Test: __getattr__ returns table when valid
# ---------------------------------------------

@patch("survivorpy.get_table_names", return_value=["castaways", "seasons"])
@patch("survivorpy.load", return_value="MOCK")
def test_getattr_returns_table(mock_load, mock_tables):
    import survivorpy
    assert survivorpy.castaways == "MOCK"
    assert survivorpy.seasons == "MOCK"

# -----------------------------------------------------
# Test: __getattr__ raises AttributeError when invalid
# -----------------------------------------------------

@patch("survivorpy.get_table_names", return_value=["castaways"])
def test_getattr_invalid_table_raises(mock_tables):
    import survivorpy
    with pytest.raises(AttributeError, match="module 'survivorpy' has no attribute 'invalid_name'"):
        _ = survivorpy.invalid_name

# -----------------------------------------------------------
# Test: refresh_data() is not called if cache already exists
# -----------------------------------------------------------

@patch("survivorpy.get_last_synced", return_value="2025-05-03")
@patch("survivorpy.get_table_names", return_value=["castaways"])
@patch("survivorpy._has_cache", return_value=True)
@patch("survivorpy.refresh_data")
def test_no_refresh_if_cache_exists(mock_refresh, mock_cache, *_):
    import importlib
    import survivorpy
    importlib.reload(survivorpy)
    mock_refresh.assert_not_called()
