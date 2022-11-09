import pandas as pd


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
    df_players = df_join['player_name'].unique()
    df_teams = df_join['team'].unique()


if __name__ == '__main__':
    main()