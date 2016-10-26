"""
Debate analyzer project

Preston Mackert, Dylan Telford, Alexis Grebenok, Jerry Daigler
"""

import sys
import nltk
import re
import bs4
from __future__ import print_function
from urllib import urlopen
from bs4 import BeautifulSoup


def main_menu():
    user_in = raw_input(">> ")
    quit_prog = False
    while not quit_prog:
        if user_in == "help":
            print("list commands")
            main_menu()
        elif user_in == "quit":
            sys.exit(0)
        else:
            print("lol not done yet")

def main():
    print("Welcome! Are you ready to 'Make AI Great Again?'\ntype a command, help will show all commands, quit will"
          "exit the program")
    main_menu()

def clean_and_tag(url):
    """"""
    raw = urlopen(url).read()
    soup = BeautifulSoup(raw, 'html.parser')
    cleaned = BeautifulSoup.get_text(soup)
    tokens = nltk.word_tokenize(cleaned)
    tokens = trim_tokens(tokens)
    tagged_tokens = nltk.pos_tag(tokens)
    return nltk.Text(tagged_tokens)

def trim_tokens(tokens):
    """Removes garbage from beginning and end of tokens"""


if __name__ == '__main__':
    main()