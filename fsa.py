#!/usr/bin/env python3
"""
The template for this part can be found in fsa.py.
You are already given a rudimentary implementation of a finite-state automata class.
You need to implement two functions/methods:

build_trie() which takes a list of words and returns a trie (an instance of the FSA class)
that recognizes all (and the only) words in the list.

minimize() method of the FSA class, which minimizes the FSA in place if it is not minimal.
You can use any of the minimization methods discussed in the class.
"""

from collections import defaultdict


class FSA:
    """ A class representing finite state automata.
    Args:
        deterministic: The automaton is deterministic
    Attributes:
        transitions: transitions kept as a dictionary
            where keys are the tuple (source_state, symbol),
            values are the target state for DFA
            and a set of target states for NFA.
            Note that we do not require a dedicated 'sink' state.
            Any undefined transition should cause the FSA to reject the
            string immediately.
        start_state: number/name of the start state
        accepting: the set of accepting states
        is_deterministic (boolean): whether the FSA is deterministic or not
    """

    def __init__(self, deterministic=True):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self.is_deterministic = deterministic
        self._alphabet = set()  # just for convenience, we can
        self._states = set()  # always read it off from transitions

    def add_transition(self, s1, sym, s2=None, accepting=False):
        """ Add a transition from state s1 to s2 with symbol
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        self._states.add(s2)
        self._alphabet.add(sym)
        if (s1, sym) not in self.transitions:
            self.transitions[(s1, sym)] = set()
        self.transitions[(s1, sym)].add(s2)
        if accepting:
            self.accepting.add(s2)
        if len(self.transitions[(s1, sym)]) > 1:
            self.deterministic = False
        return s2

    def mark_accept(self, state):
        self.accepting.add(state)

    def is_accepting(self, state):
        return state in self.accepting

    def move(self, sym, s1=None):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if s1 is None: s1 = self.start_state
        if (s1, sym) not in self.transitions:
            return None
        else:
            return self.transitions[(s1, sym)]

    def _recognize_dfa(self, s):
        state = self.start_state
        for sym in s:
            states = self.transitions.get((state, sym), None)
            if states is None:
                return False
            else:
                state = next(iter(states))
        if state in self.accepting:
            return True
        else:
            return False

    def _recognize_nfa(self, s):
        """ NFA recognition of 's' using a stack-based agenda.
        """
        agenda = []
        state = self.start_state
        inp_pos = 0
        for node in self.transitions.get((self.start_state, s[inp_pos]), []):
            agenda.append((node, inp_pos + 1))

        while agenda:
            node, inp_pos = agenda.pop()
            if inp_pos == len(s):
                if node in self.accepting:
                    return True
            else:
                for node in self.transitions.get((node, s[inp_pos]), []):
                    agenda.append((node, inp_pos + 1))
        return False

    def recognize(self, s):
        """ Recognize the given string 's', return a boolean value
        """
        if self.is_deterministic:
            return self._recognize_dfa(s)
        else:
            return self._recognize_nfa(s)

    @staticmethod
    def get_position(partitions):
        state_positions = {}
        for idx, partition in enumerate(partitions):
            for state in partition:
                state_positions[state] = idx
        return state_positions

    def minimize(self):
        """ Minimize the automaton.

        You are free to use any of the minimization algorithms here.
        """
        # TODO
        # minimization by partitioning
        # partition states into different subsets as long there is a change
        partitions, prev = [self._states - self.accepting, self.accepting], None
        while prev != partitions:
            prev = partitions
            state_positions = FSA.get_position(partitions)
            next_partitions = []
            for partition in partitions:
                merger = defaultdict(set)
                for st in partition:
                    lst_tr = []
                    for (s, sym), st2 in self.transitions.items():
                        if st == s:
                            tr = (sym, state_positions[next(iter(st2))])
                            lst_tr.append(tr)
                    merger[tuple(lst_tr)].add(st)
                next_partitions.extend(list(merger.values()))
            partitions = next_partitions

        # the states of the minimized automaton
        fsa_minimized = FSA(deterministic=True)
        state_positions = FSA.get_position(partitions)
        for (st, sym), st2 in self.transitions.items():
            st2 = next(iter(st2))
            fsa_minimized.add_transition(state_positions[st], sym, state_positions[st2], self.is_accepting(st2))

        # in-place
        self.transitions = fsa_minimized.transitions
        self._states = fsa_minimized._states
        self.accepting = fsa_minimized.accepting


def build_trie(words):
    """Given a list of words, create and return a trie FSA.

    For the given sequence of words, you should build a trie,
    an FSA where letters are the edge labels. Since the structure is a
    trie, common prefix paths should be shared but suffixes will
    necessarily use many redundant paths.

    You should initialize an instance of the FSA class defined above,
    and add only the required arcs successively. 
    """
    # TODO
    fsa = FSA(deterministic=True)

    transitions = {(i, words[0][i]): i + 1 for i in range(len(words[0]))}
    prev_end = len(words[0])
    state_accepting = {prev_end}
    for i in range(1, len(words)):
        w, last_state = words[i], None
        start = 0
        for j in range(len(w)):
            let = w[j]
            if (start, let) in transitions:
                start = transitions[(start, let)]
                continue
            else:
                transitions.update({(start, let): prev_end + 1})
                start = prev_end + 1
                prev_end += 1
                last_state = start
        state_accepting.add(last_state)

    for k, sym2 in transitions.items():
        sym1, let = k
        if sym2 in state_accepting:
            fsa.add_transition(sym1, let, sym2, accepting=True)
        else:
            fsa.add_transition(sym1, let, sym2, accepting=False)
    return fsa


if __name__ == '__main__':
    # Example usage:
    m = build_trie(["walk", "walks", "wall", "walls", "want", "wants",
                    "work", "works", "forks"])

    m.minimize()

    assert m.recognize("walk")
    assert not m.recognize("wark")
    print('automata is working as expected')
