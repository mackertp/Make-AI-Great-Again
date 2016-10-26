"""
Debate analyzer project

Preston Mackert, Dylan Telford, Alexis Grebenok, Jerry Daigler
"""
from __future__ import print_function
import sys


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

main()