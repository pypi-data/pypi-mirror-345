class TextSubstitution:
    def __init__(self, shortcut: str, phrase: str):
        """
        Initialize a TextSubstitution instance.

        :param shortcut: The shortcut string for the substitution.
        :param phrase: The phrase to substitute when the shortcut is used.
        """
        self.shortcut = shortcut
        self.phrase = phrase

    def __eq__(self, other):
        if not isinstance(other, TextSubstitution):
            return False
        return self.shortcut == other.shortcut and self.phrase == other.phrase

    def __repr__(self):
        """
        Return a string representation of the TextSubstitution instance.
        """
        return f"TextSubstitution(shortcut={self.shortcut!r}, phrase={self.phrase!r})"
