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

module.exports = function(sequelize, Sequelize) {
    var Plugin = sequelize.define('plugin', {
	    id: {type: Sequelize.INTEGER, unique: true, primaryKey: true, autoIncrement: true} ,
	    name: Sequelize.TEXT,
	    type: Sequelize.TEXT,
	    description: Sequelize.TEXT,
        status: Sequelize.BOOLEAN,
	    created: Sequelize.DATE,
    });
    return Plugin;
}




