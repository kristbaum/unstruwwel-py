import pytest

from unstruwwel_py.lang import guess_language


@pytest.mark.parametrize("lang", ["en", "de", "fr"])
def test_guess_language_single(lang, lang_jsons):
    # Use words from the language json
    data = lang_jsons[lang]
    sample_vals = []
    for key in ("century", "january", "before"):
        if key in data:
            sample_vals.extend(data[key])
    assert guess_language(sample_vals, verbose=False) == lang


def test_guess_language_multiple(lang_jsons):
    # Create a mixed sample to trigger multiple
    en = lang_jsons["en"]["century"][:2]
    fr = lang_jsons["fr"]["century"][:1]
    x = en + fr
    res = guess_language(x, verbose=False)
    assert set(res) >= {"fr", "en"}


def test_guess_language_none():
    if hasattr(__builtins__, "__IPYTHON__") and __builtins__.__IPYTHON__:
        pytest.skip("Session is interactive.")
    with pytest.raises(Exception):
        guess_language([str(i) for i in range(1750, 1901)], verbose=False)


def test_guess_language_message(lang_jsons, capsys):
    data = lang_jsons["de"]["century"]
    guess_language(data, verbose=True)
    captured = capsys.readouterr()
    assert captured.out
