import database_creation
import populate_match_teams_results
import populate_tables_map_teamId_player


def main():
    database_creation.main()
    print('tables created\n')
    populate_tables_map_teamId_player.main()
    print('map, teamId, and player populated\n')
    populate_match_teams_results.main()
    print('match, teams, and results populated\n')


if __name__ == '__main__':
    main()
