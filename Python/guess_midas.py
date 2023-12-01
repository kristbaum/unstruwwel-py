import re


def guess_midas(x, midas=False, verbose=True):
    count_slash = sum(1 for item in x if re.search(r"/", item)) / len(x)

    valid_dashes = "-|" + "|".join(chr(code) for code in range(0x2010, 0x2016))
    count_dash = sum(1 for item in x if re.search(valid_dashes, item)) / len(x)

    if count_dash - count_slash < -0.15 and not midas:
        if verbose:
            print(
                "Please check if input vector might have been standardized using MIDAS."
            )

    return midas
