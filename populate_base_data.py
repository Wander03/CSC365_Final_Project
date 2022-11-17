import database_creation
import populate_fake_data
import populate_match_teams_results
import populate_tables_map_teamId_player


def main():
    database_creation.main()
    print('tables created\n')
    populate_tables_map_teamId_player.main()
    print('map, teamId, and player created\n')

    ans = 'n'
    while ans != 'y':
        ans = input('are map, teamId, and player data imported?\ny/n\n')

    populate_match_teams_results.main()
    print('\nmatch, teams, and results created\n')

    ans = 'n'
    while ans != 'y':
        ans = input('are teams, matches and results imported?\ny/n\n')

    populate_fake_data.main()
    print('fake data created\n')


if __name__ == '__main__':
    inpt = 'n'
    while inpt != 'y':
        inpt = input('re-build database?\ny/n\n')

    main()
