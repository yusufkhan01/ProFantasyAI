from team_builder import build_best_team
from utils import get_player_position, get_team_name
from fpl_api import fetch_player_data, fetch_player_summary

def main():
    # Fetch all players' data
    players, teams, positions = fetch_player_data()
    team_dict = {team['id']: team['name'] for team in teams}
    

    # Build the best team from the player data
    best_team, budget_left = build_best_team(players)

    print(f"Best Team Built! Remaining Budget: {budget_left/10.0} million")
    for player in best_team:
        # Make sure position is correctly mapped
        position_name = get_player_position(player['element_type'])
        team_name = team_dict.get(player['team'], "Unknown Team")
        print(f"{player['web_name']:<15} ({position_name:<3}) {player['now_cost']/10.0:>5.1f} million   ({team_name})")
            

# Call the main function to run the app
if __name__ == "__main__":
    main()
