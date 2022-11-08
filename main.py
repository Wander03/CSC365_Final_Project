import os
from dotenv import load_dotenv
import sqlalchemy
import urllib.parse


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
    engine = sqlalchemy.create_engine(connectionString)

    with engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.text("show tables")
        )
    for i in result:
        print(i)


if __name__ == '__main__':
    main()

# while loop for n days
#     for each agent, give match info, place bet
#
#     each agent is an object with a different "goal", eg greedy