-- create table for Sheet model
DROP TABLE IF EXISTS webinar;
CREATE TABLE IF NOT EXISTS webinar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_at DATE default (datetime('now')),
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    date_str VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    UNIQUE (url)
);

-- create table users for Participant model
DROP TABLE IF EXISTS account;
CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY,
    timestamp VARCHAR(255),
    family_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    father_name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    webinar_id INTEGER NOT NULL,
    FOREIGN KEY (webinar_id)
    REFERENCES webinar (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
    UNIQUE (email, webinar_id),
    UNIQUE (phone, webinar_id)
);
