select
    team_id,
    full_name,
    season,
    games_played
from {{ ref('team_season_phase_summary') }}
where season_phase = 'regular_season'
  and games_played <> 82