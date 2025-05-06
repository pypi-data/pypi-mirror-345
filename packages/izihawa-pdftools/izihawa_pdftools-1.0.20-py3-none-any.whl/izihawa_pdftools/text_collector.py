import re


class TextCollector:
    def __init__(self, inverted=False, separator=""):
        self.text = []
        self.operations = []
        self.inverted = inverted
        self.separator = separator

    def add_piece(self, text, operation):
        if self.inverted:
            self.text = [text] + self.text
            self.operations = [operation] * (
                len(text) + len(self.separator)
            ) + self.operations
        else:
            self.text.append(text)
            self.operations.extend([operation] * (len(text) + len(self.separator)))

    def match(self, pattern):
        operations = []
        texts = []

        for match in re.finditer(pattern, self.separator.join(self.text)):
            left, right = match.span()
            texts.append(match.group())
            operations.extend(self.operations[left:right])
        return "\n".join(texts), list(sorted(set(operations)))

    def clear(self):
        self.text = []
        self.operations = []
