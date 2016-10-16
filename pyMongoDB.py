import pymongo
from pymongo import MongoClient
from datetime import datetime

class PyMongoDB():

        """docstring for PyMongoDB"""
        def __init__(self, arg):
                super(PyMongoDB, self).__init__()
                self.arg = arg

        clientMongo = ""
        db = ""
        usersColl = ""
        issuesColl = ""
        eventsColl = ""

        def connectMongo():

                global clientMongo
                global db
                global issuesColl
                global usersColl
                global eventsColl


                print("\n")
                print(str(datetime.now()))
                print("MongoDB configs")
                try:
                        clientMongo = MongoClient()
                        print(clientMongo)
                        ## Could be
                        # client = MongoClient('mongodb://localhost:27017/')

                        db = clientMongo.test_database
                        print(db)
                        
                       
                        try:
                                usersColl = db.users
                                result = usersColl.create_index([('user_id', pymongo.ASCENDING)], unique=True)
                                print(str(result))
                        except:
                                pass
                        
                        try:
                                issuesColl = db.issues
                                result = issuesColl.create_index([('repo_name', pymongo.TEXT)], unique=True)
                                print(str(result))
                        except:
                                pass
                        try:
                                eventsColl = db.events
                                result = eventsColl.create_index([('repo_name', pymongo.TEXT)], unique=True)
                                print(str(result))
                        except:
                                pass

                        print("Finished mongoDB configs")
                except:
                        print("MongoDB config ERROR!")

        def countIssues():
                global issuesColl
                return issuesColl.find().count()

        def countUsers():
                global usersColl
                return usersColl.find().count()
        def countEvents():
                global eventsColl
                return eventsColl.find().count()

        def getIssuesColl():
                global issuesColl
                return issuesColl

        def getUsersColl():
                global usersColl
                return usersColl

        def getEventsColl():
                global eventsColl
                return eventsColl

        def resetIssuesColl():
                global issuesColl
                print(str(issuesColl.find().count()))
                issuesColl.drop()
                print(str(issuesColl.find().count()))

        def resetUsersColl():
                global usersColl
                print(str(usersColl.find().count()))
                usersColl.drop()
                print(str(usersColl.find().count()))

        def resetEventsColl():
                global eventsColl
                print(str(eventsColl.find().count()))
                eventsColl.drop()
                print(str(eventsColl.find().count()))
