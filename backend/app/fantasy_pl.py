from team_builder import build_best_team
from utils import get_player_position, get_team_name
from fpl_api import fetch_player_data, fetch_player_summary

from flask import Flask

app = Flask(__name__)

@app.route('/home')
def main():
    # Fetch all players' data
    players, teams, positions = fetch_player_data()
    team_dict = {team['id']: team['name'] for team in teams}
    

    # Build the best team from the player data
    best_team, budget_left = build_best_team(players)

    best_team_list = [[0] * 4 for _ in range(15)]
    i=0

    

    for player in best_team:
        # Make sure position is correctly mapped
        position_name = get_player_position(player['element_type'])
        team_name = team_dict.get(player['team'], "Unknown Team")

        best_team_list[i][0]=player['web_name']
        best_team_list[i][1]=position_name
        best_team_list[i][2]=player['now_cost']/10.0
        best_team_list[i][3]=team_name
        i+=1

    return {
    "best_team": best_team_list
}

            
# Call the main function to run the app
if __name__ == '__main__':
    app.run(debug=True)