from engine import build_best_team, get_player_position
from fpl_api import fetch_player_data

def main():
    # Fetch all players' data
    players = fetch_player_data()
    
    # Build the best team
    best_team, budget_left = build_best_team(players)

    # If a valid team is built, display the results
    if best_team is None:
        print("Failed to build a valid team.")
    else:
        print(f"Best Team Built! Remaining Budget: {budget_left:.2f} million")
        for player in best_team:
            print(f"{player['name']} ({get_player_position(player['position'])}) - {player['price']} million")
        
if __name__ == "__main__":
    main()