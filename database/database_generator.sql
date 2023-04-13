USE emotibit;

DROP TABLE IF EXISTS ACCOUNTS;
DROP TABLE IF EXISTS HR_DATA;
DROP TABLE IF EXISTS TH_DATA;
DROP TABLE IF EXISTS WORKOUTS;

CREATE TABLE WORKOUTS(
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    extension VARCHAR(4) NOT NULL DEFAULT 'csv',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
);

CREATE TABLE HR_DATA (
   id INT NOT NULL AUTO_INCREMENT,
   bpm INT,
   workout_id INT UNSIGNED NOT NULL,
   PRIMARY KEY (id),
   FOREIGN KEY (workout_id) REFERENCES WORKOUTS(id) ON DELETE CASCADE
);

CREATE TABLE TH_DATA (
   id INT NOT NULL AUTO_INCREMENT,
   workout_id INT UNSIGNED NOT NULL,
   temperature FLOAT,
   PRIMARY KEY (id),
   FOREIGN KEY (workout_id) REFERENCES WORKOUTS(id) ON DELETE CASCADE
);

CREATE TABLE ACCOUNTS(
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(30),
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY (email)
);

INSERT INTO ACCOUNTS(
	username, email, password_hash, password_salt
)VALUES(
	'Lucas Camino',
    'lacami01@louisville.edu',
    '2e2b24f8ee40bb847fe85bb23336a39ef5948e6b49d897419ced68766b16967a',
    '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
),(
	'Tristan Dunlavy',
    'tristan.dunlavy@louisville.edu',
    '2e2b24f8ee40bb847fe85bb23336a39ef5948e6b49d897419ced68766b16967a',
    '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
);

-- INSERT INTO WORKOUTS()VALUES(),(),(),(),(),(),();