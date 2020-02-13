-- TABLE USER
CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY NOT NULL);


-- TABLE PLACE
CREATE TABLE IF NOT EXISTS place (id INTEGER PRIMARY KEY NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    image BLOB,
                    latitude FLOAT  NOT NULL,
                    longitude FLOAT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                    );
