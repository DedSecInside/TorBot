import MySQLdb


def saveToDatabase(database, user, password, links):
        """
        Connects to a MYSQL DB
        Create MYSQL Table
        Add link to the DB

        Args:
                data = data that is being stored in the database
                user = username to login into MYSQL
                password = password of MYSQL
                link = URLs from the crawler
        """
        if not database and not user and not password:
                print("Wrong DB Credentials")
                exit()

        #Debug
        #print("Database:", database, "\nuser:",user, "\npass:",password)
        try:
            db = MySQLdb.connect(host="localhost",    # your host
                                    user=user,         # your username
                                    passwd=password,  # your password
                                    db=database)        # name of the data base

            cur = db.cursor()

        except :
            print("Unable to connect to database")

        try:
                query = """ CREATE TABLE IF NOT EXISTS `tor_url` (
                id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                link VARCHAR(30) NOT NULL UNIQUE,
                reg_date TIMESTAMP)"""
                cur.execute(query)
                for link in links:
                        query = "INSERT IGNORE INTO `tor_url` (link) VALUES ('{0}')".format(link)
                        cur.execute(query)
                        #print(query)
                db.commit()

        except (MySQLdb.Error, MySQLdb.Warning, TypeError, ValueError) as e:
                print(e)
                return None
        finally:
                cur.close()
                db.close()

