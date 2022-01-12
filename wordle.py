import sys
from allWords import sortedEnglishWords as englishWords

class GameState(object):
    def __init__(self, englishWords, answer):
        self.knownCorrect = ['*'] * 5     # green letters
        self.minLetterCounts = dict()     # yellow letters
        self.exactLetterCounts = dict()   # accumulation of greys
        self.answer = answer              # optional known answer
        self.words = englishWords

    def guess(self):
        return self.words[0]

    def done(self):
        return self.knownCorrect.count('*') == 0

    def printState(self):
        print("".join(self.knownCorrect).upper())
        print("Minimum letter frequencies: " + str(self.minLetterCounts))
        print("Exact letter frequencies: " + str({key:value for (key,value) in self.exactLetterCounts.items() if value > 0}))
        print("Letters not present: " + str({key:value for (key,value) in self.exactLetterCounts.items() if value == 0}))
        if (len(self.words) < 5):
            plural = ' candidates' if len(self.words) > 1 else ' candidate'
            print(str(len(self.words)) + plural + " remaining: " + ', '.join(self.words))
        else:
            print(str(len(self.words)) + " candidates remaining")

    def filterWords(self):
        self.words = [word for word in self.words if self.wordAllowed(word)]

    def wordAllowed(self, word):
        """ Determine if a word fits what we know about the Wordle solution """

        # All green letters must be present
        for idx, letter in enumerate(self.knownCorrect):
            if letter != "*" and word[idx] != letter:
                return False

        # All yellow letters must be present (and we might need more than 1)
        for letter in self.minLetterCounts:
            if word.count(letter) < self.minLetterCounts[letter]:
                return False

        # If we've seen grey letters, we know exactly the count of that letter (doesn't mean it's 0 though)
        for letter in self.exactLetterCounts:
            if word.count(letter) != self.exactLetterCounts[letter]:
                return False

        return True

    def promptForResult(self):
        """
        Ask the user what colors were returned by the Wordle web app.
        Not used if we know the answer already (see autoUpdateState())
        """
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
                self.exactLetterCounts[guess[idx]] = self.minLetterCounts.get(guess[idx]) or 0

    def autoUpdateState(self, guess):
        """ Only used when we already know the answer and we're just demonstrating the program. """
        self.minLetterCounts = {}
        for idx, letter in enumerate(guess):
            if self.answer[idx] == letter:
                self.knownCorrect[idx] = letter

        tempAnswer = self.answer
        for letter in guess:
            if tempAnswer.find(letter) >= 0:
                tempAnswer = tempAnswer.replace(letter, '', 1)
                self.minLetterCounts.setdefault(letter, 0)
                self.minLetterCounts[letter] += 1
            else:
                self.exactLetterCounts[letter] = self.minLetterCounts.get(letter) or 0

#
# Two modes.
# If answer is provided in args, this runs automatically.
# Otherwise, we don't know the answer, and we need to ask the user for knownCorrect, yellows, etc.
#

answer = None
if (len(sys.argv) > 1):
    answer = sys.argv[1]
else:
    print("You'll have to enter the results from the wordle app. Use G, B, and Y.")

gameState = GameState(englishWords, answer)
attempts = 0

while attempts < 20:
    print("\n\n")
    attempts += 1
    guess = gameState.guess()
    print("Attempt " + str(attempts))
    print(guess.upper())
    
    if answer:
        gameState.autoUpdateState(guess)
    else:
        gameState.promptForResult()

    if gameState.done():
        print("\nDone!\n")
        break

    gameState.filterWords()
    gameState.printState()

