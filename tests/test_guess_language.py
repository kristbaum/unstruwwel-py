import pytest

from unstruwwel import guess_language


def test_guess_german(german_dates):
    assert guess_language(german_dates, verbose=False) == ["de"]


def test_guess_french(french_dates):
    assert guess_language(french_dates, verbose=False) == ["fr"]


def test_guess_english(english_dates):
    assert guess_language(english_dates, verbose=False) == ["en"]


def test_guess_none():
    # purely numeric input carries no language signal
    with pytest.raises(ValueError):
        guess_language([str(y) for y in range(1750, 1900)], verbose=False)


def test_show_message(german_dates, capsys):
    guess_language(german_dates, verbose=True)
    out = capsys.readouterr().out
    assert "detected" in out


def test_detection_via_unstruwwel(german_dates):
    from unstruwwel import unstruwwel

    sample = [d for d in german_dates if "Jahrhundert" in d][:5]
    # language=None triggers automatic detection
    result = unstruwwel(sample, language=None)
    assert len(result) == len(sample)
