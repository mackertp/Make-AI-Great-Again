"""
Debate analyzer project ("Make AI Great Again")
Main class
-- creates the menu based program for analyzing debates

Dylan Telford, Preston Mackert, Alexis Grebenok, Jerry Daigler
10/26/16
"""

# ------------------------------------------- #
# imports
# ------------------------------------------- #

from __future__ import print_function
import sys
import nltk
from urllib.request import urlopen
from bs4 import BeautifulSoup
from support_functions.analysis_tools import AnalysisTools
from support_functions.twitter_tools import *


# ------------------------------------------- #
# start CLI application
# ------------------------------------------- #

def main_menu():
    """
    Main menu for the program. Forces you to select a debate for analysis
    """
    print("Type 'select' to pick a debate for analysis, 'help' shows all commands, 'quit' will exit the program")
    user_in = input(">> ")
    quit_prog = False

    while not quit_prog:
        if user_in == "help":
            print("\nhelp -- show options\nselect -- pick a debate to be analyzed\nquit -- quits program\n")
            main_menu()
        elif user_in == "select":
            info = select_debate()
            url = info[0]
            date = info[1]
            print("processing text...")
            clean_text = clean_and_tag(url)
            at = AnalysisTools(clean_text)
            print("\nDebate selected, perform analysis on this debate with the following commands!\n1) print "
                  "participants\n2) print moderators\n3) print total number of words by candidates\n4) print out number"
                  " of words for each candidate\n5) print number of words for specific candidate\n6) print out "
                  "concordance for a word and candidate\n7) Twitter tools!")
            sub_menu(at, date)

        elif user_in == "quit":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid command\n")
            main_menu()


def sub_menu(at, date):
    """
    Sub menu, once a debate is selected this menu provides the options for analyzing the text
    """
    print("\nType a command, 'help' shows all valid commands, 'return' sends back to main menu")
    user_in = input(">> ")

    if user_in == "help":
        print("\n1) print participants\n2) print moderators\n3) print total number of words by candidates\n4) "
              "print out number of words for each candidate\n5) print number of words for specific candidate\n6) print"
              "out concordance for a word and candidate\n7) goes to twitter tools submenu\n'help' -- prints out all "
              "commands\n'return' -- sends back to main menu\n'quit' -- quits the program")
        sub_menu(at, date)

    elif user_in == "return":
        print("\n")
        main_menu()

    elif user_in == "1":
        # prints participants in the debate
        output = ""
        for name in at.get_participants():
            if name != at.get_participants()[len(at.get_participants()) - 1]:
                output += name + ", "
            else:
                output += name
        print("\nParticipants: " + output + "\n")
        sub_menu(at, date)

    elif user_in == "2":
        # prints the moderators
        output = ""
        for name in at.get_moderators():
            if name != at.get_moderators()[len(at.get_moderators()) - 1]:
                output += name + ", "
            else:
                output += name
        print("\nModerators: " + output + "\n")
        sub_menu(at, date)

    elif user_in == "3":
        # choose total words spoken or break down by candidates
        print("\nTotal words spoken by candidates: " + str(at.total_words()) + "\n")
        sub_menu(at, date)

    elif user_in == "4":
        print("\n" + at.words_by_all_candidates())
        sub_menu(at, date)

    elif user_in == "5":
        can_num = 1
        print("\nSelect a candidate:")
        for name in at.get_participants():
            print("%d) %s" % (can_num, name))
            can_num += 1
        select = input(">> ")
        candidate = ""
        try:
            candidate = at.get_participants()[int(select)-1]
        except (IndexError, ValueError):
            print("No valid candidate selected")
            sub_menu(at, date)
        print("\n" + at.words_by_candidate(candidate) + "\n")
        sub_menu(at, date)

    elif user_in == "6":
        # select a word and a candidate, gives back concordance
        can_num = 1
        print("\nSelect a candidate:\n")
        for name in at.get_participants():
            print("%d) %s" % (can_num, name))
            can_num += 1
        select = input(">> ")
        candidate = ""
        try:
            candidate = at.get_participants()[int(select) - 1]
        except (IndexError, ValueError):
            print("No valid candidate selected")
            sub_menu(at, date)
        print("\nSelect a word to look for")
        word = input(">> ")
        at.get_concordance(candidate, word)
        # print(at.make_concordance(candidate, word))  # * for testing our own concordance function *
        sub_menu(at, date)

    elif user_in == "7":
        twitter_menu(at, date)

    elif user_in == "quit":
        print("Goodbye!")
        sys.exit(0)

    else:
        print("Invalid command, type 'help' to see a list of all valid commands\n")
        sub_menu(at, date)


