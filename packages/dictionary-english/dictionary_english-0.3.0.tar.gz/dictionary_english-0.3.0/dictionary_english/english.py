class english:
    def __init__(self):
        self.language = "English"
        self.dictionary = {
            "hello": "A greeting or expression of goodwill.",
            "world": "The earth, together with all of its countries and peoples.",
            "python": "A high-level programming language.",
            "code": "A system of words, letters, figures, or symbols used to represent others.",
        }

    def get_definition(self, word):
        return self.dictionary.get(word.lower(), "Definition not found.")

def korea(word):
    return "heello" if word == "hello" else "Definition not found."