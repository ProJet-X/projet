
from datetime import datetime

from bson.objectid import ObjectId
from timesheet import Timesheet

from pyMongoDB import PyMongoDB

class TimesheetsRepository(object):
    """ Repository implementing CRUD operations on timesheets collection in MongoDB """

    def __init__(self):
        # Access the MongoDB databases and collections
        print("TimesheetsRepo")
        
        self.database = PyMongoDB.getTimeSheetsColl()
        PyMongoDB.countTimeSheets()


    def create(self, timesheet):
        print("TimesheetsRepo")
        if timesheet is not None:
            self.database.timesheets.insert(timesheet.get_as_json())            
        else:
            raise Exception("Nothing to save, because timesheet parameter is None")


    def read(self, timesheet_id=None):
        if timesheet_id is None:
            return self.database.timesheets.find({})
        else:
            return self.database.timesheets.find({"_id":timesheet_id})


    def update(self, timesheet):
        if timesheet is not None:
            # the save() method updates the document if this has an _id property 
            # which appears in the collection, otherwise it saves the data
            # as a new document in the collection
            self.database.timesheets.save(timesheet.get_as_json())            
        else:
            raise Exception("Nothing to update, because timesheet parameter is None")


    def delete(self, timesheet):
        if timesheet is not None:
            self.database.timesheets.remove(timesheet.get_as_json())            
        else:
            raise Exception("Nothing to delete, because timesheet parameter is None")


    def getByUser(self, user=None):
        if user is None:
            return self.database.timesheets.find({})
        else:
            return self.database.timesheets.find({"user":user})
