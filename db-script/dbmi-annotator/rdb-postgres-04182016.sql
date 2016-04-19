-- Table: USER
-- DROP TABLE IF EXISTS USER;
CREATE TABLE "user"(
    id SERIAL NOT NULL PRIMARY KEY,
    uid TEXT NOT NULL,
    username TEXT NOT NULL,
    admin BOOLEAN,
    manager BOOLEAN,
    email TEXT NOT NULL,
    status INTEGER,
    last_login_date timestamp,
    registered_date timestamp,
    activation_id INTEGER,
    password TEXT NOT NULL
);

-- Table: USER_PROFILE
-- DROP TABLE IF EXISTS USER_PROFILE;
CREATE TABLE "user_profile"(
    id SERIAL NOT NULL PRIMARY KEY,
    uid TEXT NOT NULL,
    set_id TEXT NOT NULL,
    status BOOLEAN,
    created timestamp
);

-- Table: PLUGIN_SET
-- DROP TABLE IF EXISTS PLUGIN_SET;
CREATE TABLE "plugin_set"(
    id SERIAL NOT NULL PRIMARY KEY,
    set_id TEXT NOT NULL,
    plugin_id INTEGER NOT NULL,
    status BOOLEAN,
    created timestamp
);


-- Table: PLUGIN
-- DROP TABLE IF EXISTS PLUGIN;
CREATE TABLE "plugin"(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status BOOLEAN,
    created timestamp
);


-- Table: USER_GROUP
-- DROP TABLE IF EXISTS USER_GROUP;
CREATE TABLE "user_group"(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id TEXT NOT NULL,
    group_id INTEGER NOT NULL
);


-- Table: GROUP
-- DROP TABLE IF EXISTS GROUP;
CREATE TABLE "group"(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    created timestamp,
    updated timestamp,
    creator_id TEXT NOT NULL
);

-- Table: ACTIVATION
-- DROP TABLE IF EXISTS ACTIVATION;
CREATE TABLE "activation"(
    id SERIAL NOT NULL PRIMARY KEY,
    code TEXT NOT NULL,
    created timestamp,
    valid_until timestamp
);
