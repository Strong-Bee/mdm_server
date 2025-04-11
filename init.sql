CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial TEXT,
    udid TEXT,
    ip TEXT,
    timestamp TEXT,
    al_bypass_code TEXT,
    push_token TEXT
);
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    udid TEXT,
    command_uuid TEXT,
    command_type TEXT,
    payload TEXT,
    status TEXT
);
