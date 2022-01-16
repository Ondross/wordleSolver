from wordle import run
from allWords import englishWords

hist = [list() for i in range(10)]
for word in englishWords:
    atms = run(word, False, False)
    hist[atms].append(word)
    if (atms > 6):
        print('%s took %d'% (word, atms))

for idx, words in enumerate(hist):
    left = str(idx) + ': ' + str(len(words))
    hundreds = round(len(words) / 100)
    print(left + (10 - len(left)) * ' ' + '*' * hundreds)
