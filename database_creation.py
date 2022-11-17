import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, DECIMAL, Boolean, ForeignKey


def main():
    # Load env file
    load_dotenv()

    # Connection Parameters (you will sub in with your own databases values)
    escapedPassword = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD"))
    sqldialect = os.environ.get("DB_DIALECT")
    username = os.environ.get("DB_USER")
    database = os.environ.get("DB_NAME")
    host = os.environ.get("DB_HOST")

    # Build the connection string based on database specific parameters
    connectionString = f"{sqldialect}://{username}:{escapedPassword}@{host}/{database}"

    # Create a new DB engine based on our connection string
    engine = sa.create_engine(connectionString)

    with engine.begin() as conn:
        meta = sa.MetaData()
        try:
            conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.execute(sa.text("DROP TABLE IF EXISTS betType, transactionType, map, user, transactions, "
                                 "wallet, player, teamId, teams, pool, matches, bets, results, teamsSnapshot"))
            conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))

            Table(
                'betType', meta,
                Column('id', Integer, primary_key=True),
                Column('type', String(50))
            )

            Table(
                'transactionType', meta,
                Column('id', Integer, primary_key=True),
                Column('type', String(50)),
                sa.UniqueConstraint('type')
            )

            Table(
                'map', meta,
                Column('id', Integer, primary_key=True),
                Column('name', String(50)),
                sa.UniqueConstraint('name')
            )

            Table(
                'user', meta,
                Column('id', Integer, primary_key=True),
                Column('firstName', String(50)),
                Column('lastName', String(50)),
                Column('email', String(50)),
                Column('passwordHash', String(50)),
                Column('salt', String(50)),
                sa.UniqueConstraint('email')
            )

            Table(
                'transactions', meta,
                Column('id', Integer, primary_key=True),
                Column('transactionTypeId', Integer, ForeignKey('transactionType.id')),
                Column('walletId', Integer, ForeignKey('wallet.id')),
                Column('amount', DECIMAL(50, 2))
            )

            Table(
                'wallet', meta,
                Column('id', Integer, primary_key=True),
                Column('userId', Integer, ForeignKey('user.id')),
                Column('name', String(50)),
                Column('amountStored', DECIMAL(50, 2)),
                sa.UniqueConstraint('name')
            )

            Table(
                'player', meta,
                Column('id', Integer, primary_key=True),
                Column('playerName', String(50)),
                sa.UniqueConstraint('playerName')
            )

            Table(
                'teamId', meta,
                Column('id', Integer, primary_key=True),
                Column('teamName', String(50)),
                sa.UniqueConstraint('teamName')
            )

            Table(
                'teams', meta,
                Column('id', Integer, primary_key=True),
                Column('playerId', Integer, ForeignKey('player.id')),
                Column('teamId', Integer, ForeignKey('teamId.id'))
            )

            Table(
                'pool', meta,
                Column('id', Integer, primary_key=True),
                Column('matchId', Integer, ForeignKey('matches.id')),
                Column('betTypeId', Integer, ForeignKey('betType.id')),
                Column('amount', DECIMAL(50, 2))
            )

            Table(
                'matches', meta,
                Column('id', Integer, primary_key=True),
                Column('team1Id', Integer, ForeignKey('teamId.id')),
                Column('team2Id', Integer, ForeignKey('teamId.id')),
                Column('mapId', Integer, ForeignKey('map.id')),
                Column('date', Date)
            )

            Table(
                'bets', meta,
                Column('id', Integer, primary_key=True),
                Column('transactionId', Integer, ForeignKey('transactions.id')),
                Column('matchId', Integer, ForeignKey('matches.id')),
                Column('betTypeId', Integer, ForeignKey('betType.id')),
                Column('guess', Integer),
                Column('amount', DECIMAL(50, 2))
            )

            Table(
                'results', meta,
                Column('id', Integer, primary_key=True),
                Column('matchId', Integer, ForeignKey('matches.id')),
                Column('totalKills', Integer),
                Column('headshotCount', Integer),
                Column('team1Score', Integer),
                Column('team2Score', Integer)
            )

            Table(
                'teamsSnapshot', meta,
                Column('id', Integer, primary_key=True),
                Column('playerId', Integer, ForeignKey('player.id')),
                Column('teamId', Integer, ForeignKey('teamId.id'))
            )

            meta.create_all(engine)

            result = conn.execute(sa.text("show tables"))
            for i in result:
                print(i)

        except Exception as error:
            print(f"Error returned: <<<{error}>>>")


if __name__ == '__main__':
    main()

# while loop for n days
#     for each agent, give match info, place bet
#
#     each agent is an object with a different "goal", eg greedy
