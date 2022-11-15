import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
import pandas as pd
import numpy as np


def main():
    df_results = pd.read_csv('data/results.csv')
    df_results = df_results[['date', 'team_1', 'team_2', '_map', 'result_1', 'result_2', 'event_id', 'match_id']]
    df_players = pd.read_csv('data/players.csv')
    df_players = df_players[['date', 'player_name', 'team', 'country', 'player_id', 'event_id', 'match_id', 'map_1',
                             'm1_kills', 'm1_hs']]

    df_join = df_players.merge(df_results,
                               left_on=['event_id', 'match_id', 'date', 'team'],
                               right_on=['event_id', 'match_id', 'date', 'team_1'])

    df_maps = df_join['_map'].unique()
    df_maps = pd.DataFrame(np.squeeze(df_maps), columns=['name'])

    df_players = df_join['player_name'].str.upper().unique()
    df_players = pd.DataFrame(np.squeeze(df_players), columns=['name'])

    df_teams = df_join['team'].str.upper().unique()
    df_teams = pd.DataFrame(np.squeeze(df_teams), columns=['name'])

    df_maps.to_csv('data/mapsData.csv')
    df_players.to_csv('data/playersData.csv')
    df_teams.to_csv('data/teamsIdData.csv')

    # # Load env file
    # load_dotenv()
    #
    # # Connection Parameters (you will sub in with your own databases values)
    # escapedPassword = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD"))
    # sqldialect = os.environ.get("DB_DIALECT")
    # username = os.environ.get("DB_USER")
    # database = os.environ.get("DB_NAME")
    # host = os.environ.get("DB_HOST")
    #
    # # Build the connection string based on database specific parameters
    # connectionString = f"{sqldialect}://{username}:{escapedPassword}@{host}/{database}"
    #
    # # Create a new DB engine based on our connection string
    # engine = sa.create_engine(connectionString, echo="debug")
    #
    # metadata_obj = sa.MetaData()
    # maps = sa.Table("map", metadata_obj, autoload_with=engine)
    # teams = sa.Table("teamId", metadata_obj, autoload_with=engine)
    # players = sa.Table("player", metadata_obj, autoload_with=engine)
    #
    # with engine.begin() as conn:
    #     try:
    #
    #         for m in df_maps:
    #             conn.execute(sa.insert(maps), [{'name': f'{m}'}])
    #
    #         for t in df_teams:
    #             conn.execute(sa.insert(teams), [{'teamName': f'{t}'}])
    #
    #         for p in df_players:
    #             conn.execute(sa.insert(players), [{'playerName': f'{p}'}])
    #
    #     except Exception as error:
    #         print(f"Error returned: <<<{error}>>>")


if __name__ == '__main__':
    main()

