# usage:
# python wordle.py hardMode knownAnswer

import sys
from allWords import englishWords
from functools import cmp_to_key

letters = "abcdefghijklmnopqrstuvwxyz"


class GameState(object):
    def __init__(self, allWords, answer=None, hardMode=False):
        self.knownCorrect = ['*'] * 5     # green letters
        self.wrongLocations = [list() for i in range(5)]  # lists of letters not at that list's index
        self.minLetterCounts = dict()     # yellow letters
        self.exactLetterCounts = dict()   # accumulation of greys
        self.answer = answer              # optional known answer
        self.allWords = sorted(allWords, key=cmp_to_key(lambda a, b: self.sortCandidates(a, b)))
        self.candidates = self.allWords.copy()
        self.hardMode = hardMode

    def guess(self):
        """
        Easy mode lets us focus on gathering intel instead of using what we already know.
        At some point (arbitrarily 5 candidates left), it makes sense to start putting letters
        where we know they belong in hopes of getting the answer right.
        Hard mode requires us to use words that match, and forego some opportunities for learning.
        """
        if len(self.candidates) < 5 or self.hardMode:
            return self.candidates[0]
        else:
            mostUseful = sorted(self.allWords, key=cmp_to_key(lambda a, b: self.sortCandidates(a, b)))
            return mostUseful[0]

    def letterMultipliers(self):
        """ When picking a word, letters are less valuable the more we already know about them. """
        """ These numbers are admittedly pretty random. """
        multipliers = {letter:1 for letter in letters}

        for letter in self.exactLetterCounts:
            multipliers[letter] = 0
        for letter in self.minLetterCounts:
            multipliers[letter] = .9
        for letter in self.knownCorrect:
            multipliers[letter] = .5

        return multipliers


    def sortCandidates(self, word1, word2):
        return self.wordUsefulness(word2) - self.wordUsefulness(word1)

    def wordUsefulness(self, word, debug=False):
        # for each letter that we don't have info about, a word gets points relative to how common the letter is in english
        valuableLetters = "qjzxvkwyfbghmpduclsntoirae"
        letters = set(word) # don't value duplicates
        score = 0
        multipliers = self.letterMultipliers()
        for letter in letters:
            if letter not in self.wrongLocations[word.find(letter)]:
                score += valuableLetters.find(letter) * multipliers[letter]

            # if (word.lower() == 'scone' and letter == 'e'):
            #     print(idx, letters, letter, letter in self.wrongLocations[idx])

        return score

    def done(self):
        return self.knownCorrect.count('*') == 0

    def printState(self):
        print("".join(self.knownCorrect).upper())
        print("Minimum letter frequencies: " + str(self.minLetterCounts))
        print("Wrong Locations: " + str(self.wrongLocations))
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

        # No letters can be in a known wrong index
        for idx, letterList in enumerate(self.wrongLocations):
            if word[idx] in letterList:
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
                self.wrongLocations[idx].append(guess[idx])
            else:
                self.exactLetterCounts[guess[idx]] = tempMinLetterCounts.get(guess[idx]) or 0

        for key in tempMinLetterCounts:
            self.minLetterCounts[key] = max(self.minLetterCounts.get(key) or 0, tempMinLetterCounts[key])

    def autoUpdateState(self, guess):
        """ Only used when we already know the answer and we're just demonstrating the program. """
        self.minLetterCounts = {}
        for idx, letter in enumerate(guess):
            if self.answer[idx] == letter:
                self.knownCorrect[idx] = letter

        tempAnswer = self.answer
        for idx, letter in enumerate(guess):
            if tempAnswer.find(letter) >= 0:
                tempAnswer = tempAnswer.replace(letter, '', 1)
                self.minLetterCounts.setdefault(letter, 0)
                self.minLetterCounts[letter] += 1
                if self.answer[idx] != letter:
                    self.wrongLocations[idx].append(letter)
            else:
                self.exactLetterCounts[letter] = self.minLetterCounts.get(letter) or 0


def run(answer, hardMode, printStats=True):
    """
        answer:
            if provided the game guesses runs automatically by self-evaluating
            if None, user must provide green/yellow/black inputs via wordle sit.
        hardMode:
            if True, the bot is required to use information it has learned
            if False, the bot can optimize for gathering information over using known-correct letters
    """
    gameState = GameState(englishWords, answer, hardMode)
    attempts = 0

    while attempts < 20:
        printStats and print("\n\n")
        attempts += 1
        guess = gameState.guess()
        printStats and print(str(attempts) + ": " + guess.upper())

        if answer:
            gameState.autoUpdateState(guess)
        else:
            gameState.promptForResult()

        if gameState.done():
            printStats and print("\nDone!\n")
            break

        gameState.filterWords()
        printStats and gameState.printState()
    return attempts



if __name__ == "__main__":
    answer = None
    hardMode = False
    if (len(sys.argv) > 1):
        hardMode = sys.argv[1].lower() == "hard"
    if (len(sys.argv) > 2):
        answer = sys.argv[2]
    else:
        print("You'll have to enter the results from the wordle app. Use G, B, and Y.")
    run(answer, hardMode)