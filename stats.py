from wordle import run
from allWords import englishWords

hist = [list() for i in range(10)]
total = 0
toTest = englishWords
for word in toTest:
    try:
        atms = run(word, False, False)
    except Exception as e:
        print("hit error on %s" % word)
        print(e)
        atms = 7
    total += atms
    hist[atms].append(word)
    if (atms > 6):
        print('%s took %d'% (word, atms))

for idx, words in enumerate(hist):
    left = str(idx) + ': ' + str(len(words))
    hundreds = round(len(words) / 100)
    print(left + (10 - len(left)) * ' ' + '*' * hundreds)

print("average: %f" % (total / len(toTest)))