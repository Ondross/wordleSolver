# usage:
# python wordle.py hardMode knownAnswer

import sys
from allWords import englishWords
from functools import cmp_to_key

letters = "abcdefghijklmnopqrstuvwxyz"


class GameState(object):
    def __init__(self, allWords, answer=None, hardMode=False):
        self.done = False
        self.knownCorrect = ['*'] * 5     # green letters
        self.wrongLocations = [list() for i in range(5)]  # lists of letters not at that list's index
        self.minLetterCounts = dict()     # yellow letters
        self.exactLetterCounts = dict()   # accumulation of greys
        self.answer = answer              # optional known answer
        self.allWords = allWords
        self.candidates = self.allWords.copy()
        self.lastUpdateCount = -1
        self.updateLetterUsefulness()
        self.hardMode = hardMode

    def guess(self):
        """
        Easy mode lets us focus on gathering intel instead of using what we already know.
        At some point (arbitrarily 5 candidates left), it makes sense to start putting letters
        where we know they belong in hopes of getting the answer right.
        Hard mode requires us to use words that match, and forego some opportunities for learning.
        """

        choices = self.allWords
        if len(self.candidates) < 3 or self.hardMode:
            choices =  self.candidates

        self.updateLetterUsefulness()
        mostUseful = sorted(choices, key=cmp_to_key(lambda a, b: self.sortCandidates(a, b)))
        return mostUseful[0]

    def sortCandidates(self, word1, word2):
        return self.wordUsefulness(word2) - self.wordUsefulness(word1)

    def updateLetterUsefulness(self):
        """
        computes the histogram of letters in the remaining words
        letter score is equal to -abs(frequency of appearance - .5) + .5, since the best
        guesses are in 50% of words.
        store dupes as {a: 10, aa: 2} signifying 2 words with double As (not necessarily consecutive).
        """
        if len(self.candidates) == self.lastUpdateCount:
            return
        letterHist = {}
        for letter in letters:
            letterHist[letter] = 0
            letterHist[letter * 2] = 0
            letterHist[letter * 3] = 0
            for word in self.candidates:
                if letter in word:
                    for i in range(word.count(letter)):
                        toAdd = 1
                        if self.minLetterCounts.get(letter):
                            toAdd = .1  # still somewhat worthwhile to find where it fits. Difficult to tune this number.
                        letterHist[letter * (i + 1)] += toAdd
        
        def score(frequency):
            return -1 * abs(frequency - .5) + .5

        self.lastUpdateCount = len(self.candidates)
        self.letterValues = {letter: score(val/len(self.candidates)) for letter,val in letterHist.items()}

    def wordUsefulness(self, word):
        # for each letter that we don't have info about, a word gets points relative to how common the letter is in english
        letters = list(word) 
        score = 0
        for idx, letter in enumerate(letters):
            knownWrongLocation = letter in self.wrongLocations[word.find(letter)]
            knownRightLocation = self.knownCorrect[idx] == letter
            if not knownWrongLocation and not knownRightLocation:
                if idx == word.find(letter):
                    score += self.letterValues[letter]
                else:
                    # it's the second time we're seeing this. probably less valuable.
                    # todo: handle triples
                    score += self.letterValues[letter * 2]

        return score

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

    def promptForResult(self, guess):
        """
        Ask the user what colors were returned by the Wordle web app.
        Not used if we know the answer already (see autoUpdateState())
        """
        print("Input result:")
        colors = input().lower().replace(' ', '')

        # make a temp version of this dict based only on the information we're getting here.
        tempMinLetterCounts = {}
        numCorrect = 0
        for idx, color in enumerate(colors):
            if color == "g":
                self.knownCorrect[idx] = guess[idx]
                numCorrect += 1
            elif color == "y":
                tempMinLetterCounts.setdefault(guess[idx], 0)
                tempMinLetterCounts[guess[idx]] += 1
                self.wrongLocations[idx].append(guess[idx])
            else:
                self.exactLetterCounts[guess[idx]] = tempMinLetterCounts.get(guess[idx]) or 0

        if numCorrect == 5:
            self.done = True
        for key in tempMinLetterCounts:
            self.minLetterCounts[key] = max(self.minLetterCounts.get(key) or 0, tempMinLetterCounts[key])

    def autoUpdateState(self, guess):
        """ Only used when we already know the answer and we're just demonstrating the program. """
        tempMinLetterCounts = {}
        if guess == self.answer:
            self.done = True
        for idx, letter in enumerate(guess):
            if self.answer[idx] == letter:
                self.knownCorrect[idx] = letter

        tempAnswer = self.answer
        for idx, letter in enumerate(guess):
            if tempAnswer.find(letter) >= 0:
                tempAnswer = tempAnswer.replace(letter, '', 1)
                tempMinLetterCounts.setdefault(guess[idx], 0)
                tempMinLetterCounts[guess[idx]] += 1
                if self.answer[idx] != letter:
                    self.wrongLocations[idx].append(letter)
            else:
                self.exactLetterCounts[letter] = tempMinLetterCounts.get(letter) or 0

        for key in tempMinLetterCounts:
            self.minLetterCounts[key] = max(self.minLetterCounts.get(key) or 0, tempMinLetterCounts[key])

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
            gameState.promptForResult(guess)

        if gameState.done:
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