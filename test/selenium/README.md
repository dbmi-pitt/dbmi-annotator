##Selenium Test Scripts##

**How to run test**

There are two maven profiles (-P)

* **local-dev** - development environment (or local Ubuntu) which points to URL http://localhost/dbmiannotator
* **production-icode** - considered the production environment (on icode server) which points to URL http://dikb.org:80/dbmiannotator

Params to test against different browsers (-Dbrowser)
* ie
* chrome
* firefox    *(Not working with current version of FireFox)*


**Usage**

* `mvn -P local-dev -Dbrowser=ie integration-test`

* `mvn -P production-icode -Dbrowser=chrome integration-test`

* `mvn -P production-icode -Dbrowser=ie integration-test`

**this will test IE*

---

**Code organization**

all test inherit from a base class called TestBase.  This class contains only the beforeClass and afterClass methods for initializing the drivers, etc.  See test located in the **src/main/java/

***Test Suite***

You can run multiple tests by adding a new test class to the **testng.xml** file.

    <test name="BasicTests">
        <classes>
        <class name="dbmi.Login"/>

---
***NOTES:***
a resource directory exist which contain platform-specific executable drivers, i.e., Windows.  In the future, these test may be restructured to download the appropriate drivers, but for now this will work as is.

**local-dev**, since the Selenium test only run on Windows at the moment, you will need a secure shell to the NoMachine development instance , i.e., Putty with port forwarding established for ports 80 and 8081.


