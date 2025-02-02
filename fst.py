class FST:
    """
    A weighted FST class
    """

    def __init__(self):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self._sigma_in = set()
        self._sigma_out = set()
        self._states = set()

    @classmethod
    def fromfsa(cls, fsa):
        """
        Return an FST with identity transitions using an FSA.
        """
        fst = cls()
        for (s1, sym), s2s in fsa.transitions.items():
            for s2 in s2s:
                fst.add_transition(s1, sym, s2, sym)
        fst.accepting = fsa.accepting
        fst.start_state = fsa.start_state
        return fst

    def get_transitions(self, s1, insym=None):
        """
        Yields all transitions based on the input.
        """
        if insym is None:
            syms = self._sigma_in
        else:
            syms = (insym,)
        for sym in syms:
            if (s1, sym) in self.transitions:
                for outsym, s2, w in self.transitions[(s1, sym)]:
                    yield outsym, s2, w

    def add_transition(self, s1, insym, s2=None, outsym=None, w=0, accepting=False):
        """
        Add a transition from s1 to s2 with label insym:outsym.

        If s2 is None, create a new state. If outsym is None, assume
        identity transition.
        """

        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        if s2 not in self._states:
            self._states.add(s2)
        if outsym is None: outsym = insym
        self._sigma_in.add(insym)
        self._sigma_out.add(outsym)
        if (s1, insym) not in self.transitions:
            self.transitions[(s1, insym)] = set()
        self.transitions[s1, insym].add((outsym, s2, w))
        if accepting:
            self.accepting.add(s2)
        return s2

    def transduce(self, s):
        """
        Transduce the string s, returning all possible candidates after the transduction.

        Each result is accompanied by the weight of the
        particular transduction of the input string. It is
        the weight of a path as the sum of the weights of the transitions
        in the path, assuming log probabilities.

        Yields pairs of (output, weight)
        """

        initsymbol = list(self.get_transitions(self.start_state, s[0]))
        initepsilon = list(self.get_transitions(self.start_state, ""))

        transducer = []
        for sym, st, log_prob in initsymbol:
            transducer.append((sym, st, log_prob, 1))
        for sym, st, log_prob in initepsilon:
            transducer.append((sym, st, log_prob, 0))

        unique = set()
        while transducer:
            string, st, w, idx = transducer.pop()
            if (string, st, idx) not in unique:
                unique.add((string, st, idx))
                if idx < len(s):
                    nextsymbol = list(self.get_transitions(st, s[idx]))
                    nextepsilon = list(self.get_transitions(st, ""))

                    for sym, to_state, log_prob in nextsymbol:
                        transducer.append((string + sym, to_state, w + log_prob, idx + 1))

                    for sym, to_state, log_prob in nextepsilon:
                        transducer.append((string + sym, to_state, w + log_prob, idx))
                else:
                    if string != s and st in self.accepting:
                        yield string, 10 ** w

    def invert(self):
        """
        Invert the FST
        """
        inverted_fst = FST()
        for (from_state, sym1), sigmas_out in self.transitions.items():
            for sym2, to_state, log_prob in sigmas_out:
                inverted_fst.add_transition(s1=from_state, insym=sym2, s2=to_state, outsym=sym1,
                                            w=log_prob)
        self.transitions = inverted_fst.transitions

    @classmethod
    def compose_fst(cls, m1, m2):
        """
        Composes two FST instances (m1 and m2) and returns the composed FST.

        While implementing this method, you should pay attention to
        epsilons, since our use case requires epsilon transitions.

       `m1` does not include any epsilon transitions in our application.
        Also, since `m1` in our application is not weighted, the arc weight
        can trivially be taken from `m2`.

        """
        for state in m1._states:
            m1.add_transition(s1=state, insym="", s2=state, outsym="")

        m3 = FST()
        for (from_state, in_sym), sigmas_out in m1.transitions.items():
            for (out_sym, to_state, _) in sigmas_out:
                for (from_state2, in_sym2), sigmas_out2 in m2.transitions.items():
                    if out_sym == in_sym2:
                        for (out_sym2, to_state2, log_prob) in sigmas_out2:
                            st1 = int(str(from_state) + str(from_state2))
                            st2 = int(str(to_state) + str(to_state2))

                            if from_state in m1.accepting and from_state2 in m2.accepting:
                                m3.accepting.add(st1)
                            if to_state in m1.accepting and to_state2 in m2.accepting:
                                m3.accepting.add(st2)

                            m3.add_transition(s1=st1, insym=in_sym, s2=st2, outsym=out_sym2, w=log_prob)

        return m3


if __name__ == "__main__":
    import json
    from fsa import FSA
    from spell_fst import Spell_Checker

    # draft of the pipeline, useful for testing
    with open("data/lexicon.txt", 'rt', encoding="utf8") as f:
        words = f.read().strip().split()
        alphabet = sorted(set("".join(words))) + [""]

    with open("data/spell-errors.json", 'rt', encoding='utf8') as f:
        errcount = json.loads(f.read())

    fsa = FSA(deterministic=True)
    fsa.build_trie(words)
    # fsa.minimize()

    lexicon = FST.fromfsa(fsa)
    edits = Spell_Checker.build_editfst(alphabet, errcount)

    spellfst = FST.compose_fst(lexicon, edits)
    spellfst.invert()

    inword = "gras"
    corrections = sorted(spellfst.transduce(inword), key=lambda x: x[1], reverse=True)[: 10]

    print(f'entered word: {inword}')
    print('candidate corrections...')
    for idx, (w, prob) in enumerate(corrections):
        print(f'{idx + 1}. {w} ~ {prob}')
