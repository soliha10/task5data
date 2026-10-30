import pytest
from mining.data import TOTAL, extract_sheet_id, mine_columns, parse_mine_output, series_label

SHEET_CSV = (
    '"Date","LV-426","Origae-6","","","Total"\n'
    '"11/2/2099","54.1","47.4","","","999"\n'
    '"11/3/2099","58.5","34.7","","","999"\n'
)

def test_extract_sheet_id_accepts_url_and_bare_id():
    url = "https://docs.google.com/spreadsheets/d/abc_123-XYZ/edit?gid=0"
    assert extract_sheet_id(url) == "abc_123-XYZ"
    assert extract_sheet_id("  abc_123-XYZ ") == "abc_123-XYZ"

def test_parse_mine_output_drops_empty_slots_and_recomputes_total():
    output = parse_mine_output(SHEET_CSV)
    assert mine_columns(output) == ["LV-426", "Origae-6"]
    assert output[TOTAL].tolist() == pytest.approx([101.5, 93.2])
    assert str(output.index[0].date()) == "2099-11-02"

def test_parse_mine_output_requires_date_column():
    with pytest.raises(ValueError, match="Date"):
        parse_mine_output('"Day","LV-426"\n"1","2"\n')

def test_series_label_names_total():
    assert series_label(TOTAL) == "Total (all mines)"
    assert series_label("LV-426") == "LV-426"
