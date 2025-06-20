from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
from .db_player_xpass import get_all_player_xpass
from .db_player_goals_added import get_all_players_goals_added_by_season
from .db_goalkeeper_goals_added import get_all_goalkeeper_goals_added_by_season
from .db_goalkeeper_xgoals import get_all_goalkeepers_xgoals_by_season
from .db_game_shots import get_shots_by_type
from .data_util import get_range, normalize, get_range
import sqlite3

def update_goalkeeper_strength(season):
    players_goals_added = get_all_goalkeeper_goals_added_by_season(season)
    players_xgoals = get_all_goalkeepers_xgoals_by_season(season)

    # Convert to dicts for lookup
    ga_dict = {p['player_id']: dict(p) for p in players_goals_added}
    xg_dict = {p['player_id']: dict(p) for p in players_xgoals}

    goalkeepers = []
    for player_id, p_xg in xg_dict.items():
        if player_id not in ga_dict:
            continue
        p_ga = ga_dict[player_id]

        gk = {
            'player_id': player_id,
            'season': p_xg['season'],
            'minutes_played': p_xg['minutes_played'],
            'save_perc': p_xg['save_perc'],
            'goals_divided_by_xgoals_gk': p_xg['goals_divided_by_xgoals_gk'],
            'shotstopping_ga': p_ga['shotstopping_goals_added_raw'],
            'claiming_ga': p_ga['claiming_goals_added_raw'],
            'passing_ga': p_ga['passing_goals_added_raw'],
            'handling_ga': p_ga['handling_goals_added_raw'],
            'sweeping_ga': p_ga['sweeping_goals_added_raw']
        }
        goalkeepers.append(gk)

    # Separate qualified and unqualified
    qualified = [gk for gk in goalkeepers if gk['minutes_played'] >= MINIMUM_MINUTES]
    unqualified = [gk for gk in goalkeepers if gk['minutes_played'] < MINIMUM_MINUTES]

    if not qualified:
        print("No qualified goalkeepers found.")
        return

    # Get normalization ranges
    min_sv, max_sv = get_range(qualified, 'save_perc')
    min_eff, max_eff = get_range(qualified, 'goals_divided_by_xgoals_gk')
    min_ss, max_ss = get_range(qualified, 'shotstopping_ga')
    min_cl, max_cl = get_range(qualified, 'claiming_ga')
    min_pa, max_pa = get_range(qualified, 'passing_ga')
    min_ha, max_ha = get_range(qualified, 'handling_ga')
    min_sw, max_sw = get_range(qualified, 'sweeping_ga')

    # DB connection
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for gk in qualified:
        sv = normalize(gk['save_perc'], min_sv, max_sv)
        eff = normalize(gk['goals_divided_by_xgoals_gk'], min_eff, max_eff)
        ss = normalize(gk['shotstopping_ga'], min_ss, max_ss)
        cl = normalize(gk['claiming_ga'], min_cl, max_cl)
        pa = normalize(gk['passing_ga'], min_pa, max_pa)
        ha = normalize(gk['handling_ga'], min_ha, max_ha)
        sw = normalize(gk['sweeping_ga'], min_sw, max_sw)

        strength = (
            0.20 * sv +
            0.20 * (1 - eff) +  # Lower G/xG is better
            0.20 * ss +
            0.10 * cl +
            0.10 * pa +
            0.10 * ha +
            0.10 * sw
        )

        score = round(strength * 100, 1)

        cursor.execute(
            '''
            UPDATE goalkeeper_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (score, gk['player_id'], gk['season'])
        )

    # Set unqualified to 0
    for gk in unqualified:
        cursor.execute(
            '''
            UPDATE goalkeeper_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (gk['player_id'], gk['season'])
        )

    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} goalkeepers, reset {len(unqualified)} others.")

