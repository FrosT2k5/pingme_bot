from mysql import connector
from os import environ

# Get the host, port, user password and database values from environment variables
db = connector.connect(
    host = environ.get("DB_HOST"),
    port = int(environ.get("DB_PORT")),
    user = environ.get("DB_USER"),
    password = environ.get("DB_PASSWORD"),
    database = environ.get("DB_NAME")
    )


# global cursor object, used throughout all functions
dbcursor = db.cursor()


# This function is used to insert record to database for the first time
def inserttodb(tguserid, tgusername, securitykey):
    query = "SELECT * from user ORDER BY id DESC LIMIT 1"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    if not answer:
        id = 1
    else:
        id = answer[0][0]+1

    query = "INSERT INTO user (id, tguserid, securitykey, tgusername) VALUES (%s,%s,%s,%s)"
    values = (id,tguserid,securitykey,tgusername)
    dbcursor.execute(query,values)
    db.commit()


# This function is used to update pin of already existing user in db
def updatepin(tguserid,securitykey,tgusername):
    query = "UPDATE user SET securitykey = %s,tgusername = %s WHERE tguserid = %s"
    values = (securitykey,tgusername,tguserid)
    dbcursor.execute(query,values)
    answer = dbcursor.fetchall()
    return 1


# This function prints full database, useful for debugging 
def printfulltable():
    query = "SELECT * FROM user"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    for x in answer:
        print(x)


# This function returns full record of user using userid, used to check for already existing user's in bot
def getusinguserid(userid):
    query = "SELECT * FROM user WHERE tguserid = %s"
    dbcursor.execute(query,[userid])
    answer = dbcursor.fetchall()
    if not answer:
        return 0
    else:
        return answer[0]


# This function returns full record of user using username, used in web api handler
def getusingusername(username):
    query = "SELECT * FROM user WHERE tgusername = %s"
    dbcursor.execute(query,[username])
    answer = dbcursor.fetchall()
    if not answer:
        return 0
    else:
        return answer[0]