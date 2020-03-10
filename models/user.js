/* Copyright 2016-2017 University of Pittsburgh

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http:www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License. */

var bcrypt = require('bcryptjs');

module.exports = function (sequelize, Sequelize) {
    const User = sequelize.define('user', {
        id: {type: Sequelize.INTEGER, unique: true, primaryKey: true, autoIncrement: true},
        uid: Sequelize.TEXT,
        username: Sequelize.TEXT,
        admin: Sequelize.BOOLEAN,
        manager: Sequelize.BOOLEAN,
        email: Sequelize.TEXT,
        status: Sequelize.INTEGER,
        last_login_date: Sequelize.DATE,
        registered_date: Sequelize.DATE,
        activation_id: Sequelize.INTEGER,
        password: Sequelize.TEXT
    }, {});

    User.associate = function (models) {
    };

    User.validPassword = function (password1, password2) {
        return bcrypt.compareSync(password1, password2);
    };
    User.generateHash = function (password) {
        return bcrypt.hashSync(password, bcrypt.genSaltSync(8));
    };

    return User;
};




