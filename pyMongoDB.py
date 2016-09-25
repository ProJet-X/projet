import pymongo
from pymongo import MongoClient
from datetime import datetime

class PyMongoDB():

        clientMongo = ""
        db = ""
        usersColl = ""
        issuesColl = ""

        def connectMongo():

                global clientMongo
                global db
                global issuesColl
                global usersColl

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

                        usersColl = db.users
                        issuesColl = db.issues
                        #eventsColl = db.events
                        print(usersColl)

                        try:
                                result = usersColl.create_index([('user_id', pymongo.ASCENDING)], unique=True)
                                print(str(result))
                        except:
                                pass
                        
                        try:
                                result = issuesColl.create_index([('repo_name', pymongo.TEXT)], unique=True)
                                print(str(result))
                        except:
                                pass
                        print(usersColl.index_information())
                        print("Finished mongoDB configs")
                except:
                        print("MongoDB config ERROR!")

        def countIssues():
                global issuesColl
                return issuesColl.find().count()

        def countUsers():
                global usersColl
                return usersColl.find().count()

        def getIssuesColl():
                global issuesColl
                return issuesColl

        def getUsersColl():
                global usersColl
                return usersColl


        def resetIssuesColl():
                global issuesColl
                issuesColl.drop()
                print(str(issuesColl.find().count()))

        def resetUsersColl():
                global usersColl
                usersColl.drop()
                print(str(usersColl.find().count()))
