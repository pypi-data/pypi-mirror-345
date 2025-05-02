import hgtk


def std(char: str):
    cho, jung, jong = hgtk.letter.decompose(char)
    if cho == "ㄹ" and jung in ["ㅑ", "ㅕ", "ㅛ", "ㅠ", "ㅣ", "ㅖ"]:
        return [char, hgtk.letter.compose("ㅇ", jung, jong)]

    elif cho == "ㄹ" and jung in ["ㅏ", "ㅐ", "ㅗ", "ㅜ", "ㅡ", "ㅚ"]:
        return [char, hgtk.letter.compose("ㄴ", jung, jong)]

    elif cho == "ㄴ" and jung in ["ㅕ", "ㅛ", "ㅠ", "ㅣ"]:
        return [char, hgtk.letter.compose("ㅇ", jung, jong)]

    else:
        return [char]
