import sys
import random
from allWords import englishWords

# import re
# pattern = re.compile("[a-z]+")
# englishWords = list()
# for line in open('english-words.txt'):
#     englishWords = englishWords + [word.strip().lower() for word in line.split() if len(word.strip()) == 5 and pattern.fullmatch(word.strip().lower())]

# used to filter list of possible words
def wordAllowed(word, greens, minNumEachLetter, maxNumEachLetter):
    for idx, letter in enumerate(greens):
        if letter and word[idx] != letter:
            return False

    for letter in maxNumEachLetter:
        if word.count(letter) > maxNumEachLetter[letter]:
            return False

    for letter in minNumEachLetter:
        if word.count(letter) < minNumEachLetter[letter]:
            return False

    return True

# this is only used when we already know the answer and we're just demonstrating the program.
def updateGreensEtc(guess, answer, maxNumEachLetter):
    minNumEachLetter = {}
    greens = [None] * len(answer)
    for idx, letter in enumerate(guess):
        if answer[idx] == letter:
            greens[idx] = letter
            answer = answer.replace(letter, '*')
            minNumEachLetter.setdefault(letter, 0)
            minNumEachLetter[letter] += 1

    for letter in guess:
        if answer.find(letter) >= 0:
            answer = answer.replace(letter, '')
            minNumEachLetter.setdefault(letter, 0)
            minNumEachLetter[letter] += 1
        else:
            maxNumEachLetter[letter] = minNumEachLetter.get(letter) or 0

    return greens, minNumEachLetter

# Two modes.
# If answer is provided in args, this runs automatically.
# Otherwise, we don't know the answer, and we need to ask the user for greens, yellows, etc.
answer = None
if (len(sys.argv) > 1):
    answer = sys.argv[1]
else:
    print("You'll have to enter your own results from the wordle app. Use G, B, and Y.")

attempts = 0
minNumEachLetter = {}
maxNumEachLetter = {}
greens = [None] * 5

while attempts < 20:
    guess = random.choice(englishWords)

    print("Attempt " + str(attempts + 1))
    print("Guess: " + guess)

    # TODO: right now, this assumes hard mode. If we don't reset this every time, we could use past yellows, but it's not so simple.
    minNumEachLetter = dict()
    if answer:
        greens, minNumEachLetter = updateGreensEtc(guess, answer, maxNumEachLetter)
    else:
        print("Input result:")
        colors = input()

        # If they enter an empty string, assume that wordle didn't accept the guess as a real word, and try again.
        if not colors:
            englishWords.remove(guess)
            continue

        # Update running list of greens, running
        for idx, color in enumerate(colors):
            if color.lower() == "g":
                greens[idx] = guess[idx]
            elif color.lower() == "y":
                minNumEachLetter.setdefault(guess[idx], 0)
                minNumEachLetter[guess[idx]] += 1
            else:
                maxNumEachLetter[guess[idx]] = minNumEachLetter.get(guess[idx]) or 0
    englishWords = [word for word in englishWords if wordAllowed(word, greens, minNumEachLetter, maxNumEachLetter)]
    attempts += 1

    print("Greens: " + str(greens))
    print("Min letter counts: " + str(minNumEachLetter))
    print("Max letter counts: " + str(maxNumEachLetter))
    print("Num candidates remaining: " + str(len(englishWords)))

    if (len(englishWords) < 5):
        print(englishWords)

    if (len(englishWords) == 1):
        print("Done")
        break

    print("\n\n")

