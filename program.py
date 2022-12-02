import os
import urllib.parse

import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv
import password_hash


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

        self.input = None
        self.input2 = None
        self.email = None
        self.password = None
        self.salt = None
        self.userid = None
        self.betmatch = None
        self.bettype = None
        self.betguess = None
        self.walletid = None
        self.metadata_obj = sa.MetaData()
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
            if self.emailChecker(self.email):
                if self.passwordChecker(self.email, self.password):
                    self.getIds(self.email)
                    print("Login Successful!\n")
                    self.home()
                else:
                    print("The information entered is incorrect\n")
                    self.login()
            else:
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
            print(f"Error returned: <<<{error}>>>")

    def register(self):
        self.input = input("Register your <email> <password>\nBack\nQuit\n\n")
        command = self.input.split()
        if not command:
            print("Please follow the correct format\n")
            self.register()
        elif command[0].lower() == 'b' or command[0].lower() == 'back':
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
                elif firstname.lower() == "q" or firstname.lower() == "quit":
                    quit()
                else:
                    lastname = input("Enter last name\nCancel\nQuit\n\n")
                    if lastname.lower() == "c" or lastname.lower() == "cancel":
                        self.start()
                    elif lastname.lower() == "q" or lastname.lower() == "quit":
                        quit()
                    else:
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
                                print(f"Error returned: <<<{error}>>>")
                            print("Registration Successful! You may now login\n")
                            self.start()
            else:
                print("This email is already in use, please try again\n")
                self.register()

    def emailChecker(self, e):
        user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.select([user.c.email]).where(user.c.email == f"{e}")).scalar()
                return result is not None
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")

    def passwordChecker(self, e, p):
        user = sa.Table("user", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                pa, s = conn.execute(
                    sa.select([user.c.passwordHash, user.c.salt]).where(user.c.email == f"{e}")
                ).fetchall()[0]
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")
        s = bytes.fromhex(s)
        pa = bytes.fromhex(pa)
        retrieved = password_hash.get_hash(p, s)
        return retrieved == pa

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
            self.oldPassword()
        else:
            print("Please select a valid option\n")
            self.account()

    def changeWallet(self):
        self.input = input("Enter new wallet name\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
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
                print(f"Error returned: <<<{error}>>>")
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
            print(f"Error returned: <<<{error}>>>")

        print(f"Current balance: {balance}")
        self.input = input("Enter deposit amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please enter a valid amount\n")
            self.deposit()
        else:
            try:
                depositamount = float(command[0])
                if depositamount >= 10:
                    with self.engine.begin() as conn:

                        conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                     values(amountStored=float(balance) + depositamount)
                                     )
                        conn.execute(sa.insert(transactions), [
                            {'transactionTypeId': [2], 'walletId': [self.walletid], 'amount': [depositamount]}
                        ],
                                     )
                    print("Deposit Successful!\n")
                    self.account()
                elif depositamount < 10:
                    print("The minimum deposit is 10 dollars\n")
                    self.deposit()
                else:
                    print("Please enter a valid amount\n")
                    self.deposit()
            except ValueError:
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
            print(f"Error returned: <<<{error}>>>")

        print(f"Current balance: {balance}")
        self.input = input("Enter withdrawal amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please enter a valid amount\n")
            self.deposit()
        else:
            try:
                withdrawamount = float(command[0])
                if withdrawamount > float(balance):
                    print("Insufficient balance\n")
                    self.withdraw()
                elif withdrawamount <= 0:
                    print("Please enter a valid amount\n")
                    self.withdraw()
                elif float(balance) < 50:
                    print("A minimum balance of 50 dollars is required to make a withdrawal\n")
                    self.withdraw()
                else:
                    with self.engine.begin() as conn:

                        conn.execute(sa.update(wallet).where(wallet.c.userId == self.userid).
                                     values(amountStored=float(balance) - withdrawamount)
                                     )
                        conn.execute(sa.insert(transactions), [
                            {'transactionTypeId': [1], 'walletId': [self.walletid], 'amount': [withdrawamount]}
                        ],
                                     )
                    print("Withdrawal Successful!\n")
                    self.account()
            except ValueError:
                print("Please enter a valid amount\n")
                self.withdraw()

    def oldPassword(self):
        self.input = input("Enter old password\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Incorrect information\n")
            self.oldPassword()
        else:
            if self.passwordChecker(self.email, self.input):
                self.updatePassword()
            else:
                print("Incorrect information\n")
                self.oldPassword()

    def updatePassword(self):
        self.input = input("Enter new password\nCancel\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'c' or command[0].lower() == 'cancel':
            self.account()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:  # confirms password here
            self.input2 = input("Confirm your new password\nCancel\nQuit\n\n")
            command2 = self.input2.split()
            if command2[0].lower() == 'c' or command2[0].lower() == 'cancel':
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
                    print("Password update successful!\n")
                    self.account()
                else:
                    print("The passwords do not match\n")
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
        matches = sa.Table("matches", self.metadata_obj, autoload_with=self.engine)
        try:
            with self.engine.begin() as conn:
                upcoming = conn.execute(
                    sa.select([matches.c.id]).where(matches.c.date >= pd.Timestamp.today())
                ).scalars().all()
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")

        self.input = input("Enter match id\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        else:
            try:
                matchid = int(command[0])
                if matchid not in upcoming:
                    print("Please select a valid match\n")
                    self.placeBet()
                else:
                    self.betmatch = matchid
                    self.placeBet2()
            except ValueError:
                print("Please select a valid match\n")
                self.placeBet()

    def placeBet2(self):
        self.input = input("Choose your bet type:\n"
                           "1: Team 1 wins\n"
                           "2: Team 2 wins\n"
                           "3: Last digit in total kills\n"
                           "4: Last digit in total headshots\n"
                           "Back\nQuit\n\n")
        command = self.input.split()
        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.placeBet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please choose a valid bet type\n")
            self.placeBet2()
        elif command[0] == "1" or command[0] == "2":
            self.bettype = int(command[0])
            self.placeBet3()
        elif command[0] == "3" or command[0] == "4":
            self.input2 = input("Enter your guess [0-9]\n\n")
            try:
                guess = int(self.input2)
                if guess < 0 or guess > 9:
                    print("Please enter a valid guess\n")
                    self.placeBet2()
                else:
                    self.bettype = int(command[0])
                    self.betguess = guess
                    self.placeBet3()
            except ValueError:
                print("Please enter a valid guess\n")
                self.placeBet2()
        else:
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
            print(f"Error returned: <<<{error}>>>")

        self.input = input("Enter bet amount\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.placeBet2()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please enter a valid bet amount\n")
            self.placeBet3()
        else:
            try:
                betamount = float(command[0])
                if betamount > balance:
                    print("Insufficient funds\n")
                    self.placeBet3()
                elif betamount < 0:
                    print("Please enter a valid bet amount\n")
                    self.placeBet3()
                else:
                    pool = sa.Table("pool", self.metadata_obj, autoload_with=self.engine)
                    transactions = sa.Table("transactions", self.metadata_obj, autoload_with=self.engine)
                    bets = sa.Table("bets", self.metadata_obj, autoload_with=self.engine)
                    with self.engine.begin() as conn:

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
                    print("Bet successfully placed!\n")
                    self.bet()
            except ValueError:
                print("Please enter a valid bet amount\n")
                self.placeBet3()

    def viewUpcomingMatch(self):
        # brings up a list of upcoming matches first
        sql = """
        select matches.id, t1.teamname, t2.teamname, m.name, date
        from matches
            inner join teamId as t1 on matches.team1Id = t1.id
            inner join teamId as t2 on matches.team2Id = t2.id
            inner join map as m on matches.mapId = m.id
        where date >= curdate()
        order by date
        """
        upcoming = []
        try:
            with self.engine.begin() as conn:
                result = conn.execute(sa.text(sql))
                for matchid, team1, team2, map, date in result:
                    print(f"matchid: {matchid}, team1: {team1}, team2: {team2}, map: {map}, "
                          f"date: {date}")
                    upcoming.append(matchid)
        except Exception as error:
            print(f"Error returned: <<<{error}>>>")

        self.input = input("Enter a match id for more details\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.bet()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please select a valid match\n")
            self.viewUpcomingMatch()
        else:
            try:
                matchid = int(command[0])
                if matchid not in upcoming:
                    print("Please select a valid match\n")
                    self.viewUpcomingMatch()
                else:
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
                    except Exception as error:
                        print(f"Error returned: <<<{error}>>>")
            except ValueError:
                print("Please select a valid match\n")
                self.viewUpcomingMatch()
        self.viewUpcomingMatch()

    def history(self):
        self.input = input("Match History\nPersonal History\nBack\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.home()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif command[0].lower() == 'm' or command[0].lower() == 'match':
            sql = """
                select results.matchid, totalkills, headshotcount, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, date
                from results
                    inner join matches on results.matchid = matches.id
                    inner join teamId as t1 on matches.team1Id = t1.id
                    inner join teamId as t2 on matches.team2Id = t2.id
                    inner join map as m on matches.mapId = m.id
                where date < curdate()
                order by date desc
                limit 10
                """
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(sql))
                    for matchid, tk, hs, team1, t1s, team2, t2s, m, date in result:
                        print(f"Match ID: {matchid}, Total Kills: {tk}, Headshot Count: {hs}, "
                              f"Team1: {team1}, Team1 Score: {t1s}, Team2: {team2}, "
                              f"Team2 Score: {t2s} Map: {m}, Date: {date}")
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")
            print("\n")
            self.matchHistory()
        elif command[0].lower() == 'p' or command[0].lower() == 'personal':
            self.betHistory()
        else:
            print("Please select a valid option\n")
            self.history()

    def matchHistory(self):
        # brings up a list of matches played first
        self.input = input("Filter Options:\n"
                           "1: Map\n"
                           "2: Match ID\n"
                           "Back\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please enter a valid filter option\n")
            self.matchHistory()
        elif command[0] == "1":
            maps = sa.Table("map", self.metadata_obj, autoload_with=self.engine)
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.select(maps).order_by(maps.c.id))
                    for id, name in result:
                        print(f"{id}: {name}")
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")

            self.input2 = input("Enter the map ID\n\n")
            command2 = self.input2.split()
            if len(command2) > 1:
                print("Please enter a valid map ID\n")
                self.matchHistory()
            else:
                try:
                    mwant = int(command2[0])
                    sql = f"""
                          select results.matchid, totalkills, headshotcount, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, date
                            from results
                                inner join matches on results.matchid = matches.id
                                inner join teamId as t1 on matches.team1Id = t1.id
                                inner join teamId as t2 on matches.team2Id = t2.id
                                inner join map as m on matches.mapId = m.id
                            where date < curdate() and m.id = {mwant}
                            order by date desc
                            limit 50                  
                        """
                    try:
                        with self.engine.begin() as conn:
                            result = conn.execute(sa.text(sql))
                            for matchid, tk, hs, team1, t1s, team2, t2s, m, date in result:
                                print(f"Match ID: {matchid}, Total Kills: {tk}, Headshot Count: {hs}, "
                                      f"Team1: {team1}, Team1 Score: {t1s}, Team2: {team2}, "
                                      f"Team2 Score: {t2s} Map: {m}, Date: {date}")
                    except Exception as error:
                        print(f"Error returned: <<<{error}>>>")
                    print("\n")
                    self.matchHistory()
                except ValueError:
                    print("Please enter a valid map ID\n")
                    self.matchHistory()
        elif command[0] == "2":
            self.input2 = input("Enter the Match ID\n\n")
            command2 = self.input2.split()
            if len(command2) > 1:
                print("Please enter a valid Match ID\n")
                self.matchHistory()
            else:
                try:
                    mwant = int(command2[0])
                    sql2 = f"""
                                 select results.matchid, totalkills, headshotcount, t1.teamname as team1, team1score, t2.teamname as team2, team2score, m.name, date
                                   from results
                                       inner join matches on results.matchid = matches.id
                                       inner join teamId as t1 on matches.team1Id = t1.id
                                       inner join teamId as t2 on matches.team2Id = t2.id
                                       inner join map as m on matches.mapId = m.id
                                   where date < curdate() and results.matchid = {mwant}
                                   order by date desc
                                   limit 50                  
                               """
                    try:
                        with self.engine.begin() as conn:
                            result = conn.execute(sa.text(sql2))
                            for matchid, tk, hs, team1, t1s, team2, t2s, m, date in result:
                                print(f"Match ID: {matchid}, Total Kills: {tk}, Headshot Count: {hs}, "
                                      f"Team1: {team1}, Team1 Score: {t1s}, Team2: {team2}, "
                                      f"Team2 Score: {t2s} Map: {m}, Date: {date}")
                    except Exception as error:
                        print(f"Error returned: <<<{error}>>>")
                    print("\n")
                    self.matchHistory()
                except ValueError:
                    print("Please enter a valid Match ID\n")
                    self.matchHistory()
        else:
            print("Please select a valid match\n")
            self.matchHistory()

    def betHistory(self):
        # brings up a list of past bets, includes winnings and losings
        self.input = input("1: Bet History\n"
                           "2: Deposit History\n"
                           "3: Withdrawal History\n"
                           "4: Payout History\n"
                           "5: Any Transactions over X Amount\n"
                           "Back\nQuit\n\n")
        command = self.input.split()

        if command[0].lower() == 'b' or command[0].lower() == 'back':
            self.history()
        elif command[0].lower() == 'q' or command[0].lower() == 'quit':
            quit()
        elif len(command) > 1:
            print("Please enter a valid option\n")
            self.betHistory()
        elif command[0] == "1":
            s = f"""
                select transactionid, matchid, betType.type, guess, bets.amount 
                from bets 
                    inner join transactions on bets.transactionid = transactions.id
                    inner join betType on bets.bettypeid = betType.id
                where walletid = {self.walletid} and transactiontypeid = 3             
                """
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    for tid, mid, type, guess, amount in result:
                        print(f"Transaction ID: {tid},  Match ID: {mid},  Bet Type: {type}, "
                              f"Guess: {guess},  Amount: {amount}")
                    print("\n")
                    self.betHistory()
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")
        elif command[0] == "2":
            s = f"""
                  select * from transactions
                    where walletid = {self.walletid} and transactiontypeid = 2              
                """
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    for id, ttype, wid, amount in result:
                        print(f"ID: {id}, Amount: {amount}")
                    print("\n")
                    self.betHistory()
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")
        elif command[0] == "3":
            s = f"""
                  select * from transactions
                    where walletid = {self.walletid} and transactiontypeid = 1              
                       """
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    for id, ttype, wid, amount in result:
                        print(f"ID: {id}, Amount: {amount}")
                    print("\n")
                    self.betHistory()
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")
        elif command[0] == "4":
            s = f"""
                  select * from transactions
                    where walletid = {self.walletid} and transactiontypeid = 4              
                """
            try:
                with self.engine.begin() as conn:
                    result = conn.execute(sa.text(s))
                    for id, ttype, wid, amount in result:
                        print(f"ID: {id}, Amount: {amount}")
                    print("\n")
                    self.betHistory()
            except Exception as error:
                print(f"Error returned: <<<{error}>>>")
        elif command[0] == "5":
            self.input2 = input("Enter an amount\n\n")
            try:
                a = float(self.input2)
            except ValueError:
                print("Please enter a valid amount")
                self.betHistory()
            if a >= 0:
                s = f"""
                      select * from transactions
                        where walletid = {self.walletid} and amount >= {a}             
                    """
                try:
                    with self.engine.begin() as conn:
                        result = conn.execute(sa.text(s))
                        for id, ttype, wid, amount in result:
                            print(f"ID: {id}, Amount: {amount}")
                        print("\n")
                        self.betHistory()
                except Exception as error:
                    print(f"Error returned: <<<{error}>>>")
            else:
                print("Please enter a valid amount")
                self.betHistory()
        else:
            print("LOSER!\n")
            self.betHistory()


def main():
    Program()


if __name__ == '__main__':
    main()
