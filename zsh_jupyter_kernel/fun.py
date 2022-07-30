def find_word_at_pos(text : str, pos : int) -> str:
    cw = ""
    p = 0
    ic = '\n\t"' + r" |;,!@#$()<>/\'`~{}[]=+&^"

    while p < pos:
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

def get_canonical_dirname(filename: str) -> str | None:
    """
    :return: return the canonical path of the specified filename, eliminating any symbolic links encountered in the path
        (if they are supported by the operating system). if a path doesn’t exist or a symlink loop is encountered then
        return None.
    """
    from os.path import dirname
    from os.path import realpath

    return dirname(realpath(filename, strict = True))
