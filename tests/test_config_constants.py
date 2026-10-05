"""Tests for config, constants, and repo hygiene."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_trading_days_constant() -> None:
    """Trading year has 252 days."""
    from app.constants import TRADING_DAYS_PER_YEAR

    assert TRADING_DAYS_PER_YEAR == 252


def test_logo_path_points_to_docs() -> None:
    """Logo lives under docs screenshots."""
    from app.constants import LOGO_PATH

    assert LOGO_PATH == 'docs/screenshots/B3_Logo.png'
    assert (ROOT / LOGO_PATH).exists()


def test_periods_and_defaults() -> None:
    """Periods and defaults are sane."""
    from app.config import PERIODS, STOCKS, STOCKS_DEFAULT
    from app.constants import DEFAULT_PERIOD, DEFAULT_STOCK

    assert DEFAULT_PERIOD in PERIODS
    assert DEFAULT_STOCK in STOCKS
    assert set(STOCKS_DEFAULT).issubset(set(STOCKS))
    assert len(STOCKS) >= 80


def test_quote_style_is_single() -> None:
    """Ruff uses single quotes."""
    text = (ROOT / 'pyproject.toml').read_text()
    assert "quote-style = 'single'" in text


def test_requirements_slim() -> None:
    """Runtime reqs are minimal."""
    lines = [
        line.strip()
        for line in (ROOT / 'requirements.txt').read_text().splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    assert len(lines) <= 10
    for lib in ['streamlit>=', 'pandas>=', 'numpy>=', 'yfinance', 'matplotlib', 'seaborn']:
        assert any(line.startswith(lib) for line in lines), lib
    assert not any('==' in line and 'altair' in line for line in lines)


def test_requirements_dev_has_pytest() -> None:
    """Dev reqs include test tools."""
    text = (ROOT / 'requirements-dev.txt').read_text()
    assert 'pytest' in text
    assert 'ruff' in text
    assert 'mypy' in text


def test_readme_uses_docs_screenshots() -> None:
    """README points to docs screenshots."""
    text = (ROOT / 'README.md').read_text()
    assert 'docs/screenshots/' in text
    assert 'images/' not in text


def test_no_stale_images_refs() -> None:
    """No code refs to images folder."""
    for path in [*(ROOT / 'app').rglob('*.py'), ROOT / 'pyproject.toml']:
        assert 'images/' not in path.read_text(), str(path)


def test_mypy_exclude_updated() -> None:
    """Mypy exclude uses docs not images."""
    text = (ROOT / 'pyproject.toml').read_text()
    assert 'images/' not in text
