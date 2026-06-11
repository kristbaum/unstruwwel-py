from unstruwwel import guess_midas


def test_guess_false(german_dates):
    # plain verbal dates are not MIDAS-standardized
    assert guess_midas(german_dates, verbose=False) is False


def test_midas_flag_is_returned():
    assert guess_midas(["1900-01-01/1900-12-31"], midas=True, verbose=False) is True


def test_warns_on_slash_heavy_input(capsys):
    midas_like = ["1801/1850"] * 20
    guess_midas(midas_like, verbose=True)
    out = capsys.readouterr().out
    assert "MIDAS" in out
