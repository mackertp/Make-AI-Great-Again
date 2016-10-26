from __future__ import print_function
import sys
import nltk
import re
import bs4
from urllib import urlopen
from bs4 import BeautifulSoup
from AnalysisTools import AnalysisTools

"""
Debate analyzer project

Preston Mackert, Dylan Telford, Alexis Grebenok, Jerry Daigler
10/26/16
"""


def main_menu():
    print("Type a command, help shows all commands, quit will exit the program\n")
    user_in = raw_input(">> ")
    quit_prog = False

    while not quit_prog:
        if user_in == "help":
            print("help -- show options\nselect -- pick a debate to be analyzed\nquit -- quits program")
            main_menu()

        elif user_in == "select":
            url = select_debate()
            clean_text = clean_and_tag(url)
            at = AnalysisTools(clean_text)
            sub_menu(at)

        elif user_in == "quit":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("lol not done yet")


def sub_menu(at):
    print("\nType a command, help shows all valid commands, return sends back to main menu")
    user_in = raw_input(">> ")

    if user_in == "help":
        print("commands")

    elif user_in == "return":
        main_menu()

    elif user_in == "participants":
        # prints participants in the debate
        print(at.participants)
        sub_menu(at)

    elif user_in == "moderators":
        # prints the moderators
        print(at.moderators)
        sub_menu(at)

    elif user_in == "words":
        # choose total words spoken or break down by candidates
        print("")

    elif user_in == "concordance":
        # select a word and a candidate, gives back concordance
        print("")

    elif user_in == "quit":
        print("Goodbye!")
        sys.exit(0)


def select_debate():
    print("\nSelect a debate from:\n1) Democratic Primary\n2) Republican Primary\n3) VP Debate\n4) General Election\n5)"
          " add your own!\n")
    url = ""
    user_in = raw_input(">> ")
    if user_in == "1":
        # select form democrat debates
        print("\nSelect one of the debates:\n1) Las Vegas 10-13-15\n2) Des Moines 11-14-15\n3) Manchester 12-19-15\n"
              "4) Charleston 1-17-16\n5) Durham 2-4-16\n6) Milwaukee 2-11-16\n7) Flint 3-6-16\n8) Miami 3-9-16\n9) "
              "Brooklyn 4-14-16\n")
        select = raw_input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110903"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110910"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111178"
        elif select == "4":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111409"
        elif select == "5":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111471"
        elif select == "6":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111520"
        elif select == "7":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=112718"
        elif select == "8":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=112719"
        elif select == "9":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=116995"
        else:
            print("Invalid command, no debate selected")

    elif user_in == "2":
        # select from republican debates
        print("\nSelect one of the debates:\n1) Cleveland 8-6-15\n2) Simi Valley 9-16-15\n3) Boulder 10-28-15\n4) "
              "Milwaukee 11-10-15\n5) Las Vegas 12-15-15\n6) North Charleston 1-14-16\n7) Des Moines 1-28-16\n8) "
              "Manchester 2-6-16\n9) Greenville 2-13-16\n10) Houston 2-25-16\n11) Detroit 3-3-16\n12) Miami 3-10-16\n")
        select = raw_input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110489"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110756"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110906"
        elif select == "4":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110908"
        elif select == "5":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111177"
        elif select == "6":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111395"
        elif select == "7":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111412"
        elif select == "8":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111472"
        elif select == "9":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111500"
        elif select == "10":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111634"
        elif select == "11":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111711"
        elif select == "12":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=115148"
        else:
            print("Invalid command, no url selected")

    elif user_in == "3":
        # the VP debate is selected, only one exists
        url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119012"

    elif user_in == "4":
        # debates from the general election will be options
        print("\nSelect one of the debates:\n1) Hofstra 9-26-16\n2) Washington University 10-9-16\n3) University Nevada"
              " 10-19-16\n")
        select = raw_input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=118971"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119038"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119039"
        else:
            print("invalid command, no url selected")

    elif user_in == "5":
        url = raw_input(">> ")

    else:
        print("Invalid command, type a valid option (1-5)")
        select_debate()

    return url


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
    start = 0
    end = len(tokens)-1
    for i in range(len(tokens)):
        if tokens[i] == 'PARTICIPANTS' and tokens[i+1] == ':':
            start = i
        elif tokens[i] == 'Citation' and tokens[i+1] == ':':
            end = i
            break
    return tokens[start:end]


def main():
    print("Welcome! Are you ready to 'Make AI Great Again?'")
    main_menu()

if __name__ == '__main__':
    main()
