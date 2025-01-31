#!/usr/bin/env python3


class FST:
    """A weighted FST class.
    """

    def __init__(self):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self._sigma_in = set()
        self._sigma_out = set()
        self._states = {0}

    @classmethod
    def fromfsa(cls, fsa):
        """Return an FST instance using an FSA.

        This method should take an instance of the FSA class defined
        in fsa.py, and returns an FST with identity transitions.
        """
        fst = cls()
        for (s1, sym), s2s in fsa.transitions.items():
            for s2 in s2s:
                fst.add_transition(s1, sym, s2, sym)
        fst.accepting = fsa.accepting
        fst.start_state = fsa.start_state
        return fst

    def mark_accepting(self, state):
        self.accepting.add(state)

    def get_transitions(self, s1, insym=None):
        """
        """
        if insym is None:
            syms = self._sigma_in
        else:
            syms = (insym,)
        for sym in syms:
            if (s1, sym) in self.transitions:
                for outsym, s2, w in self.transitions[(s1, sym)]:
                    yield s2, outsym, w

    def add_transition(self, s1, insym,
                       s2=None, outsym=None, w=0, accepting=False):
        """Add a transition from s1 to s2 with label insym:outsym.

        If s2 is None, create a new state. If outsym is None, assume
        identity transition.

        We assume transition labels are characters, and the states are
        integers, and we use integer labels when we create states.
        However, the code should (mostly) work fine with arbitrary labels.
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

    def move(self, s1, insym):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if (s1, insym) in self.transitions:
            return self.transitions[(s1, insym)]
        else:
            return set()

    def transduce(self, s):
        """ Transduce the string s, returning the result of the transduction.

        You do not need to handle epsilon loops (our FSTs do not have
        epsilon loops).

        Each result should be accompanied by the weight of the
        particular transduction of the input string. We calculate
        the weight of a path as the sum of the weights of the transitions
        in the path (this works well with log probabilities).

        Your method should preferably yield pairs of (output, weight)
        or return a sequence of such pairs.

        Tips:
            - You may find the _recognize_nfa method of the FSA class
              a useful starting point for implementing this method.
            - You will need to keep the output string built so far
              and its weight in your agenda so that you can use it
              when backtracking.
            - Unlike NFA recognition, we cannot stop as soon as we find
              an acceptable string. We want to generate all possible
              paths. 
        """
        # TODO
        generated = self.transitions.get((0, s[0]), set())
        rec_stack = []
        for sym, st, w in generated:
            rec_stack.append((sym, st, w, 1))

        while rec_stack:
            string, st, w, idx = rec_stack.pop()
            if idx < len(s):
                generated = self.transitions.get((st, s[idx]), set())
                for sym, st2, w2 in generated:
                    rec_stack.append((string + sym, st2, w + w2, idx + 1))
            else:
                print(string)

    def invert(self):
        """Invert the FST.
        """
        inverted_fst = FST()
        for (from_state, sym1), sigmas_out in self.transitions.items():
            for sym2, to_state, log_prob in sigmas_out:
                inverted_fst.add_transition(s1=from_state, insym=sym2, s2=to_state, outsym=sym1,
                                            w=log_prob)
        self.transitions = inverted_fst.transitions

    @classmethod
    def compose_fst(cls, m1, m2):
        """Compose two FST instances (m1 and m2) and return the composed FST.

        While implementing this method, you should pay attention to
        epsilons, since our use case requires epsilon transitions.
        However, you can make use of the fact that `m1` does not
        include any epsilon transitions in our application. Also,
        since `m1` in our application is not weighted, the arc weight
        can trivially be taken from `m2`.
        """
        # TODO

        # m3 = FST()
        # for (from_state, sym1), sigmas_out in m1.transitions.items():
        #     for sym2, to_state, _ in sigmas_out:
        #         for (from_state2, sym12), sigmas_out2 in m2.transitions.items():
        #             if sym2 == sym12:
        #                 for sym22, to_state2, w2 in sigmas_out2:
        #                     st1 = int(str(from_state) + str(from_state2))
        #                     st2 = int(str(to_state) + str(to_state2))
        #                     m3._states.add(st1)
        #                     m3._states.add(st2)
        #
        #                     if from_state in m1.accepting and from_state2 in m2.accepting:
        #                         m3.accepting.add(st1)
        #                     if to_state in m1.accepting and to_state2 in m2.accepting:
        #                         m3.accepting.add(st2)
        #                     m3.add_transition(st1, sym2, st2, sym22, w2)
        # return m3
