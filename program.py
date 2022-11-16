import pandas as pd


class Program:

    def __init__(self):
        self.input = None
        self.input2 = None
        self.start()

    def start(self):
        self.input = input("Login\nRegister\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'l' or command[0].lower() == 'login':
            self.login()
        elif command[0].lower() == 'r' or command[0].lower() == 'register':
            self.register()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print('Please select a valid option\n')
            self.start()

    def login(self):
        self.input = input("Login with your email and password: <email> <passowrd>\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0] == 'hacks' and command[1] == '****':
            self.home()
        else:
            print("The information entered is not correct, please try again\n")
            self.login()

    def register(self):
        self.input = input("Register your email and password\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print("The email is already in use, please try again\n")
            self.login()

    def home(self):
        self.input = input("Bet\nHistory\nAccount\nLogout\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'l' or command[0].lower() == 'logout':
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'b' or command[0].lower() == 'bet':
            self.bet()
        elif command[0].lower() == 'a' or command[0].lower() == 'account':  # transactions now merged to account
            self.account()
        elif command[0].lower() == 'h' or command[0].lower() == 'history':
            self.history()
        else:
            print("Please select a valid option\n")
            self.home()

    def account(self):
        self.input = input("Change Wallet\nDeposit\nWithdraw\nUpdate Password\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'c' or command[0].lower() == 'change'\
                or (command[0].lower() == 'change' and
                    command[1].lower() == 'wallet'):
            self.changeWallet()
        elif command[0].lower() == 'd' or command[0].lower() == 'deposit':
            self.deposit()
        elif command[0].lower() == 'w' or command[0].lower() == 'withdraw':
            self.withdraw()
        elif command[0].lower() == 'u' or command[0].lower() == 'update'\
                or (command[0].lower() == 'p' and
                    command[0].lower() == 'password'):
            self.password()
        else:
            print("Please select a valid option\n")
            self.account()

    def changeWallet(self):
        self.input = input("Insert new information\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print("Please select a valid option\n")
            self.changeWallet()

    def deposit(self):
        # shows their current balance here
        self.input = input("Enter deposit amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print("Please enter a valid amount\n")
            self.deposit()

    def withdraw(self):
        # shows their current balance here
        self.input = input("Enter withdrawal amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print("Insufficient balance\n")
            self.withdraw()

    def password(self):
        self.input = input("Enter old password\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':  # checks to see if password is a match
            self.updatePassword()
        else:
            print("Incorrect information\n")
            self.password()

    def updatePassword(self):
        self.input = input("Enter new password\nCancel\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'c' or command[0].lower() == 'cancel':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':  # confirms password here
            self.input2 = input("Confirm your new password\nCancel\nQuit\n\n")
        else:
            print("Enter a stronger password\n")
            self.updatePassword()

    def bet(self):
        self.input = input("Place bets\nView Upcoming Matches\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'p' or command[0].lower() == 'place' \
                or (command[0].lower() == 'place' and
                    command[1].lower() == 'bets'):
            self.placeBet()
        elif command[0].lower() == 'v' or command[0].lower() == 'view'\
                or command[0].lower() == 'm' or command[0].lower() == 'matches':
            self.viewUpcomingMatch()
        else:
            print("Please select a valid option\n")
            self.bet()

    def placeBet(self):
        self.input = input("Enter match id\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':
            # confirms match id is correct and exists
            self.placeBet2()
        else:
            print("Please select a valid match\n")
            self.placeBet()

    def placeBet2(self):
        self.input = input("Enter bet amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.placeBet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':
            # places bet here into database
            self.placeBet2()  # place holder
        else:
            print("Insufficient funds\n")
            self.placeBet2()

    def viewUpcomingMatch(self):
        # brings up a list of upcoming matches first
        self.input = input("Enter match id for more details\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':
            # brings up list of players playing, as well as odds for each team
            self.viewUpcomingMatch()  # place holder
        else:
            print("Please select a valid match\n")
            self.viewUpcomingMatch()

    def history(self):
        self.input = input("Match History\nPersonal History\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'm' or command[0].lower() == 'match':
            self.matchHistory()
        elif command[0].lower() == 'p' or command[0].lower() == 'personal':
            self.betHistory()
        else:
            print("Please select a valid option\n")
            self.history()

    def matchHistory(self):
        # brings up a list of matches played first
        self.input = input("Enter match id for more details\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 't' or command[0].lower() == 'temp':
            # brings up the list of players, as well as final odds
            self.matchHistory()  # place holder
        else:
            print("Please select a valid match\n")
            self.matchHistory()

    def betHistory(self):
        # brings up a list of past bets, includes winnings and losings
        self.input = input("I have no clue what goes here yet lmao\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            print("idk man\n")
            self.betHistory()






def main():
    Program()


if __name__ == '__main__':
    main()
