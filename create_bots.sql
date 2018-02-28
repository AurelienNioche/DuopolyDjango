INSERT INTO game_user (
  "username", "password", "deserter", "connected", "registered", "registration_time", "time_last_request"
) VALUES (
    'bot0', '0000', FALSE, FALSE, FALSE,
    current_timestamp AT TIME ZONE 'Europe/Paris', current_timestamp AT TIME ZONE 'Europe/Paris'
);

INSERT INTO game_user (
  "username", "password", "deserter", "connected", "registered", "registration_time", "time_last_request"
) VALUES (
    'bot1', '0001', FALSE, FALSE, FALSE,
    current_timestamp AT TIME ZONE 'Europe/Paris', current_timestamp AT TIME ZONE 'Europe/Paris'
);
