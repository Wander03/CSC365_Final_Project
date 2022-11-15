import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
import pandas as pd


def main():
    df_results = pd.read_csv('data/results.csv')
    df_results = df_results[['date', 'team_1', 'team_2', '_map', 'result_1', 'result_2', 'event_id', 'match_id']]
    df_players = pd.read_csv('data/players.csv')
    df_players = df_players[['date', 'player_name', 'team', 'country', 'player_id', 'event_id', 'match_id', 'map_1',
                             'm1_kills', 'm1_hs']]

    df_results['team_1'] = df_results['team_1'].str.upper()
    df_results['team_2'] = df_results['team_2'].str.upper()
    df_results['i'] = range(len(df_results))

    df_players['player_name'] = df_players['player_name'].str.upper()
    df_players['team'] = df_players['team'].str.upper()

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

    df_map = pd.read_sql_table('map', engine)
    df_map.rename(columns={'id': 'mapId'}, inplace=True)
    df_team = pd.read_sql_table('teamId', engine)
    df_team.rename(columns={'id': 'teamId'}, inplace=True)
    df_player = pd.read_sql_table('player', engine)
    df_player.rename(columns={'id': 'playerId'}, inplace=True)

    # Prep teams
    df_team_tbl = df_players.merge(df_player, left_on='player_name', right_on='playerName')
    df_team_tbl = df_team_tbl.merge(df_team, left_on='team', right_on='teamName')
    df_team_tbl = df_team_tbl[['playerId', 'teamId']]
    df_team_tbl.drop_duplicates(subset=['playerId', 'teamId'], inplace=True)

    # Prep matches and results
    df_results = df_results.merge(df_map, left_on='_map', right_on='name')
    df_results = df_results.merge(df_team, left_on='team_1', right_on='teamName')
    df_results = df_results.merge(df_team, left_on='team_2', right_on='teamName')
    df_matches = df_results[['i', 'teamId_x', 'teamId_y', 'mapId', 'date']].copy()

    df_join = df_results.merge(df_players,
                               right_on=['event_id', 'match_id', 'date', 'team'],
                               left_on=['event_id', 'match_id', 'date', 'team_1'],
                               how='left')
    df_calc = df_join[['i', 'm1_kills', 'm1_hs']].groupby(['i']).sum()
    df_calc = df_matches.merge(df_calc, left_on=['i'], right_on=['i'])
    df_calc = df_calc.merge(df_results[['i', 'result_1', 'result_2']].copy(), left_on=['i'], right_on=['i'])
    df_calc = df_calc[df_calc['m1_kills'] != 0]
    df_calc.sort_values('date', inplace=True)
    df_calc['i'] = range(1, len(df_calc) + 1)

    df_matches = df_calc[['i', 'teamId_x', 'teamId_y', 'mapId', 'date']].copy()
    df_results_data = df_calc[['i', 'm1_kills', 'm1_hs', 'result_1', 'result_2']].copy()

    df_team_tbl.to_csv('data/teamsData.csv')
    df_matches.to_csv('data/matchesData.csv')
    df_results_data.to_csv('data/resultsData.csv')


if __name__ == '__main__':
    main()
