select
    game_id,
    game_date,
    season,
    status,
    period,
    postseason,
    home_team_id,
    home_team_score,
    visitor_team_id,
    visitor_team_score
from {{ source('raw', 'games') }}
where status = 'Final'