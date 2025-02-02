import json
from collections import defaultdict
import numpy as np


class Edits:
    def __init__(self, filename, counts=None):
        # goal: find the min. edit distance between two words
        self.filename = filename
        self.counts = counts

    def _cost(self, ch1, ch2):
        if self.counts is None:
            return 1
        p = (self.counts[ch1][ch2] + 0.05) / (sum(self.counts[ch1].values()) + (len(self.counts[ch1]) * 0.05))
        return 1 - p

    def find_edits(self, s1, s2):
        """

        Returns: The best alignment between two words, according to the Levenshtein edit distance algorithm.
        The implementation is traditional, however the cost change with respect to the frequencies of edit operations.
        We want smaller penalties for frequent edits and larger for rare ones.

        """
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
                    substitution = T[i - 1][j - 1] + self._cost(ch1, ch2)
                    insertion = T[i][j - 1] + self._cost("", ch1)
                    deletion = T[i - 1][j] + self._cost(ch1, "")
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

    def count_edits(self):
        count_alignments = defaultdict(dict)

        # read the file
        with open(self.filename, "rt", encoding="utf8") as f:
            lines = f.readlines()

        # pre-process
        alphabet = {""}
        pairs = []
        for line in lines:
            w1, w2 = line.strip().split('\t')
            w1, w2 = w1.lower(), w2.lower()
            pairs.append((w1, w2))

            combined = w1 + w2
            for let in combined:
                alphabet.add(let)

        # init. new spelling counts
        for let1 in alphabet:
            for let2 in alphabet:
                count_alignments[let1][let2] = 0

        # find new more precise alignments
        for w1, w2 in pairs:
            alignment = self.find_edits(s1=w1, s2=w2)
            for ch1, ch2 in alignment:
                count_alignments[ch1][ch2] += 1
        return count_alignments


if __name__ == "__main__":
    counts = None
    edits = Edits(filename="data/spelling-data.txt", counts=counts)
    counts_new = edits.count_edits()

    # estimate spelling error counts
    epochs = 1
    while counts != counts_new:
        counts = counts_new
        edits.counts = counts
        counts_new = edits.count_edits()
        epochs += 1

    print(f'counts estimated...\n'
          f'Epochs: {epochs}')

    # save the file, use later to give weights
    with open('data/spell-errors.json', 'wt') as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
