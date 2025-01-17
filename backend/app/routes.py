from flask import jsonify, request
from fpl_api import (
    fetch_all_players, fetch_fixtures, fetch_player_summary,
    fetch_gameweek_stats, fetch_manager_info, fetch_manager_history,
    fetch_manager_transfers, fetch_manager_picks, fetch_league_standings
)

@app.route('/api/players', methods=['GET'])
def get_all_players():
    data = fetch_all_players()
    return jsonify(data)

@app.route('/api/fixtures', methods=['GET'])
def get_fixtures():
    data = fetch_fixtures()
    return jsonify(data)

@app.route('/api/player/<int:eid>', methods=['GET'])
def get_player_summary(eid):
    data = fetch_player_summary(eid)
    return jsonify(data)

@app.route('/api/gameweek/<int:gw>', methods=['GET'])
def get_gameweek_stats(gw):
    data = fetch_gameweek_stats(gw)
    return jsonify(data)

@app.route('/api/manager/<int:tid>', methods=['GET'])
def get_manager_info(tid):
    data = fetch_manager_info(tid)
    return jsonify(data)

@app.route('/api/manager/<int:tid>/history', methods=['GET'])
def get_manager_history(tid):
    data = fetch_manager_history(tid)
    return jsonify(data)

@app.route('/api/manager/<int:tid>/transfers', methods=['GET'])
def get_manager_transfers(tid):
    data = fetch_manager_transfers(tid)
    return jsonify(data)

@app.route('/api/manager/<int:tid>/picks/<int:gw>', methods=['GET'])
def get_manager_picks(tid, gw):
    data = fetch_manager_picks(tid, gw)
    return jsonify(data)

@app.route('/api/league/<int:tid>/standings', methods=['GET'])
def get_league_standings(tid):
    page = request.args.get('page', 1, type=int)
    data = fetch_league_standings(tid, page)
    return jsonify(data)
