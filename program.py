import os
import pandas as pd
import sqlalchemy as sa
# from dotenv import load_dotenv
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, DECIMAL, Boolean, ForeignKey
import password_hash
from base64 import b64encode
import hashlib


class Program:

    def __init__(self):
        # load_dotenv()

        # # Connection Parameters (you will sub in with your own databases values)
        # self.escapedPassword = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD"))
        # self.sqldialect = os.environ.get("DB_DIALECT")
        # self.username = os.environ.get("DB_USER")
        # self.database = os.environ.get("DB_NAME")
        # self.host = os.environ.get("DB_HOST")

        # Connection Parameters (you will sub in with your own databases values)
        self.escapedPassword = "dylan"
        self.sqldialect = "you"
        self.username = "fool"
        self.database = "pushed"
        self.host = "this to github with the info still here"

        # Build the connection string based on database specific parameters
        self.connectionString = f"{self.sqldialect}://{self.username}:{self.escapedPassword}@{self.host}/{self.database}"

        # Create a new DB engine based on our connection string
        self.engine = sa.create_engine(self.connectionString)

        self.input = None
        self.input2 = None
        self.email = None
        self.password = None
        self.salt = None
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
        self.input = input("Login with your email and password: <email> <password>\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) == 1 or len(command) > 2:
            print("Please follow the correct format\n")
            self.login()
        else:
            self.email = command[0]
            self.password = command[1]
            if not self.emailChecker(self.email):
                print("The information entered is incorrect\n")
                self.login()
            if self.passwordChecker(self.email, self.password):
                print("Login Successful!\n")
                self.home()
            else:
                print("The information entered is incorrect\n")
                self.login()

    def register(self):
        self.input = input("Register your <email> <password>\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) == 1 or len(command) > 2:
            print("Please follow the correct format\n")
            self.register()
        else:
            self.email = command[0]
            if not self.emailChecker(self.email):
                self.password, self.salt = password_hash.create_hash(command[1])
                self.password = self.password.hex()
                self.salt = self.salt.hex()
                firstname = input("Enter first name\nCancel\nQuit\n\n")
                if firstname.lower() == "c" or firstname.lower() == "cancel":
                    self.start()
                if firstname.lower() == "q" or firstname.lower() == "quit":
                    quit()
                lastname = input("Enter last name\nCancel\nQuit\n\n")
                if lastname.lower() == "c" or lastname.lower() == "cancel":
                    self.start()
                if lastname.lower() == "q" or lastname.lower() == "quit":
                    quit()
                walletname = input("Enter wallet name\nCancel\nQuit\n\n")
                if walletname.lower() == "c" or walletname.lower() == "cancel":
                    self.start()
                if walletname.lower() == "q" or walletname.lower() == "quit":
                    quit()
                metadata_obj = sa.MetaData()
                user = sa.Table("user", metadata_obj, autoload_with=self.engine)
                try:
                    with self.engine.begin() as conn:
                        conn.execute(sa.insert(user), [
                            {'firstName': [firstname],
                             'lastName': [lastname],
                             'email': [self.email],
                             'passwordHash': [str(self.password)],
                             'salt': [str(self.salt)]}
                        ],
                                     )
                except Exception as error:
                    print(f"Error returned: <<<{error}>>>")
            else:
                print("This email is already in use, please try again\n")
                self.register()
            self.start()

    def emailChecker(self, e):
        metadata_obj = sa.MetaData()
        user = sa.Table("user", metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.select(user).where(user.c.email == f"{e}"))
                for email in result:
                    return True
                return False
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")

    def passwordChecker(self, e, p):
        metadata_obj = sa.MetaData()
        user = sa.Table("user", metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.select(user).where(user.c.email == f"{e}"))
                for z in result:
                    s = f"{z[5]}"
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")
        s = bytes.fromhex(s)
        reversed = password_hash.get_hash(p, s)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.select(user).where(user.c.email == f"{e}"))
                for z in result:
                    pa = f"{z[4]}"
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")
        pa = bytes.fromhex(pa)
        return reversed == pa


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
        elif command[0].lower() == 'c' or command[0].lower() == 'change' \
                or (command[0].lower() == 'change' and
                    command[1].lower() == 'wallet'):
            self.changeWallet()
        elif command[0].lower() == 'd' or command[0].lower() == 'deposit':
            self.deposit()
        elif command[0].lower() == 'w' or command[0].lower() == 'withdraw':
            self.withdraw()
        elif command[0].lower() == 'u' or command[0].lower() == 'update' \
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
        elif command[0].lower() == 'v' or command[0].lower() == 'view' \
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
            print("idk man lol\n")
            self.betHistory()


def main():
    Program()


if __name__ == '__main__':
    main()
