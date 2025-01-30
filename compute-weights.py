#!/usr/bin/env python3

import json
from collections import defaultdict
import numpy as np


def cost(ch1, ch2, counts=None):
    if counts is None:
        return 1
    p = (counts[ch1][ch2] + 0.05) / (sum(counts[ch1].values()) + (len(counts[ch1]) * 0.05))
    return 1 - p


def find_edits(s1, s2, counts=None):
    # edit-distance table
    T = np.full((len(s1) + 1, len(s2) + 1), 0.0)

    # fill first row
    for j in range(len(T[0])):
        T[0][j] = j

    # and column
    for i in range(len(T)):
        T[i][0] = i

    # fill table
    for i in range(1, len(T)):
        ch1 = s1[i - 1]
        for j in range(1, len(T[i])):
            ch2 = s2[j - 1]
            if ch1 == ch2:
                T[i][j] = T[i - 1][j - 1]
            else:
                substitution = T[i - 1][j - 1] + cost(ch1, ch2, counts)
                insertion = T[i][j - 1] + cost('', ch1, counts)
                deletion = T[i - 1][j] + cost(ch1, '', counts)
                T[i][j] = min(substitution, insertion, deletion)
    # the alignment is a traceback of the path, that lead us to the min. edit distance
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


def count_edits(filename, counts=None):
    count_alignments = defaultdict(dict)

    # read the file
    with open(filename, "rt", encoding="utf8") as f:
        lines = f.readlines()

    # pre-process
    alphabet = {''}
    pairs = []
    for line in lines:
        w1, w2 = line.strip().split('\t')
        w1, w2 = w1.lower(), w2.lower()
        pairs.append((w1, w2))

        alphabet = alphabet.union(set((w1 + w2)))

    # init. new spelling counts
    for let1 in alphabet:
        for let2 in alphabet:
            count_alignments[let1][let2] = 0

    # find new more precise alignments
    for w1, w2 in pairs:
        alignment = find_edits(s1=w1, s2=w2, counts=counts)
        for ch1, ch2 in alignment:
            count_alignments[ch1][ch2] += 1
    return count_alignments


if __name__ == "__main__":
    counts = None
    counts_new = count_edits('train_data/spelling-data.txt', counts)

    # estimate spelling error counts
    epochs = 1
    while counts != counts_new:
        counts = counts_new
        counts_new = count_edits('train_data/spelling-data.txt', counts)
        epochs += 1

    print(f'Counts estimated!\n'
          f'Epochs: {epochs}')

    # save the file, use later to give weights
    with open('spell-errors.json', 'wt') as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
