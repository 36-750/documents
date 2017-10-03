import numpy as np


def edit_distance(s1, s2):
    """Computes the edit distance between two strings

    Parameters s1 and s2 are strings.

    Returns the edit distance, a non-negative integer, between the strings.

    """
    len1 = len(s1)
    len2 = len(s2)
    edit = np.full((len1 + 1, len2 + 1), np.inf)

    edit[:, 0] = np.arange(len1 + 1)
    edit[0, :] = np.arange(len2 + 1)

    for index1 in range(1, len1 + 1):
        for index2 in range(1, len2 + 1):
            # ATTN:FIX
            edit[index1, index2] = np.inf  # ATTN:FIX
    edit = edit.astype(int)
    return edit[len1, len2]


def gaps(gap_length):
    return "_" * gap_length


def edit_alignment(s1, s2):
    """Computes the alignment and edit distance between two strings

    Parameters s1 and s2 are strings.

    Returns a 3-tuple containing the the edit distance, the first string
    with alignment characters _ included, and the second string with alignment
    characters included.

    """
    len1 = len(s1)
    len2 = len(s2)

    edit = np.full((len1 + 1, len2 + 1), np.inf)
    edit[:, 0] = np.arange(len1 + 1)
    edit[0, :] = np.arange(len2 + 1)

    align = np.full((len1 + 1, len2 + 1, 2), '', dtype=object)

    for i in range(1, len1 + 1):
        align[i, 0, 0] = "NA"  # ATTN:FIX
        align[i, 0, 1] = gaps(i)

    for j in range(1, len2 + 1):
        align[0, j, 0] = "NA"  # ATTN:FIX
        align[0, j, 1] = "NA"  # ATTN:FIX

    for index1 in range(1, len1 + 1):
        for index2 in range(1, len2 + 1):
            # ATTN:FIX
            edit[index1, index2] = np.inf  # ATTN:FIX

            if True:
                align[index1, index2, 0] = "NA"  # ATTN:FIX
                align[index1, index2, 1] = "NA"  # ATTN:FIX
            elif True:
                align[index1, index2, 0] = "NA"  # ATTN:FIX
                align[index1, index2, 1] = "NA"  # ATTN:FIX
            else:
                align[index1, index2, 0] = "NA"  # ATTN:FIX
                align[index1, index2, 1] = "NA"  # ATTN:FIX
    edit = edit.astype(int)
    return (edit[len1, len2], align[len1, len2, 0], align[len1, len2, 1])
