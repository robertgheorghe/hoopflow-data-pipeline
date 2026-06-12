with eligible_games as (

    select
        game_id,
        game_date,
        season,
        case
            when postseason then 'postseason'
            when not postseason and game_date <= date '2024-04-14' then 'regular_season'
        end as season_phase,
        home_team_id,
        home_team_score,
        visitor_team_id,
        visitor_team_score
    from {{ ref('stg_games') }}
    where not (
        game_date = date '2023-12-09'
        and (
            (home_team_id = 14 and visitor_team_id = 12)
            or (home_team_id = 12 and visitor_team_id = 14)
        )
    )

),

classified_games as (

    select *
    from eligible_games
    where season_phase is not null

),

team_games as (

    select
        home_team_id as team_id,
        season,
        season_phase,
        home_team_score as points_scored,
        visitor_team_score as points_allowed,
        case when home_team_score > visitor_team_score then 1 else 0 end as win
    from classified_games

    union all

    select
        visitor_team_id as team_id,
        season,
        season_phase,
        visitor_team_score as points_scored,
        home_team_score as points_allowed,
        case when visitor_team_score > home_team_score then 1 else 0 end as win
    from classified_games

),

team_phase_totals as (

    select
        team_id,
        season,
        season_phase,
        count(*) as games_played,
        sum(win) as wins,
        count(*) - sum(win) as losses,
        sum(points_scored) as points_scored,
        sum(points_allowed) as points_allowed,
        sum(points_scored) - sum(points_allowed) as point_differential,
        round(avg(points_scored)::numeric, 2) as average_points_scored,
        round(avg(points_allowed)::numeric, 2) as average_points_allowed,
        round(sum(win)::numeric / count(*), 3) as win_percentage
    from team_games
    group by
        team_id,
        season,
        season_phase

)

select
    totals.team_id,
    teams.full_name,
    teams.abbreviation,
    teams.conference,
    teams.division,
    totals.season,
    totals.season_phase,
    totals.games_played,
    totals.wins,
    totals.losses,
    totals.points_scored,
    totals.points_allowed,
    totals.point_differential,
    totals.average_points_scored,
    totals.average_points_allowed,
    totals.win_percentage
from team_phase_totals as totals
inner join {{ ref('stg_teams') }} as teams
    on totals.team_id = teams.team_id