def twitter_menu(at, date):
    """
    Sub Menu for using our twitter tools. Allows the user to pick a candidate to find topics using nltk collocations.
    A list of the topics will be presented, then the user can search candidate, opponents, or all of twitter to see
    what users had to say about the topics being discussed in the debate! More options and features to come.
    """
    print("\nFind out what the world had to say! Select a candidate and explore twitter! Type return to go back to "
          "text analysis of the debate.\n\nSelect a candidate:")
    can_num = 1
    for name in at.get_participants():
        print("%d) %s" % (can_num, name))
        can_num += 1
    select = input("\n>> ")
    if select == "return":
        sub_menu(at, date)
    candidate = ""
    try:
        candidate = at.get_participants()[int(select) - 1]
    except (IndexError, ValueError):
        print("No valid candidate selected")
        twitter_menu(at, date)

    topics = at.candidate_topics(candidate)

    print("\nThese were %s's most discussed topics, pick one!\n" % candidate)
    topic_num = 1
    for topic in topics:
        print("%d) %s" % (topic_num, topic))
        topic_num += 1

    select = input("\n>> ")

    try:
        topic = topics[int(select)-1]

    except (IndexError, ValueError):
        print("Invalid selection")
        twitter_menu(at, date)

    print("How would you like to search Twitter?\n\n1) Mentions candidate\n2) Mentions opponent\n")

    select = input(">> ")

    if select == "1":
        tweets = candidate_mentions(topic, candidate)
        top_tweets = get_top_five(tweets)
        print(top_tweets)
        tweet_text = []
        for tweet in tweets:
            tweet_text.append(tweet.text)
        at.bayes_classify(tweet_text)

    if select == "2":
        can_num = 1
        candidates = []
        print("\nSelect the candidate you wish to see on twitter!")
        for name in at.get_participants():
            if name != candidate:
                candidates.append(name)
                print("%d) %s" % (can_num, name))
                can_num += 1
        select = input("\n>> ")
        try:
            candidate = candidates[int(select) - 1]
        except (IndexError, ValueError):
            print("No valid candidate selected")
            twitter_menu(at, date)

        tweets = candidate_mentions(topic, candidate)
        top_tweets = get_top_five(tweets)
        print(top_tweets)
        tweet_text = []
        for tweet in tweets:
            tweet_text.append(tweet.text)
        at.bayes_classify(tweet_text)

    twitter_menu(at, date)


