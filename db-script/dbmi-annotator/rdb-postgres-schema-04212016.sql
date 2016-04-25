-- Table: USER
DROP TABLE IF EXISTS "user";
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
DROP TABLE IF EXISTS "user_profile";
CREATE TABLE "user_profile"(
    id SERIAL NOT NULL PRIMARY KEY,
    uid TEXT NOT NULL,
    set_id INTEGER NOT NULL,
    status BOOLEAN,
    created timestamp
);

-- Table: PLUGIN_SET
DROP TABLE IF EXISTS "plugin_set";
CREATE TABLE "plugin_set"(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status BOOLEAN,
    created timestamp,
    description TEXT
);

-- Table: PLUGIN_RELATIONSHIP
DROP TABLE IF EXISTS "plugin_relationship";
CREATE TABLE "plugin_relationship"(
    id SERIAL NOT NULL PRIMARY KEY,
    set_id INTEGER NOT NULL,
    plugin_id INTEGER NOT NULL
);

-- Table: PLUGIN
DROP TABLE IF EXISTS "plugin";
CREATE TABLE "plugin"(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    status BOOLEAN,
    created timestamp
);


-- Table: USER_GROUP
DROP TABLE IF EXISTS "user_group";
CREATE TABLE "user_group"(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id TEXT NOT NULL,
    group_id INTEGER NOT NULL
);


-- Table: GROUP
DROP TABLE IF EXISTS "group";
CREATE TABLE "group"(
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    created timestamp,
    updated timestamp,
    creator_id TEXT NOT NULL
);

-- Table: ACTIVATION
DROP TABLE IF EXISTS "activation";
CREATE TABLE "activation"(
    id SERIAL NOT NULL PRIMARY KEY,
    code TEXT NOT NULL,
    created timestamp,
    valid_until timestamp
);
