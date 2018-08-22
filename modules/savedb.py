import socket
import pymongo

original_socket = socket.socket

def saveToDatabase(url, database, user, passwd, links):
    """
    Connects to a MongoDB
    Create Mongo Collection
    Add the links to the collection
    Args:
        url = url of the mongo server
        database = data that is being stored in the database
        user = username to login into Mongo
        passwd = password of Mongo
        link = URLs from the crawler
    if not url and not database:
        print("URL and DATABASE are null")
        print("Links are not stored into database")
        exit()
    """
    socket.socket = original_socket
    if not user and not passwd:
        client = pymongo.MongoClient(url)
    elif url and database and user and passwd:
        client = pymongo.MongoClient(url,
                                     username=user,
                                     password=passwd,
                                     authSource=database,
                                     authMechanism='SCRAM-SHA-256')
    else:
        print("Insufficient information to connect to Mongo")
        exit()
    try:
        db_con = client[database]
        db_con['torbot'].create_index('link', unique=True)
        for link in links:
            try:
                db_con['torbot'].insert_one({'link':link})
            except pymongo.errors.DuplicateKeyError:
                continue
    except Exception as e:
        print("Not able to Connect/Write to Mongo server.\nException: %s" % e)
        exit()
    print("Links added to Database")
    client.close()
