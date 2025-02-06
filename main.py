from spell_fst import Spell_Checker
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("word")
    args = ap.parse_args()

    print(f'entered word: {args.word}')

    spellchecker = Spell_Checker()

    suggestions = sorted(set(list(spellchecker.fst.transduce(args.word))), key=lambda x: x[1], reverse=True)

    n = 10 if 10 < len(suggestions) else len(suggestions)

    print('candidate corrections...')
    for i in range(n):
        candidate, prob = suggestions[i] 
        print(f'{i + 1}. {candidate} ~ {prob}')