def select_debate():
    """
    Method for selecting a debate, has stored all the 2016 election debates, or can add your own by url
    """
    print("\nSelect a debate from 2016:\n1) Democratic Primary\n2) Republican Primary\n3) VP Debate\n4)"
          " General Election\n")    # 5) add your own!\n
    url = ""
    user_in = input(">> ")
    date = ""
    if user_in == "1":
        # select form democratic primary debates
        print("\nSelect one of the debates:\n1) Las Vegas 10-13-15\n2) Des Moines 11-14-15\n3) Manchester 12-19-15\n"
              "4) Charleston 1-17-16\n5) Durham 2-4-16\n6) Milwaukee 2-11-16\n7) Flint 3-6-16\n8) Miami 3-9-16\n"
              "9) Brooklyn 4-14-16\n")
        select = input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110903"
            date = "2015-10-13"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110910"
            date = "2015-11-14"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111178"
            date = "2015-12-19"
        elif select == "4":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111409"
            date = "2016-01-17"
        elif select == "5":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111471"
            date = "2016-02-04"
        elif select == "6":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111520"
            date = "2016-02-11"
        elif select == "7":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=112718"
            date = "2016-03-06"
        elif select == "8":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=112719"
            date = "2016-03-09"
        elif select == "9":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=116995"
            date = "2016-04-14"
        else:
            print("Invalid command, no debate selected")
            select_debate()

    elif user_in == "2":
        # select from republican primary debates
        print("\nSelect one of the debates:\n1) Cleveland 8-6-15\n2) Simi Valley 9-16-15\n3) Boulder 10-28-15\n4) "
              "Milwaukee 11-10-15\n5) Las Vegas 12-15-15\n6) North Charleston 1-14-16\n7) Des Moines 1-28-16\n8) "
              "Manchester 2-6-16\n9) Greenville 2-13-16\n10) Houston 2-25-16\n11) Detroit 3-3-16\n12) Miami 3-10-16\n")
        select = input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110489"
            date = "2015-08-06"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110756"
            date = "2015-09-16"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110906"
            date = "2015-10-28"
        elif select == "4":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=110908"
            date = "2015-11-10"
        elif select == "5":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111177"
            date = "2015-12-15"
        elif select == "6":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111395"
            date = "2016-01-14"
        elif select == "7":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111412"
            date = "2016-01-28"
        elif select == "8":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111472"
            date = "2016-02-06"
        elif select == "9":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111500"
            date = "2016-02-13"
        elif select == "10":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111634"
            date = "2016-02-25"
        elif select == "11":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=111711"
            date = "2016-03-03"
        elif select == "12":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=115148"
            date = "2016-03-10"
        else:
            print("Invalid command, no url selected")
            select_debate()

    elif user_in == "3":
        # the 2016 VP debate is selected, only one exists
        url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119012"
        date = "2016-10-4"

    elif user_in == "4":
        # debates from the general election will be options
        print("\nSelect one of the debates:\n1) Hofstra 9-26-16\n2) Washington University 10-9-16\n3) University Nevada"
              " 10-19-16\n")
        select = input(">> ")
        if select == "1":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=118971"
            date = "2016-09-26"
        elif select == "2":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119038"
            date = "2016-10-09"
        elif select == "3":
            url = "http://www.presidency.ucsb.edu/ws/index.php?pid=119039"
            date = "2016-10-19"
        else:
            print("invalid command, no url selected")
            select_debate()

    # elif user_in == "5":
        # add your own debate... type the url and boom there ya have it
        """ took this out because it wasn't working correctly, couldn't handle url errors """

    else:
        print("Invalid command, type a valid option (1-4)")
        select_debate()

    return [url, date]


def clean_and_tag(url):
    """ given a url for a debate, obtain the page text with urlopen, clean it with
    BeautifulSoup, tokenize with nltk.word_tokenize(), trim leading and trailing
    garbage with a call to trim_tokens(), tag the tokens with nltk.pos_tag(), and
    return a text object made with tagged_tokens """
    raw = urlopen(url).read()
    soup = BeautifulSoup(raw, 'html.parser')
    cleaned = BeautifulSoup.get_text(soup)
    tokens = nltk.word_tokenize(cleaned)
    tokens = trim_tokens(tokens)
    tagged_tokens = nltk.pos_tag(tokens)
    return nltk.Text(tagged_tokens)


def trim_tokens(tokens):
    """ Removes garbage from beginning and end of tokens """
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
    """ Main call, runs the program """
    print("Welcome! Are you ready to 'Make AI Great Again?'")
    main_menu()

if __name__ == '__main__':
    main()
