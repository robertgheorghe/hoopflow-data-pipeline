CREATE TABLE IF NOT EXISTS raw.games (
    game_id INT PRIMARY KEY,
    game_date DATE,
    season INT,
    status TEXT,
    period INT,
    postseason BOOLEAN,
    home_team_id INT,
    home_team_score INT,
    visitor_team_id INT,
    visitor_team_score INT
);