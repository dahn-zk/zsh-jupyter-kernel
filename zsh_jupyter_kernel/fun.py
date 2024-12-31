def find_word_at_pos(text : str, pos : int) -> str:
    cw = ""
    p = 0
    ic = '\n\t"' + r" |;,!@#$()<>/\'`~{}[]=+&^"

    while p < len(text) and p < pos:
        c = text[p]
        if c in ic:
            cw = ""
        else:
            cw += c
        p += 1

    while p < len(text):
        c = text[p]
        if c in ic:
            break
        else:
            cw += c
        p += 1

    return cw
