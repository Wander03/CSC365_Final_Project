import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
import password_hash
from datetime import date, timedelta
import texttable as t
import pandas as pd


def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')


class Program:

    def __init__(self):
        load_dotenv()

        # Connection Parameters (you will sub in with your own databases values)
        self.escapedPassword = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD"))
        self.sqldialect = os.environ.get("DB_DIALECT")
        self.username = os.environ.get("DB_USER")
        self.database = os.environ.get("DB_NAME")
        self.host = os.environ.get("DB_HOST")

        # Build the connection string based on database specific parameters
        self.connectionString = f"{self.sqldialect}://{self.username}:{self.escapedPassword}@{self.host}/{self.database}"

        # Create a new DB engine based on our connection string
        self.engine = sa.create_engine(self.connectionString)

        self.day = date(2022, 11, 23)

        self.input = None
        self.input2 = None
        self.first = None
        self.last = None
        self.first2 = None
        self.last2 = None
        self.email = None
        self.password = None
        self.salt = None
        self.userid = None
        self.betmatch = None
        self.bettype = None
        self.betguess = None
        self.walletid = None
        self.odd1 = None
        self.odd2 = None
        self.metadata_obj = sa.MetaData()
        self.start()

    def start(self):
        clearConsole()
        self.input = input("Login\nRegister\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.start()
        elif command[0].lower() == 'l' or command[0].lower() == 'login':
            clearConsole()
            self.login()
        elif command[0].lower() == 'r' or command[0].lower() == 'register':
            clearConsole()
            self.register()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            clearConsole()
            print('Please select a valid option\n')
            self.start()

    def login(self):
        self.input = input("Login with your email and password: <email> <password>\nBack\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.login()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) == 1 or len(command) > 2:
            clearConsole()
            print("Please follow the correct format\n")
            self.login()
        else:
            self.email = command[0]
            self.password = command[1]
            if self.emailChecker(self.email):
                if self.passwordChecker(self.email, self.password):
                    self.getIds(self.email)
                    clearConsole()
                    print("Login Successful!\n")
                    self.home()
                else:
                    clearConsole()
                    print("The information entered is incorrect\n")
                    self.login()
            else:
                clearConsole()
                print("The information entered is incorrect\n")
                self.login()

    def getIds(self, e):
        user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                self.userid = conn.execute(sa.select([user.c.id]).where(user.c.email == e)).scalar()
                self.walletid = conn.execute(sa.select([wallet.c.id]).where(wallet.c.userId == self.userid)).scalar()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

    def register(self):
        clearConsole()
        self.input = input("Register your <email> <password>\nBack\nQuit\n\n")
        command = self.input.split()
        if not command:
            clearConsole()
            print("Please follow the correct format\n")
            self.register()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) == 1 or len(command) > 2:
            clearConsole()
            print("Please follow the correct format\n")
            self.register()
        else:
            self.email = command[0]
            if not self.emailChecker(self.email):
                self.password, self.salt = password_hash.create_hash(command[1])
                self.password = self.password.hex()
                self.salt = self.salt.hex()
                clearConsole()
                firstname = input("Enter first name\nCancel\nQuit\n\n")
                if firstname.lower() == "c" or firstname.lower() == "cancel":
                    clearConsole()
                    self.start()
                elif firstname.lower() == "q" or firstname.lower() == "quit":
                    quit()
                else:
                    clearConsole()
                    lastname = input("Enter last name\nCancel\nQuit\n\n")
                    if lastname.lower() == "c" or lastname.lower() == "cancel":
                        clearConsole()
                        self.start()
                    elif lastname.lower() == "q" or lastname.lower() == "quit":
                        quit()
                    else:
                        clearConsole()
                        walletname = input("Enter wallet name\nCancel\nQuit\n\n")
                        if walletname.lower() == "c" or walletname.lower() == "cancel":
                            self.start()
                        elif walletname.lower() == "q" or walletname.lower() == "quit":
                            quit()
                        else:
                            user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
                            wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
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
                                    userid = conn.execute(
                                        sa.select([user.c.id]).where(user.c.email == f"{self.email}")
                                    ).scalar()
                                    conn.execute(sa.insert(wallet), [
                                        {'userId': [userid],
                                         'name': [walletname],
                                         'amountStored': [0]}
                                    ],
                                                 )
                            except Exception as error:
                                r = 'a'
                                while r != 'y' or r != 'n':
                                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                                    if r == 'y':
                                        self.start()
                                    elif r == 'n':
                                        quit()
                            clearConsole()
                            print("Registration Successful! You may now login\n")
                            self.start()
            else:
                clearConsole()
                print("This email is already in use, please try again\n")
                self.register()

    def emailChecker(self, e):
        user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.select([user.c.email]).where(user.c.email == f"{e}")).scalar()
                return result is not None
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

    def passwordChecker(self, e, p):
        user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                pa, s = conn.execute(
                    sa.select([user.c.passwordHash, user.c.salt]).where(user.c.email == f"{e}")
                ).fetchall()[0]
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()
        s = bytes.fromhex(s)
        pa = bytes.fromhex(pa)
        retrieved = password_hash.get_hash(p, s)
        return retrieved == pa

    def payout(self):
        sql = f"""
            with matchids as (
                select distinct matchid 
                    from bets
                        join matches on matches.id = bets.matchid
                        join transactions on bets.transactionid = transactions.id
                        where date = '{self.day}'
            ), subttotals as (
              select m.matchid, bettypeid, sum(amount) subt
                from matchids as m
                    left join pool on m.matchid = pool.matchid
                where bettypeid in (1, 2)
                group by m.matchid, bettypeid
            ), odds as (
                select matchid, bettypeid, 
                case when subt = (sum(subt) over(partition by matchid))
                    then 1.2
                    when round(sum(subt) over(partition by matchid) / subt, 2) - 0.1 = 1
                    then 1.05
                    else round(sum(subt) over(partition by matchid) / subt, 2) - 0.1
                    end odds
                from subttotals
            ), winners as (
                select m.matchid, case when team1Score > team2Score then 1 else 2 end win
                    from matchids as m
                        left join results on m.matchid = results.matchid
            )
            select walletid, round(bets.amount * odds, 2) payout
                from bets
                    join matches on matches.id = bets.matchid
                    join transactions on bets.transactionid = transactions.id
                    join odds on odds.matchid = matches.id and odds.bettypeid = bets.bettypeid
                    join winners on winners.matchid = odds.matchid
                    where date = '{self.day}' and odds.bettypeid = win
            """
        sql2 = f"""
            with matchids as (
            select distinct matchid 
                from bets
                    join matches on matches.id = bets.matchid
                    join transactions on bets.transactionid = transactions.id
                    where date = '{self.day}'
            ), playerBets as (
            select m.matchid, bettypeid, amount, guess, transactionid
            from matchids as m
                left join bets on m.matchid = bets.matchid
            where bettypeid in (3, 4)
            )
            select walletid, round(p.amount * 4, 2) payout
            from playerBets as p
                left join results on p.matchid = results.matchid
                left join transactions on p.transactionid = transactions.id
            where case when bettypeid = 3 then guess = totalkills % 10 else guess = headshotcount % 10 end
            """
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        transactions = sa.Table("transactions", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql)).fetchall()

                for walletid, amount in result:

                    balance = conn.execute(
                        sa.select([wallet.c.amountStored]).where(wallet.c.id == walletid)
                    ).scalar()

                    conn.execute(sa.update(wallet).where(wallet.c.id == walletid).
                                 values(amountStored=float(balance) + float(amount))
                                 )

                    conn.execute(sa.insert(transactions), [
                        {'transactionTypeId': [4], 'walletId': [walletid], 'amount': [float(amount)]}
                    ],
                                 )

                result = conn.execute(sa.text(sql2)).fetchall()

                for walletid, amount in result:
                    balance = conn.execute(
                        sa.select([wallet.c.amountStored]).where(wallet.c.id == walletid)
                    ).scalar()

                    conn.execute(sa.update(wallet).where(wallet.c.id == walletid).
                                 values(amountStored=float(balance) + float(amount))
                                 )

                    conn.execute(sa.insert(transactions), [
                        {'transactionTypeId': [4], 'walletId': [walletid], 'amount': [float(amount)]}
                    ],
                                 )

        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

    def home(self):
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                balance = conn.execute(
                    sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                ).scalar()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        print(f"Current balance: ${balance}")

        self.input = input(f"Current Day: {self.day}\n\nBet\nHistory\nAccount\nNext Day\nLogout\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.home()
        elif command[0].lower() == 'l' or command[0].lower() == 'logout':
            clearConsole()
            self.start()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'b' or command[0].lower() == 'bet':
            clearConsole()
            self.bet()
        elif command[0].lower() == 'a' or command[0].lower() == 'account':  # transactions now merged to account
            clearConsole()
            self.account()
        elif command[0].lower() == 'h' or command[0].lower() == 'history':
            clearConsole()
            self.history()
        elif command[0].lower() == 'n' or command[0].lower() == 'next':
            clearConsole()
            self.payout()
            self.day += timedelta(days=1)
            print(f'Day advanced to {self.day}!\n')
            self.home()
        else:
            clearConsole()
            print("Please select a valid option\n")
            self.home()

    def account(self):
        self.input = input("Change Wallet\nDeposit\nWithdraw\nUpdate Password\nBack\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.account()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'c' or command[0].lower() == 'change' \
                or (command[0].lower() == 'change' and
                    command[1].lower() == 'wallet'):
            clearConsole()
            self.changeWallet()
        elif command[0].lower() == 'd' or command[0].lower() == 'deposit':
            clearConsole()
            self.deposit()
        elif command[0].lower() == 'w' or command[0].lower() == 'withdraw':
            clearConsole()
            self.withdraw()
        elif command[0].lower() == 'u' or command[0].lower() == 'update' \
                or (command[0].lower() == 'p' and
                    command[0].lower() == 'password'):
            clearConsole()
            self.oldPassword()
        else:
            clearConsole()
            print("Please select a valid option\n")
            self.account()

    def changeWallet(self):
        self.input = input("Enter new wallet name\nBack\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.changeWallet()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.account()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            walletname = self.input
            wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
            try:
                with self.engine.begin() as conn:
                    conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                 values(name=walletname)
                                 )
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
            clearConsole()
            print("Update Successful!\n")
            self.account()

    def deposit(self):
        # shows their current balance here
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        transactions = sa.Table("transactions", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                balance = conn.execute(
                    sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                ).scalar()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        print(f"Current balance: ${balance}")
        self.input = input("Enter deposit amount\nBack\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.deposit()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please enter a valid amount\n")
            self.deposit()
        else:
            try:
                depositamount = float(command[0])
                if depositamount >= 10:
                    with self.engine.begin() as conn:
                        balance = conn.execute(
                            sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                        ).scalar()
                        conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                     values(amountStored=float(balance) + depositamount)
                                     )
                        conn.execute(sa.insert(transactions), [
                            {'transactionTypeId': [2], 'walletId': [self.walletid], 'amount': [depositamount]}
                        ],
                                     )
                    clearConsole()
                    print("Deposit Successful!\n")
                    self.account()
                elif depositamount < 10:
                    clearConsole()
                    print("The minimum deposit is 10 dollars\n")
                    self.deposit()
                else:
                    clearConsole()
                    print("Please enter a valid amount\n")
                    self.deposit()
            except ValueError:
                clearConsole()
                print("Please enter a valid amount\n")
                self.deposit()

    def withdraw(self):
        # shows their current balance here
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        transactions = sa.Table("transactions", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                balance = conn.execute(
                    sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                ).scalar()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        print(f"Current balance: ${balance}")
        self.input = input("Enter withdrawal amount\nBack\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.withdraw()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please enter a valid amount\n")
            self.deposit()
        else:
            try:
                withdrawamount = float(command[0])
                if withdrawamount > float(balance):
                    clearConsole()
                    print("Insufficient balance\n")
                    self.withdraw()
                elif withdrawamount <= 0:
                    clearConsole()
                    print("Please enter a valid amount\n")
                    self.withdraw()
                elif float(balance) < 50:
                    clearConsole()
                    print("A minimum balance of 50 dollars is required to make a withdrawal\n")
                    self.withdraw()
                else:
                    with self.engine.begin() as conn:
                        balance = conn.execute(
                            sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                        ).scalar()
                        conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                     values(amountStored=float(balance) - withdrawamount)
                                     )
                        conn.execute(sa.insert(transactions), [
                            {'transactionTypeId': [1], 'walletId': [self.walletid], 'amount': [withdrawamount]}
                        ],
                                     )
                    clearConsole()
                    print("Withdrawal Successful!\n")
                    self.account()
            except ValueError:
                clearConsole()
                print("Please enter a valid amount\n")
                self.withdraw()

    def oldPassword(self):
        self.input = input("Enter old password\nBack\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.oldPassword()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Incorrect information\n")
            self.oldPassword()
        else:
            if self.passwordChecker(self.email, self.input):
                clearConsole()
                self.updatePassword()
            else:
                clearConsole()
                print("Incorrect information\n")
                self.oldPassword()

    def updatePassword(self):
        self.input = input("Enter new password\nCancel\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.updatePassword()
        elif command[0].lower() == 'c' or command[0].lower() == 'cancel':
            clearConsole()
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:  # confirms password here
            self.input2 = input("\nConfirm your new password\nCancel\nQuit\n\n")
            command2 = self.input2.split()
            if command2[0].lower() == 'c' or command2[0].lower() == 'cancel':
                clearConsole()
                self.account()
            elif command2[0].lower() == 'q' or command2[0].lower() == 'quit':
                quit()
            else:
                if command[0] == command2[0]:
                    self.password, self.salt = password_hash.create_hash(command[0])
                    self.password = self.password.hex()
                    self.salt = self.salt.hex()

                    user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
                    with self.engine.begin() as conn:

                        conn.execute(sa.update(user).where(user.c.id == self.userid).
                                     values(passwordHash=self.password,
                                            salt=self.salt)
                                     )
                    clearConsole()
                    print("Password update successful!\n")
                    self.account()
                else:
                    clearConsole()
                    print("The passwords do not match\n")
                    self.updatePassword()

    def odds_calc(self):
        sql = f"""
              select sum(amount)
                from pool
                where matchid = {self.betmatch} and bettypeid in (1, 2)
                group by bettypeid
                """
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql)).fetchall()
                if len(result) != 2 or result[0][0] == 0 or result[1][0] == 0:
                    self.odd1 = 1.2
                    self.odd2 = 1.2
                else:
                    self.odd1 = float(round((result[0][0] + result[1][0]) / result[0][0], 2)) - 0.1
                    self.odd2 = float(round((result[0][0] + result[1][0]) / result[1][0], 2)) - 0.1
                    if self.odd1 == 1:
                        self.odd1 = 1.05
                    if self.odd2 == 1:
                        self.odd2 = 1.05

        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

    def bet(self):
        self.input = input("Place bets\nView Upcoming Matches\nBack\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.bet()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'p' or command[0].lower() == 'place' \
                or (command[0].lower() == 'place' and
                    command[1].lower() == 'bets'):
            clearConsole()
            self.first = 1
            self.last = 10
            self.placeBet()
        elif command[0].lower() == 'v' or command[0].lower() == 'view' \
                or command[0].lower() == 'm' or command[0].lower() == 'matches':
            clearConsole()
            self.first = 1
            self.last = 10
            self.viewUpcomingMatch()
        else:
            clearConsole()
            print("Please select a valid option\n")
            self.bet()

    def placeBet(self):
        sql = f"""
                    with counts as (
                    select id, row_number() over(order by `date`) num
                        from matches
                        where `date` >= '{self.day}'
                    )
                    select matches.id, date, t1.teamname, t2.teamname, m.name
                    from matches
                        inner join teamId as t1 on matches.team1Id = t1.id
                        inner join teamId as t2 on matches.team2Id = t2.id
                        inner join map as m on matches.mapId = m.id
                        inner join counts as c on c.id = matches.id
                    where `date` >= '{self.day}' and num between {self.first} and {self.last}
                    order by `date`
                """
        upcoming = []
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                tab = t.Texttable()
                headings = ['Match Id', 'Date', 'Team 1', 'Team 2', 'Map']
                tab.header(headings)

                for row in result:
                    tab.add_row(row)
                    upcoming.append(row[0])
                tab.set_cols_width([10, 15, 15, 15, 15])
                print(tab.draw())
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        matches = sa.Table("matches", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                upcoming = conn.execute(
                    sa.select([matches.c.id]).where(matches.c.date >= self.day)
                ).scalars().all()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        self.input = input(f"Matches {self.first} to {self.last}\n\nEnter match id"
                           "\nEnter Next to view next 10 matches"
                           "\nEnter Previous to view previous 10 matches"
                           "\nBack\nHome"
                           "\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.placeBet()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif command[0].lower() == 'n' or command[0].lower() == 'next':
            if self.first == 41:
                clearConsole()
                print('This is the last page\n')
                self.viewUpcomingMatch()
            self.first += 10
            self.last += 10
            clearConsole()
            self.placeBet()
        elif command[0].lower() == 'p' or command[0].lower() == 'previous':
            if self.first == 1:
                clearConsole()
                print('This is the first page\n')
                self.viewUpcomingMatch()
            self.first -= 10
            self.last -= 10
            clearConsole()
            self.placeBet()
        else:
            try:
                matchid = int(command[0])
                if matchid not in upcoming:
                    clearConsole()
                    print("Please select a valid match\n")
                    self.placeBet()
                else:
                    self.betmatch = matchid
                    clearConsole()
                    self.placeBet2()
            except ValueError:
                clearConsole()
                print("Please select a valid match\n")
                self.placeBet()

    def placeBet2(self):
        sql = f"""
            select matches.id, date, t1.teamname, t2.teamname, m.name
            from matches
                inner join teamId as t1 on matches.team1Id = t1.id
                inner join teamId as t2 on matches.team2Id = t2.id
                inner join map as m on matches.mapId = m.id
            where matches.id = {self.betmatch}
        """
        upcoming = []
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                tab = t.Texttable()
                headings = ['Match Id', 'Date', 'Team 1', 'Team 2', 'Map']
                tab.header(headings)

                for row in result:
                    tab.add_row(row)
                    upcoming.append(row[0])
                tab.set_cols_width([10, 15, 15, 15, 15])
                print(tab.draw())
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()
        self.odds_calc()
        self.input = input(f"\nChoose your bet type:\n"
                           f"1: Team 1 wins (odds: {round(self.odd1, 2)}x)\n"
                           f"2: Team 2 wins (odds: {round(self.odd2, 2)}x)\n"
                           f"3: Last digit in total kills (odds: 4.00x)\n"
                           f"4: Last digit in total headshots (odds: 4.00x)\n"
                           f"Back\nHome\nQuit\n\n")
        command = self.input.split()
        if not command:
            clearConsole()
            self.placeBet2()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.placeBet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please choose a valid bet type\n")
            self.placeBet2()
        elif command[0] == "1" or command[0] == "2":
            self.bettype = int(command[0])
            clearConsole()
            self.placeBet3()
        elif command[0] == "3" or command[0] == "4":
            clearConsole()
            self.input2 = input("Enter your guess [0-9]\n\n")
            try:
                guess = int(self.input2)
                if guess < 0 or guess > 9:
                    clearConsole()
                    print("Please enter a valid guess\n")
                    self.placeBet2()
                else:
                    self.bettype = int(command[0])
                    self.betguess = guess
                    clearConsole()
                    self.placeBet3()
            except ValueError:
                clearConsole()
                print("Please enter a valid guess\n")
                self.placeBet2()
        else:
            clearConsole()
            print("Please choose a valid bet type\n")
            self.placeBet2()

    def placeBet3(self):
        wallet = sa.Table("wallet", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                balance = conn.execute(
                    sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                ).scalar()
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()
        print(f'Current Balance: ${balance}')
        self.input = input("Enter bet amount\nBack\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.placeBet3()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.placeBet2()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please enter a valid bet amount\n")
            self.placeBet3()
        else:
            try:
                betamount = float(command[0])
                if betamount > balance:
                    clearConsole()
                    print("Insufficient funds\n")
                    self.placeBet3()
                elif betamount < 0:
                    clearConsole()
                    print("Please enter a valid bet amount\n")
                    self.placeBet3()
                else:
                    pool = sa.Table("pool", self.metadata_obj, autoload_with=self.engine)
                    transactions = sa.Table("transactions", self.metadata_obj, autoload_with=self.engine)
                    bets = sa.Table("bets", self.metadata_obj, autoload_with=self.engine)
                    with self.engine.begin() as conn:
                        balance = conn.execute(
                            sa.select([wallet.c.amountStored]).where(wallet.c.userId == self.userid)
                        ).scalar()
                        conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                     values(amountStored=float(balance) - betamount)
                                     )
                        conn.execute(sa.insert(pool), [
                            {'matchId': [self.betmatch], 'betTypeId': [self.bettype], 'amount': [betamount]}
                        ],
                                     )
                        conn.execute(sa.insert(transactions), [
                            {'transactionTypeId': [3], 'walletId': [self.walletid], 'amount': [betamount]}
                        ],
                                     )
                        tid = conn.execute(
                            sa.select([transactions.c.id]).
                            where(transactions.c.walletId == self.walletid).
                            order_by(transactions.c.id.desc())
                        ).scalar()

                        conn.execute(sa.insert(bets), [
                            {'userId': [self.userid],
                             'transactionId': [tid],
                             'matchId': [self.betmatch],
                             'betTypeId': [self.bettype],
                             'guess': [self.betguess],
                             'amount': [betamount]}
                        ],
                                     )
                    clearConsole()
                    print("Bet successfully placed!\n")
                    self.bet()
            except ValueError:
                clearConsole()
                print("Please enter a valid bet amount\n")
                self.placeBet3()

    def viewUpcomingMatch(self):
        # brings up a list of upcoming matches first
        sql = f"""
            with counts as (
            select id, row_number() over(order by `date`) num
                from matches
                where `date` >= '{self.day}'
            )
            select matches.id, date, t1.teamname, t2.teamname, m.name
            from matches
                inner join teamId as t1 on matches.team1Id = t1.id
                inner join teamId as t2 on matches.team2Id = t2.id
                inner join map as m on matches.mapId = m.id
                inner join counts as c on c.id = matches.id
            where `date` >= '{self.day}' and num between {self.first} and {self.last}
            order by `date`
        """
        upcoming = []
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                tab = t.Texttable()
                headings = ['Match Id', 'Date', 'Team 1', 'Team 2', 'Map']
                tab.header(headings)

                for row in result:
                    tab.add_row(row)
                    upcoming.append(row[0])
                tab.set_cols_width([10, 15, 15, 15, 15])
                print(tab.draw())
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        self.input = input(f"Matches {self.first} to {self.last}\n\nEnter a match id for more details"
                           f"\nEnter Next to view next 10 matches"
                           f"\nEnter Previous to view previous 10 matches"
                           f"\nBack\nHome"
                           f"\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.viewUpcomingMatch()
        elif command[0].lower() == 'n' or command[0].lower() == 'next':
            if self.first == 41:
                clearConsole()
                print('This is the last page\n')
                self.viewUpcomingMatch()
            self.first += 10
            self.last += 10
            clearConsole()
            self.viewUpcomingMatch()
        elif command[0].lower() == 'p' or command[0].lower() == 'previous':
            if self.first == 1:
                clearConsole()
                print('This is the first page\n')
                self.viewUpcomingMatch()
            self.first -= 10
            self.last -= 10
            clearConsole()
            self.viewUpcomingMatch()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please select a valid match\n")
            self.viewUpcomingMatch()
        else:
            try:
                matchid = int(command[0])
                if matchid not in upcoming:
                    clearConsole()
                    print("Please select a valid match\n")
                    self.viewUpcomingMatch()
                else:
                    clearConsole()
                    sqlteam1 = f"""
                            select distinct matches.id, p1.playername as team1players
                            from matches 
                                inner join teams as t1 on matches.team1Id = t1.teamid
                                inner join player as p1 on t1.playerId = p1.id
                            where matches.id = {matchid}
                            order by matches.id
                            """
                    sqlteam2 = f"""
                            select distinct matches.id, p2.playername as team2players
                                from matches 
                                    inner join teams as t2 on matches.team2Id = t2.teamid
                                    inner join player as p2 on t2.playerId = p2.id
                                where matches.id = {matchid}
                                order by matches.id
                            """
                    try:
                        with self.engine.begin() as conn:
                            result = conn.execute(sa.text(sqlteam1))
                            print("Team 1 Players:")
                            for id, players in result:
                                print(f"{players}")

                            result2 = conn.execute(sa.text(sqlteam2))
                            print("\nTeam 2 Players:")
                            for id, players in result2:
                                print(f"{players}")

                        self.input = input('\nBack\nHome\nQuit')
                        command = self.input.split()

                        if not command or command[0].lower() == 'b' or command[0].lower() == 'back':
                            clearConsole()
                            self.viewUpcomingMatch()
                        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
                            quit()
                        elif command[0].lower() == 'h' or command[0].lower() == 'home':
                            clearConsole()
                            self.home()

                    except Exception as error:
                        r = 'a'
                        while r != 'y' or r != 'n':
                            r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                            if r == 'y':
                                self.start()
                            elif r == 'n':
                                quit()
            except ValueError:
                clearConsole()
                print("Please select a valid match\n")
                self.viewUpcomingMatch()
        self.viewUpcomingMatch()

    def history(self):
        self.input = input("Match History\nPersonal History\nBack\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.history()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'm' or command[0].lower() == 'match':
            self.first = 1
            self.last = 10
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'p' or command[0].lower() == 'personal':
            clearConsole()
            self.betHistory()
        else:
            clearConsole()
            print("Please select a valid option\n")
            self.history()

    def mapMatchHistory(self, n):
        sql = f"""
            with counts as (
                select matches.id, row_number() over(order by `date` desc) num
                    from matches
                    inner join map as m on matches.mapId = m.id
                    where `date` < '{self.day}' and m.id = {n}
                )
              select results.matchid, date, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, totalkills, headshotcount
                from results
                    inner join matches on results.matchid = matches.id
                    inner join teamId as t1 on matches.team1Id = t1.id
                    inner join teamId as t2 on matches.team2Id = t2.id
                    inner join map as m on matches.mapId = m.id
                    inner join counts as c on matches.id = c.id
                where date < '{self.day}' and m.id = {n} and num between {self.first2} and {self.last2}
                order by num              
            """
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                tab = t.Texttable()
                headings = ['Match Id', 'Date', 'Team 1', 'Team 1 Score',
                            'Team 2', 'Team 2 Score', 'Map', 'Total Kills',
                            'Headshot Count']
                tab.header(headings)
                for row in result:
                    tab.add_row(row)
                tab.set_cols_width([10, 10, 15, 10, 15, 10, 15, 10, 10])
                print(tab.draw())
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()

        self.input = input(f"Matches {self.first2} to {self.last2}\n\n"
                           f"\nEnter Next to view next 10 matches"
                           f"\nEnter Previous to view previous 10 matches"
                           f"\nBack\nHome"
                           f"\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.mapMatchHistory(n)
        elif command[0].lower() == 'n' or command[0].lower() == 'next':
            if self.first2 == 991:
                clearConsole()
                print('This is the last page\n')
                self.mapMatchHistory(n)
            self.first2 += 10
            self.last2 += 10
            clearConsole()
            self.mapMatchHistory(n)
        elif command[0].lower() == 'p' or command[0].lower() == 'previous':
            if self.first2 == 1:
                clearConsole()
                print('This is the first page\n')
                self.mapMatchHistory(n)
            self.first2 -= 10
            self.last2 -= 10
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        else:
            print('Please enter a valid option')
            self.mapMatchHistory(n)

    def matchHistory(self):
        sql = f"""
        with counts as (
            select id, row_number() over(order by `date` desc) num
                from matches
                where `date` < '{self.day}'
            )
            select results.matchid, date, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, totalkills, headshotcount
            from results
                inner join matches on results.matchid = matches.id
                inner join teamId as t1 on matches.team1Id = t1.id
                inner join teamId as t2 on matches.team2Id = t2.id
                inner join map as m on matches.mapId = m.id
                inner join counts as c on matches.id = c.id
            where date < '{self.day}' and num between {self.first} and {self.last}
            order by num
            """
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                tab = t.Texttable()
                headings = ['Match Id', 'Date', 'Team 1', 'Team 1 Score',
                            'Team 2', 'Team 2 Score', 'Map', 'Total Kills',
                            'Headshot Count']
                tab.header(headings)
                for row in result:
                    tab.add_row(row)
                tab.set_cols_width([10, 10, 15, 10, 15, 10, 15, 10, 10])
                print(tab.draw())
        except Exception as error:
            r = 'a'
            while r != 'y' or r != 'n':
                r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                if r == 'y':
                    self.start()
                elif r == 'n':
                    quit()
        # brings up a list of matches played first
        self.input = input(f"Matches {self.first} to {self.last}\n"
                           f"\nEnter Next to view next 10 matches"
                           f"\nEnter Previous to view previous 10 matches\n"
                           f"Filter Options:\n"
                           f"  1: Map\n"
                           f"  2: Match ID\n"
                           f"Back\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'n' or command[0].lower() == 'next':
            if self.first == 991:
                clearConsole()
                print('This is the last page\n')
                self.matchHistory()
            self.first += 10
            self.last += 10
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'p' or command[0].lower() == 'previous':
            if self.first == 1:
                clearConsole()
                print('This is the first page\n')
                self.matchHistory()
            self.first -= 10
            self.last -= 10
            clearConsole()
            self.matchHistory()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please enter a valid filter option\n")
            self.matchHistory()
        elif command[0] == "1":
            clearConsole()
            maps = sa.Table("map", self.metadata_obj, autoload_with=self.engine)
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.select(maps).order_by(maps.c.id))
                    for id, name in result:
                        print(f"{id}: {name}")
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
            self.input2 = input("Enter the map ID\n\n")
            command2 = self.input2.split()
            if len(command2) > 1:
                clearConsole()
                print("Please enter a valid map ID\n")
                self.matchHistory()
            else:
                try:
                    mwant = int(command2[0])
                    self.first2 = 1
                    self.last2 = 10
                    clearConsole()
                    self.mapMatchHistory(mwant)
                except ValueError:
                    clearConsole()
                    print("Please enter a valid map ID\n")
                    self.matchHistory()
        elif command[0] == "2":
            clearConsole()
            self.input2 = input("Enter the Match ID\n\n")
            command2 = self.input2.split()
            if len(command2) > 1:
                clearConsole()
                print("Please enter a valid Match ID\n")
                self.matchHistory()
            else:
                try:
                    mwant = int(command2[0])
                    sql2 = f"""
                                 select results.matchid, date, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, totalkills, headshotcount
                                   from results
                                       inner join matches on results.matchid = matches.id
                                       inner join teamId as t1 on matches.team1Id = t1.id
                                       inner join teamId as t2 on matches.team2Id = t2.id
                                       inner join map as m on matches.mapId = m.id
                                   where date < '{self.day}' and results.matchid = {mwant}                
                               """
                    try:
                        with self.engine.begin() as conn:
                            result = conn.execute(sa.text(sql2))
                            tab = t.Texttable()
                            headings = ['Match Id', 'Date', 'Team 1', 'Team 1 Score',
                                        'Team 2', 'Team 2 Score', 'Map', 'Total Kills',
                                        'Headshot Count']
                            tab.header(headings)
                            tab.set_cols_width([10, 10, 15, 10, 15, 10, 15, 10, 10])
                            for row in result:
                                tab.add_row(row)
                            print(tab.draw())
                    except Exception as error:
                        r = 'a'
                        while r != 'y' or r != 'n':
                            r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                            if r == 'y':
                                self.start()
                            elif r == 'n':
                                quit()

                    self.input = input("\nBack\nHome\nQuit\n\n")
                    command = self.input.split()

                    if not command:
                        clearConsole()
                        self.matchHistory()
                    elif command[0].lower() == 'b' or command[0].lower() == 'back':
                        clearConsole()
                        self.matchHistory()
                    elif command[0].lower() == 'q' or command[0].lower() == 'quit':
                        quit()
                    elif command[0].lower() == 'h' or command[0].lower() == 'home':
                        clearConsole()
                        self.home()
                    else:
                        clearConsole()
                        self.matchHistory()

                except ValueError:
                    clearConsole()
                    print("Please enter a valid Match ID\n")
                    self.matchHistory()
        else:
            clearConsole()
            print("Please select a valid match\n")
            self.matchHistory()

    def betHistory(self):
        # brings up a list of past bets, includes winnings and losings
        self.input = input("1: Bet History\n"
                           "2: Deposit History\n"
                           "3: Withdrawal History\n"
                           "4: Payout History\n"
                           "5: Any Transactions over X Amount\n"
                           "Back\nHome\nQuit\n\n")
        command = self.input.split()

        if not command:
            clearConsole()
            self.betHistory()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
            clearConsole()
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'h' or command[0].lower() == 'home':
            clearConsole()
            self.home()
        elif len(command) > 1:
            clearConsole()
            print("Please enter a valid option\n")
            self.betHistory()
        elif command[0] == "1":
            s = f"""
                select transactions.id, matchid, betType.type, guess, bets.amount 
                from bets 
                    inner join transactions on bets.transactionid = transactions.id
                    inner join betType on bets.bettypeid = betType.id
                where walletid = {self.walletid} and transactiontypeid = 3             
                """
            try:
                clearConsole()
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    tab = t.Texttable()
                    headings = ['Transaction Id', 'Match Id', 'Type of Bet', 'Guess',
                                'Bet Amount ($)']
                    tab.header(headings)
                    for row in result:
                        tab.add_row(row)
                    tab.set_cols_width([11, 10, 10, 10, 10])
                    print(tab.draw())
                    print()
                    self.betHistory()
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
        elif command[0] == "2":
            s = f"""
                  select id, amount from transactions
                    where walletid = {self.walletid} and transactiontypeid = 2              
                """
            clearConsole()
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    tab = t.Texttable()
                    headings = ['Transaction Id', 'Amount ($)']
                    tab.header(headings)
                    for row in result:
                        tab.add_row(row)
                    tab.set_cols_width([11, 10])
                    print(tab.draw())
                    print()
                    self.betHistory()
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
        elif command[0] == "3":
            s = f"""
                  select id, amount from transactions
                    where walletid = {self.walletid} and transactiontypeid = 1              
                       """
            clearConsole()
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    tab = t.Texttable()
                    headings = ['Transaction Id', 'Amount ($)']
                    tab.header(headings)
                    for row in result:
                        tab.add_row(row)
                    tab.set_cols_width([11, 10])
                    print(tab.draw())
                    print()
                    self.betHistory()
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
        elif command[0] == "4":
            s = f"""
                  select id, amount from transactions
                    where walletid = {self.walletid} and transactiontypeid = 4              
                """
            clearConsole()
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    tab = t.Texttable()
                    headings = ['Transaction Id', 'Amount ($)']
                    tab.header(headings)
                    for row in result:
                        tab.add_row(row)
                    tab.set_cols_width([11, 10])
                    print(tab.draw())
                    print()
                    self.betHistory()
            except Exception as error:
                r = 'a'
                while r != 'y' or r != 'n':
                    r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                    if r == 'y':
                        self.start()
                    elif r == 'n':
                        quit()
        elif command[0] == "5":
            clearConsole()
            self.input2 = input("Enter an amount\n\n")
            try:
                a = float(self.input2)
            except ValueError:
                clearConsole()
                print("Please enter a valid amount")
                self.betHistory()
            if a >= 0:
                s = f"""
                      select t.id, type, amount from transactions as t
                        join transactionType as tt on t.transactiontypeid = tt.id 
                        where walletid = {self.walletid} and amount >= {a}             
                    """
                try:
                    with self.engine.begin() as conn:
                        result = conn.execute(sa.text(s))
                        tab = t.Texttable()
                        headings = ['Transaction Id', 'Type of Transaction', 'Amount ($)']
                        tab.header(headings)
                        for row in result:
                            tab.add_row(row)
                        tab.set_cols_width([11, 11, 10])
                        print(tab.draw())
                        print()
                        self.betHistory()
                except Exception as error:
                    r = 'a'
                    while r != 'y' or r != 'n':
                        r = input(f"Error returned: <<<{error}>>>\nWould you like to restart? (y/n)")
                        if r == 'y':
                            self.start()
                        elif r == 'n':
                            quit()
            else:
                clearConsole()
                print("Please enter a valid amount")
                self.betHistory()
        else:
            clearConsole()
            print("Please enter a valid option")
            self.betHistory()


def main():
    Program()


if __name__ == '__main__':
    main()
