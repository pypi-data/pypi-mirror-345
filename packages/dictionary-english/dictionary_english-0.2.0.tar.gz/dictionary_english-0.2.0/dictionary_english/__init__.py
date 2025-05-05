__vsersion__ = "0.1.0"
__author__ = "WooYoung Moon"

from .english import english
import csv

dictionary = {
    "hello": "A greeting or expression of goodwill.",
    "world": "The earth, together with all of its countries and peoples.",
    "python": "A high-level programming language.",
    "code": "A system of words, letters, figures, or symbols used to represent others.",
}

def add(word):
    print("heello" if word == "hello" else "Definition not found.")