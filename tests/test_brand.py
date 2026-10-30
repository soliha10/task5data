import re
import tomllib
from pathlib import Path
import pytest
from mining import brand

ROOT = Path(__file__).resolve().parent.parent
CONFIG = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text())
HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{6}\b")
BRAND_MODULE = ROOT / "mining" / "brand.py"
AA_TEXT = 4.5
AA_GRAPHICS = 3.0
TEXT_PAIRS = {
    "body text on page": (brand.TEXT, brand.WHITE),
    "secondary text on page": (brand.TEXT_BODY, brand.WHITE),
    "muted text on page": (brand.TEXT_MUTED, brand.WHITE),
    "muted text on sidebar": (brand.TEXT_MUTED_ON_TINT, brand.SUBTLE_BACKGROUND),
    "PDF KPI label": (brand.TEXT_MUTED_ON_TINT, brand.SUBTLE_BACKGROUND),
    "sidebar heading": (brand.PRIMARY_800, brand.SUBTLE_BACKGROUND),
    "brand line, active tab, link": (brand.ACTION, brand.WHITE),
    "primary button label": (brand.WHITE, brand.ACTION),
    "primary button hover label": (brand.WHITE, brand.ACTION_HOVER),
    "secondary button hover label": (brand.ACTION_HOVER, brand.SUBTLE_BACKGROUND),
    "live badge": (brand.PRIMARY_800, brand.SUBTLE_ACCENT),
    "table header": (brand.BRAND_DARK, brand.SUBTLE_BACKGROUND),
    "PDF table header": (brand.WHITE, brand.BRAND_DARK),
    "PDF spike banner": (brand.WHITE, brand.SPIKE),
    "PDF drop banner": (brand.TEXT, brand.DROP),
}
GRAPHIC_PAIRS = {
    "metric accent bar": (brand.ACTION, brand.WHITE),
    "spike marker": (brand.SPIKE, brand.WHITE),
    "drop marker outline": (brand.DROP_OUTLINE, brand.WHITE),
    "total series": (brand.BRAND_DARK, brand.WHITE),
}

def _relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)

@pytest.mark.parametrize("name", TEXT_PAIRS)
def test_text_pairs_meet_wcag_aa(name):
    assert contrast_ratio(*TEXT_PAIRS[name]) >= AA_TEXT

@pytest.mark.parametrize("name", GRAPHIC_PAIRS)
def test_graphic_pairs_meet_wcag_aa(name):
    assert contrast_ratio(*GRAPHIC_PAIRS[name]) >= AA_GRAPHICS

def test_streamlit_theme_mirrors_brand_tokens():
    theme, sidebar = CONFIG["theme"], CONFIG["theme"]["sidebar"]
    assert theme["primaryColor"] == brand.ACTION
    assert theme["linkColor"] == brand.ACTION
    assert theme["backgroundColor"] == brand.WHITE
    assert theme["secondaryBackgroundColor"] == brand.SURFACE
    assert theme["textColor"] == brand.TEXT
    assert theme["borderColor"] == brand.BORDER
    assert theme["dataframeBorderColor"] == brand.BORDER
    assert theme["dataframeHeaderBackgroundColor"] == brand.SUBTLE_BACKGROUND
    assert theme["dataframeHeaderTextColor"] == brand.BRAND_DARK
    assert theme["chartCategoricalColors"] == brand.CATEGORICAL
    assert theme["font"] == theme["headingFont"] == f"{brand.FONT_NAME}:{brand.FONT_URL}"
    assert theme["baseRadius"] == f"{brand.RADIUS_PX}px"
    assert theme["buttonRadius"] == f"{brand.RADIUS_SMALL_PX}px"
    assert sidebar["backgroundColor"] == brand.SUBTLE_BACKGROUND
    assert sidebar["secondaryBackgroundColor"] == brand.WHITE
    assert sidebar["textColor"] == brand.TEXT

def test_hex_colours_live_only_in_brand_module():
    sources = [*ROOT.joinpath("mining").rglob("*.py"), *ROOT.joinpath("ui").rglob("*.py")]
    offenders = [
        path.relative_to(ROOT)
        for path in [*sources, ROOT / "app.py"]
        if path != BRAND_MODULE and HEX_COLOUR.search(path.read_text())
    ]
    assert offenders == []

def test_mine_palette_is_distinct_from_brand_and_semantic_colours():
    reserved = {brand.ACTION, brand.BRAND_DARK, brand.SPIKE, brand.DROP}
    assert reserved.isdisjoint(brand.CATEGORICAL)
    assert len(set(brand.CATEGORICAL)) == len(brand.CATEGORICAL)
