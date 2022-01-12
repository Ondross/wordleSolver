import sys
from allWords import sortedEnglishWords as englishWords

class GameState(object):
    def __init__(self, answer):
        self.knownCorrect = [None] * 5  # green letters
        self.minLetterCounts = dict()   # yellow letters
        self.maxLetterCounts = dict()   # accumulation of greys
        self.answer = answer

    def wordAllowed(self, word):
        """ Check if a word is allowed based on the game state """
        for idx, letter in enumerate(self.knownCorrect):
            if letter and word[idx] != letter:
                return False

        for letter in self.maxLetterCounts:
            if word.count(letter) > self.maxLetterCounts[letter]:
                return False

        for letter in self.minLetterCounts:
            if word.count(letter) < self.minLetterCounts[letter]:
                return False

        return True

    def promptForResult(self):
        print("Input result:")
        colors = input()

        self.minLetterCounts = dict()
        for idx, color in enumerate(colors):
            if color.lower() == "g":
                self.knownCorrect[idx] = guess[idx]
            elif color.lower() == "y":
                self.minLetterCounts.setdefault(guess[idx], 0)
                self.minLetterCounts[guess[idx]] += 1
            else:
                self.maxLetterCounts[guess[idx]] = self.minLetterCounts.get(guess[idx]) or 0

    def update(self, guess):
        """ Only used when we already know the answer and we're just demonstrating the program. """
        self.minLetterCounts = {}
        tempAnswer = self.answer
        for idx, letter in enumerate(guess):
            if tempAnswer[idx] == letter:
                self.knownCorrect[idx] = letter
                tempAnswer = tempAnswer.replace(letter, '*')
                self.minLetterCounts.setdefault(letter, 0)
                self.minLetterCounts[letter] += 1

        for letter in guess:
            if tempAnswer.find(letter) >= 0:
                tempAnswer = tempAnswer.replace(letter, '')
                self.minLetterCounts.setdefault(letter, 0)
                self.minLetterCounts[letter] += 1
            else:
                self.maxLetterCounts[letter] = self.minLetterCounts.get(letter) or 0

# Two modes.
# If answer is provided in args, this runs automatically.
# Otherwise, we don't know the answer, and we need to ask the user for knownCorrect, yellows, etc.
answer = None
if (len(sys.argv) > 1):
    answer = sys.argv[1]
else:
    print("You'll have to enter your own results from the wordle app. Use G, B, and Y.")

gameState = GameState(answer)
attempts = 0

while attempts < 20:
    guess = englishWords[0]
    print("Attempt " + str(attempts + 1))
    print("Guess: " + guess)
    
    if answer:
        gameState.update(guess)
    else:
        gameState.promptForResult()

    if gameState.knownCorrect.count(None) == 0:
        print("Done!")
        break

    englishWords = [word for word in englishWords if gameState.wordAllowed(word)]
    attempts += 1

    print("Greens: " + str(gameState.knownCorrect))
    print("Min letter counts: " + str(gameState.minLetterCounts))
    print("Max letter counts: " + str(gameState.maxLetterCounts))
    print("Num candidates remaining: " + str(len(englishWords)))

    if (len(englishWords) < 5):
        print(englishWords)

    print("\n\n")

