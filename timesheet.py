from bson.objectid import ObjectId

class Timesheet(object):
    """A class for storing Timesheet related information"""

    def __init__(self, timesheet_id=None, user=None, date=None, project=None,
                 begin=None, end=None, activity=None, issue=None, comment=None):        
        if timesheet_id is None:
            self._id = ObjectId()
        else:
            self._id = timesheet_id
        self.user = user
        self.date = date
        self.project = project
        self.begin = begin
        self.end = end
        self.activity = activity
        self.issue = issue
        self.comment = comment

    def get_as_json(self):
        """ Method returns the JSON representation of the Timesheet object, which can be saved to MongoDB """
        return self.__dict__
    

    @staticmethod    
    def build_from_json(json_data):
        """ Method used to build Timesheet objects from JSON data returned from MongoDB """
        if json_data is not None:
            try:                            
                return Timesheet(json_data.get('_id', None),
                    json_data['user'],
                    json_data['date'],
                    json_data['project'],
                    json_data['begin'],
                    json_data['end'],
                    json_data['activity'],
                    json_data['issue'],
                    json_data['comment'])
            except KeyError as e:
                raise Exception("Key not found in json_data: {}".format(e.message))
        else:
            raise Exception("No data to create Timesheet from!")
