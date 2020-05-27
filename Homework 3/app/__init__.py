import sqlalchemy
import os

db_user = "root" #os.environ.get("DB_USER")
db_pass = "57js6E804y8Gb4im" #os.environ.get("DB_PASS")
db_name = "DbCloudComputing" #os.environ.get("DB_NAME")
db_public_ip = "35.233.43.207" #os.environ.get("DB_PUBLIC_IP")
cloud_sql_connection_name = "cloudt1:europe-west1:db-instance" #os.environ.get("CLOUD_SQL_CONNECTION_NAME")

db = sqlalchemy.create_engine('mysql+pymysql://' + db_user + ':' + db_pass + '@' +
                              db_public_ip + '/' + db_name)
