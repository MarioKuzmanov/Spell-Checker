#!/usr/bin/env python3

import json
from collections import defaultdict


def cost(ch1, ch2, smoothing, counts=None):
    """ Given two aligned characters, return cost for ch1 -> ch2.

    This function should be called from the find_edits() function
    below when calculating costs for the edit operations.  If the
    first character is the empty string, it indicates an insert.
    Similarly, an empty string as the second character indicates a
    deletion.

    If `counts` is not given, the function should return 1 for all
    operations. if `counts` is given, you are strongly recommended to
    use estimated probability p of the edit operation from the given
    counts, and return `1 - p` as the cost (you should also consider
    using a smoothing technique). You are also welcome to
    experiment with other scoring functions.

    """
    # TODO
    if counts is None:
        return 1
    # smoothing factor = 1
    p = (counts[ch1][ch2] + smoothing) / (sum(counts[ch1].values()) + (len(counts[ch1]) * smoothing))
    return 1 - p


def find_edits(s1, s2, smoothing, counts=None):
    """ Find edits with minimum cost for given sequences.

    This function should implement the edit distance algorithm, using
    the scoring function above. If `counts` is given, the scoring
    should be based on the counts edits passed.

    The return value from this function should be a list of tuples.
    For example if the best alignment between correct word `work` and
    the misspelling `wrok` is as follows

                        wor-k
                        w-rok

    the return value should be
    [('w', 'w'), ('o', ''), ('r', 'r'), ('', o), ('k', 'k')].

    Parameters
    ---
    s1      The source sequences.
    s2      The target sequences.
    counts  A dictionary of dictionaries with counts of edit
            operations (see assignment description for more
            information and an example)
    """
    # TODO
    T = [[0 for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]

    for i in range(len(T)):
        T[i][0] = i
    for j in range(len(T[0])):
        T[0][j] = j

    for i in range(1, len(T)):
        ch1 = s1[i - 1]
        for j in range(1, len(T[i])):
            ch2 = s2[j - 1]
            if ch1 == ch2:
                T[i][j] = T[i - 1][j - 1]
            else:
                substitution = T[i - 1][j - 1] + cost(ch1, ch2, smoothing, counts)
                insertion = T[i][j - 1] + cost('', ch1, smoothing, counts)
                deletion = T[i - 1][j] + cost(ch1, '', smoothing, counts)
                T[i][j] = min(substitution, insertion, deletion)

    alignment = []
    i, j = len(T) - 1, len(T[0]) - 1
    while i > 0 or j > 0:
        ch1, ch2 = s1[i - 1], s2[j - 1]
        substitution, insertion, deletion = T[i - 1][j - 1], T[i][j - 1], T[i - 1][j]

        min_val = min(substitution, insertion, deletion)
        if substitution == min_val:
            alignment.append((ch1, ch2))
            i -= 1
            j -= 1
        elif insertion == min_val:
            alignment.append(('', ch1))
            j -= 1
        else:
            alignment.append((ch1, ''))
            i -= 1

    return list(reversed(alignment))


def count_edits(filename, smoothing, counts=None):
    """ Compute and return number of times pairs of letters aligned.

    This function should align each word and its misspelling in
    'filename' using find_edits(), and return the number of times each
    pair of letters are aligned as described in the assignment
    description.

    Parameters
    ---
    filename    A file containing (misspelling - word) pairs.
                One pair per line, pairs separated by tab.
    counts      If given, pass it to find_edits as initial counts.
                Do to updated it online (after each alignment).
    """
    # TODO
    count_alignments = defaultdict(dict)

    with open(filename, "rt", encoding="utf8") as f:
        lines = f.readlines()

    alphabet = {''}
    for line in lines:
        w1, w2 = line.strip().split('\t')
        alphabet = alphabet.union(set(w1 + w2))

    for let1 in alphabet:
        for let2 in alphabet:
            count_alignments[let1][let2] = 0

    for line in lines:
        misspelled, w = line.strip().split('\t')
        alignment = find_edits(s1=misspelled, s2=w, smoothing=smoothing, counts=counts)
        for ch1, ch2 in alignment:
            count_alignments[ch1][ch2] += 1
    return count_alignments


if __name__ == "__main__":
    ## The code below shows the intended use of your implementation above.

    counts = None
    counts_new = count_edits('spelling-data.txt', 1, counts)

    # target: around 11 iterations (Darja and Giulio)
    epochs = 0
    while counts != counts_new:
        counts = counts_new
        counts_new = count_edits('spelling-data.txt', 1, counts)
        epochs += 1

    print(f'epochs: {epochs}')

    with open('../spell-checker/spell-errors.json', 'wt') as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
