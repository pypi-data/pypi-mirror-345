# same file as gailbotplugins , use it solely for the purpose of retrieving
# the complete url (including creator id) to a plugin in the bucket

import mysql.connector
from mysql.connector import Error



class RDSClient:
    def __init__(self):
        self.host = "plugin-db.c3aqee64crhq.us-east-1.rds.amazonaws.com"
        self.user = "admin"
        self.password = 'hilab12#'
        self.database = "gailbot"
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )


        except Error as e:
            print(f"Error connecting to RDS: {e}")
            self.connection = None
    
    def fetch_plugin_info(self, plugin_id):
        plugin_info = dict()
        if self.connection is None:
            print("No database connection.")
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT user_id FROM Plugins WHERE id = %s"
            cursor.execute(query, (plugin_id,))
            result = cursor.fetchone()
            
            print("Database row:", result)

            if result:
                plugin_info["user_id"] = result["user_id"]
            else:
                print(f"No user id found for plugin ID {plugin_id}")
                return None

            query = "SELECT name FROM Plugins WHERE id = %s"
            cursor.execute(query, (plugin_id,))
            result = cursor.fetchone()

            if result:
                plugin_info["name"] = result["name"]
            else:
                print(f"No name found for plugin ID {plugin_id}")
                return None

            query = "SELECT version FROM Plugins WHERE id = %s"
            cursor.execute(query, (plugin_id,))
            result = cursor.fetchone()

            if result:
                plugin_info["version"] = result["version"]
            else:
                print(f"No version found for plugin ID {plugin_id}")
                return None
            
            query = "SELECT s3_url FROM Plugins WHERE id = %s"
            cursor.execute(query, (plugin_id,))
            result = cursor.fetchone()
            
            if result:
                plugin_info["s3_url"] = result["s3_url"]
            else:
                print(f"No s3_url found for plugin ID {plugin_id}")
                return None

            
        except Error as e:
            print(f"Error fetching info for plugin in RDS Connect: {e}")
            return None
        finally:
            cursor.close()
        return plugin_info

    

        # CODE TO CHECK COLUMNS
        # if self.connection is None:
        #     print("No database connection.")
        #     return None

        # try:
        #     cursor = self.connection.cursor()
        #     query = "SHOW COLUMNS FROM Plugins"
        #     cursor.execute(query)
        #     columns = cursor.fetchall()

        #     column_names = [column[0] for column in columns]  # Extract column names
        #     print("column: ", column_names)
        #     return column_names
        # except Error as e:
        #     print(f"Error fetching column names: {e}")
        #     return None
        # finally:
        #     cursor.close()

    def fetch_suite_info(self, suite_id):
        suite_info = dict()
        if self.connection is None:
            print("No database connection.")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get user_id
            query = "SELECT user_id FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["user_id"] = result["user_id"]
            else:
                print(f"No user_id found for suite ID {suite_id}")
                return None

            # Get name
            query = "SELECT name FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["name"] = result["name"]
            else:
                print(f"No name found for suite ID {suite_id}")
                return None

            # Get description
            query = "SELECT description FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["description"] = result["description"]
            else:
                print(f"No description found for suite ID {suite_id}")
                return None

            # Get version
            query = "SELECT version FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["version"] = result["version"]
            else:
                print(f"No version found for suite ID {suite_id}")
                return None

            # Get published flag
            query = "SELECT published FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["published"] = result["published"]
            else:
                print(f"No published flag found for suite ID {suite_id}")
                return None

            # Get created_at timestamp
            query = "SELECT created_at FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["created_at"] = result["created_at"]
            else:
                print(f"No created_at timestamp found for suite ID {suite_id}")
                return None

            # Get updated_at timestamp
            query = "SELECT updated_at FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["updated_at"] = result["updated_at"]
            else:
                print(f"No updated_at timestamp found for suite ID {suite_id}")
                return None

            # Get s3_url
            query = "SELECT s3_url FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["s3_url"] = result["s3_url"]
            else:
                print(f"No s3_url found for suite ID {suite_id}")
                return None

            # Get is_active flag
            query = "SELECT is_active FROM Suites WHERE id = %s"
            cursor.execute(query, (suite_id,))
            result = cursor.fetchone()
            if result:
                suite_info["is_active"] = result["is_active"]
            else:
                print(f"No is_active flag found for suite ID {suite_id}")
                return None

        except Error as e:
            print(f"Error fetching suite info for RDS Connect: {e}")
            return None
        finally:
            cursor.close()
        return suite_info

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            # print("RDS connection closed")