def update_midfielder_strength(season):
    players_xgoals = get_top_player_xgoals_stat(season)
    players_xpass = get_all_player_xpass(season)
    player_goals_added = get_all_players_goals_added_by_season(season)
    penalty_shots = get_shots_by_type('penalty', season)

    # Build dictionaries for joins
    xgoals_dict = {p['player_id']: dict(p) for p in players_xgoals}
    xpass_dict = {p['player_id']: dict(p) for p in players_xpass}
    goals_added_dict = {p['player_id']: dict(p) for p in player_goals_added}

    # Sum penalty xG per player
    penalty_xg_by_player = {}
    for shot in penalty_shots:
        pid = shot['shooter_player_id']
        penalty_xg_by_player[pid] = penalty_xg_by_player.get(pid, 0) + shot['shot_xg']

    # Join and filter midfielders
    midfielders = []
    for player_id, p_xpass in xpass_dict.items():
        if p_xpass['general_position'] not in ('DM', 'CM', 'AM'):
            continue
        if player_id not in xgoals_dict or player_id not in goals_added_dict:
            continue

        xg_data = xgoals_dict[player_id]
        ga_data = goals_added_dict[player_id]

        # Deduct penalty xG
        original_pts = xg_data['points_added']
        pk_xg = penalty_xg_by_player.get(player_id, 0)
        adjusted_pts = max(0, original_pts - pk_xg)

        combined = {
            'player_id': player_id,
            'season': p_xpass['season'],
            'xassists': xg_data['xassists'],
            'points_added': adjusted_pts,
            'passes_completed_over_expected': p_xpass['passes_completed_over_expected'],
            'pass_completion_percentage': p_xpass['pass_completion_percentage'],
            'share_team_touches': p_xpass['share_team_touches'],
            'minutes_played': p_xpass['minutes_played'],
            'passing_ga': ga_data['passing_goals_added_raw'],
            'receiving_ga': ga_data['receiving_goals_added_raw'],
            'interrupting_ga': ga_data['interrupting_goals_added_raw'],
            'player_name': xg_data.get('player_name', 'Unknown',),
        }
        midfielders.append(combined)

    # Filter by minutes
    qualified = [p for p in midfielders if p['minutes_played'] >= MINIMUM_MINUTES]
    unqualified = [p for p in midfielders if p['minutes_played'] < MINIMUM_MINUTES]

    if not qualified:
        print("No qualified midfielders found.")
        return

    # Normalize features
    min_exp, max_exp = get_range(qualified, 'passes_completed_over_expected')
    min_touch, max_touch = get_range(qualified, 'share_team_touches')
    min_xa, max_xa = get_range(qualified, 'xassists')
    min_pts, max_pts = get_range(qualified, 'points_added')
    min_pga, max_pga = get_range(qualified, 'passing_ga')
    min_rga, max_rga = get_range(qualified, 'receiving_ga')
    min_iga, max_iga = get_range(qualified, 'interrupting_ga')

    # DB update
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for p in qualified:
        exp = normalize(p['passes_completed_over_expected'], min_exp, max_exp)
        touch = normalize(p['share_team_touches'], min_touch, max_touch)
        xa = normalize(p['xassists'], min_xa, max_xa)
        pts = normalize(p['points_added'], min_pts, max_pts)
        pga = normalize(p['passing_ga'], min_pga, max_pga)
        rga = normalize(p['receiving_ga'], min_rga, max_rga)
        iga = normalize(p['interrupting_ga'], min_iga, max_iga)

        strength = (
            0.20 * exp +          # Distribution skill
            0.15 * touch +        # Involvement
            0.15 * xa +           # Creative quality
            0.15 * pts +          # Total attacking contribution
            0.15 * pga +          # Passing impact
            0.10 * rga +          # Receiving quality
            0.10 * iga            # Disruption
        )

        score = round(strength * 100, 1)

        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (score, p['player_id'], season)
        )

    # Unqualified players get a score of 0
    for p in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (p['player_id'], season)
        )

    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} midfielders, reset {len(unqualified)} others.")

def update_attacker_strength(season):
    players_data = get_top_player_xgoals_stat(season)
    goals_added_data = get_all_players_goals_added_by_season(season)
    penalty_shots = get_shots_by_type('penalty', season)

    # Convert and filter for attackers
    xgoals_dict = {p['player_id']: dict(p) for p in players_data}
    goals_added_dict = {p['player_id']: dict(p) for p in goals_added_data}

    # Tally PK goals and xG by player
    penalty_xg_by_player = {}
    penalty_goals_by_player = {}
    for shot in penalty_shots:
        pid = shot['shooter_player_id']
        penalty_xg_by_player[pid] = penalty_xg_by_player.get(pid, 0) + shot['shot_xg']
        if shot['goal']:
            penalty_goals_by_player[pid] = penalty_goals_by_player.get(pid, 0) + 1

    attackers = []
    for player_id, player in xgoals_dict.items():
        if player['general_position'] not in ('W', 'ST'):
            continue
        if player_id not in goals_added_dict:
            continue

        ga = goals_added_dict[player_id]

        # Remove PK goals and xG
        adjusted_xg = max(0, player['xgoals'] - penalty_xg_by_player.get(player_id, 0))
        adjusted_goals = max(0, player['goals'] - penalty_goals_by_player.get(player_id, 0))

        combined = {
            'player_id': player_id,
            'season': player['season'],
            'xgoals': adjusted_xg,
            'goals': adjusted_goals,
            'xassists': player['xassists'],
            'shots_on_target': player['shots_on_target'],
            'points_added': player['points_added'],
            'shooting_ga': ga['shooting_goals_added_raw'],
            'receiving_ga': ga['receiving_goals_added_raw'],
            'dribbling_ga': ga['dribbling_goals_added_raw'],
            'minutes_played': player['minutes_played']
        }
        attackers.append(combined)

    qualified = [p for p in attackers if p['minutes_played'] >= MINIMUM_MINUTES]
    unqualified = [p for p in attackers if p['minutes_played'] < MINIMUM_MINUTES]

    if not qualified:
        print("No qualified attackers to score.")
        return

    # Normalize each metric
    min_xg, max_xg = get_range(qualified, 'xgoals')
    min_goals, max_goals = get_range(qualified, 'goals')
    min_xa, max_xa = get_range(qualified, 'xassists')
    min_sot, max_sot = get_range(qualified, 'shots_on_target')
    min_pts, max_pts = get_range(qualified, 'points_added')
    min_shoot, max_shoot = get_range(qualified, 'shooting_ga')
    min_recv, max_recv = get_range(qualified, 'receiving_ga')
    min_drib, max_drib = get_range(qualified, 'dribbling_ga')

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for p in qualified:
        xg = normalize(p['xgoals'], min_xg, max_xg)
        goals = normalize(p['goals'], min_goals, max_goals)
        xa = normalize(p['xassists'], min_xa, max_xa)
        sot = normalize(p['shots_on_target'], min_sot, max_sot)
        pts = normalize(p['points_added'], min_pts, max_pts)
        shoot = normalize(p['shooting_ga'], min_shoot, max_shoot)
        recv = normalize(p['receiving_ga'], min_recv, max_recv)
        drib = normalize(p['dribbling_ga'], min_drib, max_drib)

        strength_score = round((
            0.25 * xg +
            0.20 * goals +
            0.15 * xa +
            0.10 * sot +
            0.10 * pts +
            0.10 * shoot +
            0.05 * recv +
            0.05 * drib
        ) * 100, 1)

        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (strength_score, p['player_id'], p['season'])
        )

    for p in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (p['player_id'], p['season'])
        )

    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} attackers, reset {len(unqualified)} others.")
