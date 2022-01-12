import sys
from allWords import englishWords
from functools import cmp_to_key

letters = "abcdefghijklmnopqrstuvwxyz"


def sortCandidates(word1, word2):
    return gameState.wordUsefulness(word2) - gameState.wordUsefulness(word1)

class GameState(object):
    def __init__(self, allWords, answer):
        self.knownCorrect = ['*'] * 5     # green letters
        self.minLetterCounts = dict()     # yellow letters
        self.exactLetterCounts = dict()   # accumulation of greys
        self.answer = answer              # optional known answer
        self.candidates = allWords.copy()
        self.allWords = allWords

    def guess(self):
        if len(self.candidates) < 50:
            return self.candidates[0]
        else:
            mostUseful = sorted(englishWords, key=cmp_to_key(sortCandidates))
            return mostUseful[0]

    def unknownLetters(self):
        missing = letters
        for letter in list(self.exactLetterCounts.keys()) + list(self.minLetterCounts.keys()) + self.knownCorrect:
            missing = missing.replace(letter, '')

        return set(missing)

    def wordUsefulness(self, word, debug=False):
        # for each letter that we don't have info about, a word gets points relative to how common the letter is in english
        valuableLetters = "qjzxvkwyfbghmpduclsntoirae"
        letters = set(word) # don't value duplicates
        score = 0

        for letter in letters & self.unknownLetters():
            score += valuableLetters.find(letter)

        return score

    def done(self):
        return self.knownCorrect.count('*') == 0

    def printState(self):
        print("".join(self.knownCorrect).upper())
        print("Minimum letter frequencies: " + str(self.minLetterCounts))
        print("Exact letter frequencies: " + str({key:value for (key,value) in self.exactLetterCounts.items() if value > 0}))
        print("Letters not present: " + str({key:value for (key,value) in self.exactLetterCounts.items() if value == 0}))
        if (len(self.candidates) < 5):
            plural = ' candidates' if len(self.candidates) > 1 else ' candidate'
            print(str(len(self.candidates)) + plural + " remaining: " + ', '.join(self.candidates))
        else:
            print(str(len(self.candidates)) + " candidates remaining")

    def filterWords(self):
        self.candidates = [word for word in self.candidates if self.wordAllowed(word)]

    def wordAllowed(self, word):
        """ Determine if a word matches with the info that we know about the Wordle solution """

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

        # make a temp version of this dict based only on the information we're getting here.
        tempMinLetterCounts = dict()
        for idx, color in enumerate(colors):
            if color.lower() == "g":
                self.knownCorrect[idx] = guess[idx]
            elif color.lower() == "y":
                tempMinLetterCounts.setdefault(guess[idx], 0)
                tempMinLetterCounts[guess[idx]] += 1
            else:
                self.exactLetterCounts[guess[idx]] = tempMinLetterCounts.get(guess[idx]) or 0

        for key in tempMinLetterCounts:
            self.minLetterCounts[key] = max(self.minLetterCounts.get(key), tempMinLetterCounts[key])

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

while attempts < 7:
    print("\n\n")
    attempts += 1
    guess = gameState.guess()
    print(str(attempts) + ": " + guess.upper())
    
    if answer:
        gameState.autoUpdateState(guess)
    else:
        gameState.promptForResult()

    if gameState.done():
        print("\nDone!\n")
        break

    gameState.filterWords()
    gameState.printState()

