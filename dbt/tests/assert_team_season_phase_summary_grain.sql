select
    team_id,
    season,
    season_phase,
    count(*) as row_count
from {{ ref('team_season_phase_summary') }}
group by
    team_id,
    season,
    season_phase
having count(*) > 1