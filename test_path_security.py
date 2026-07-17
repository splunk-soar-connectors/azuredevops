from pathlib import Path


CONNECTOR_SOURCE = Path("azuredevops_connector.py").read_text()


def test_string_identifiers_are_encoded_as_path_segments():
    assert 'urlparse.quote(str(value), safe="")' in CONNECTOR_SOURCE
    assert "team=_quote_path_segment(team)" in CONNECTOR_SOURCE
    assert 'work_item_type = _quote_path_segment(param["work_item_type"])' in CONNECTOR_SOURCE
    assert 'user_id = _quote_path_segment(param["user_id"])' in CONNECTOR_SOURCE


def test_work_item_ids_are_coerced_to_integers_before_use():
    assert CONNECTOR_SOURCE.count('_parse_work_item_id(param["work_item_id"], action_result)') == 2
    assert "Work item ID must be an integer" in CONNECTOR_SOURCE
