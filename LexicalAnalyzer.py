import __future__
import re
from typing import Any


def isfloat(elem: Any) -> bool:
    try:
        float(elem)
        return True
    except ValueError:
        return False


def char_to_index(elem: Any) -> int:
    if elem == ' ':
        return 0
    if isfloat(elem):
        return 1
    if elem.isalpha():
        return 2
    if elem == '*':
        return 3
    if elem == '=':
        return 4
    regex = re.compile('[!%^+\-*()<>?/\|}{~;]')
    if regex.search(elem):
        return 5
    if elem == '/':
        return 6
    if elem == '\n':
        return 7
    return 8


class LexicalAnalyzer:
    dfa = [
        [1, 2, 5, 7, 9, 12, 13, 19, 20],                            # 0: initial state
        [1, None, None, None, None, None, None, 1, None],           # 1: whitespace
        [3, 2, 4, 3, 3, 3, 3, 3, 4],                                # 2: number
        [None, None, None, None, None, None, None, None, None],     # 3:
        [None, None, None, None, None, None, None, None, None],     # 4: illegal number
        [6, 5, 5, 6, 6, 6, 6, 6, 20],                               # 5
        [None, None, None, None, None, None, None, None, None],     # 6: id/keyword
        [21, 21, 21, 21, 21, 21, 8, 21, 20],                        # 7
        [None, None, None, None, None, None, None, None, None],     # 8: unmatched */
        [11, 11, 11, 11, 10, 11, 11, 11, 20],                       # 9
        [None, None, None, None, None, None, None, None, None],     # 10 symbol ==
        [None, None, None, None, None, None, None, None, None],     # 11: symbol =
        [None, None, None, None, None, None, None, None, None],     # 12: symbol
        [22, 22, 22, 14, 22, 22, 17, 22, 22],                       # 13
        [14, 14, 14, 15, 14, 14, 14, 14, 14],                       # 14
        [14, 14, 14, 15, 14, 14, 16, 14, 14],                       # 15
        [None, None, None, None, None, None, None, None, None],     # 16: /* comment */
        [17, 17, 17, 17, 17, 17, 17, 18, 17],                       # 17
        [None, None, None, None, None, None, None, None, None],     # 18: // comment\n
        [19, None, None, None, None, None, None, 19, None],         # 19: newline + whitespace
        [None, None, None, None, None, None, None, None, None],     # 20: invalid input
        [None, None, None, None, None, None, None, None, None],     # 21: symbol *
        [None, None, None, None, None, None, None, None, None]      # 22: invalid comment
    ]

    def __init__(self, filename):
        self.filename = filename
        self.output = []
        self.correct = True

    def tokenizing(self):
        try:
            f = open(self.filename, "r")
        except IOError:
            print("Invalid file path!")
            exit(1)
        i = 0
        in_comment = False
        for line in f.readlines():
            in_comment = self.use_dfa(line, i, in_comment)
            i += 1
        while self.output[0][1] != "ID/KEYWORD":
            self.output = self.output[1:]
        if in_comment:
            print("Error: Open /*")

    def classify(self, state) -> str:
        if state == 1:
            return "WHITESPACE"
        if state == 3:
            return "NUMBER"
        if state == 4:
            return "ILLEGAL_NUMBER"
        if state == 6:
            return "ID/KEYWORD"
        if state == 8:
            return "UNMATCHED */"
        if state == 10:
            return "=="
        if state == 11:
            return "="
        if state == 12:
            return "SYMBOL"
        if state == 16:
            return "/* */"
        if state == 18:
            return "//\n"
        if state == 19:
            return "\n + WHITESPACE"
        if state == 20:
            return "INVALID_INPUT"
        if state == 21:
            return "*"
        if state == 22:
            return "INVALID_COMMENT"
        return "NONE"

    def use_dfa(self, line, linenum, in_comment) -> bool:
        if len(line) <= 0:
            return
        next_state = self.dfa[0][char_to_index(line[0])]
        curr_state = 0  # self.dfa[0][char_to_index(line[0])]
        curr_token = ''  # line[0]
        i = 0
        while i < len(line) - 1:
            if in_comment:
                if line[i] + line[i + 1] == '*/':
                    in_comment = False
                i += 1
                continue
            if line[i] + line[i + 1] == '/*':
                return True
            next_state = self.dfa[curr_state][char_to_index(line[i + 1])]
            if self.classify(next_state) != "NONE" or next_state is None:
                curr_token += line[i]
                if curr_token != " ":
                    if next_state is None:
                        if curr_state == 4 or curr_state == 8 or curr_state == 20 or curr_state == 22:
                            print("Error on line ", linenum + 1, ", reason: ", line[i], ",", self.classify(curr_state))
                            self.correct = False
                        else:
                            self.output.append([curr_token, self.classify(curr_state)])
                    else:
                        if next_state == 4 or next_state == 8 or next_state == 20 or next_state == 22:
                            print("Error on line ", linenum + 1, ", reason: ", line[i], ",", self.classify(next_state))
                            self.correct = False
                        else:
                            self.output.append([curr_token, self.classify(next_state)])
                curr_state = self.dfa[0][char_to_index(line[i + 1])]
                curr_token = ""
                i += 1
                continue
            curr_token += line[i]
            i += 1
            curr_state = next_state
        return in_comment


'''if __name__ == "__main__":
    lex = LexicalAnalyzer("testfile")
    lex.tokenizing()
    print(lex.output)
    '''