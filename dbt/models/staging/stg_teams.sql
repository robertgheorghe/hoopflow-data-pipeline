select
    team_id,
    abbreviation,
    city,
    conference,
    division,
    full_name,
    name
from {{ source('raw', 'teams') }}
where conference in ('East', 'West')