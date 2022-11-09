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

    # Prep matches
    df_results = df_results.merge(df_map, left_on='_map', right_on='name')
    df_results = df_results.merge(df_team, left_on='team_1', right_on='teamName')
    df_results = df_results.merge(df_team, left_on='team_2', right_on='teamName')
    df_matches = df_results[['teamId_x', 'teamId_y', 'mapId', 'date']]

    # Prep results
    # calculate total kills and hs then join onto results and dont forget the match id
    # find way to get consistent index for matches and results tbl the join onto both
    df_join = df_players.merge(df_results,
                               left_on=['event_id', 'match_id', 'date', 'team'],
                               right_on=['event_id', 'match_id', 'date', 'team_1'])
    df_calc = df_join[['event_id', 'match_id', 'm1_kills', 'm1_hs']].groupby(['event_id', 'match_id']).sum()
    df_calc = df_results.merge(df_calc, on=['event_id', 'match_id'])

    print(df_calc)

    #
    # df_teams = df_join[['teamId_x', 'playerId']]
    # df_teams = df_teams.unique()
    # df_matches = df_join[['teamId_x', 'teamId_y', 'mapId', 'date']]

    # metadata_obj = sa.MetaData()
    # teams = sa.Table("teams", metadata_obj, autoload_with=engine)
    #
    # with engine.begin() as conn:
    #     try:
    #
    #         for i in df_team_tbl:
    #             conn.execute(sa.insert(teams),
    #                          [{'playerId': f"{df_team_tbl['playerId'][i]}", 'teamId': f"{df_team_tbl['teamId'][i]}"}])
    #
    #     except Exception as error:
    #         print(f"Error returned: <<<{error}>>>")


if __name__ == '__main__':
    main()
