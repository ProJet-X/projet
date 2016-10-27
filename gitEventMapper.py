import time
import json

from datetime import datetime
import operator

from pyMongoDB import PyMongoDB 
from github import Github

def logGit():
    try:
        g = Github("ViniciusBVilar","asdf1234")
        gOrg = g.get_organization("TesteProGest")
        gRepo = gOrg.get_repo("progest")
        return gRepo
    except Exception as e:
        print(e)
        return null
    
class GitEventMapper(object):

    """docstring for GitEventMapper"""
    def __init__(self, gRepo):
        super(GitEventMapper, self).__init__()
        self.gRepo = gRepo
        ## Represents the points per milestones
        self.sprintsPoints = {}
        ## Represents the points per dev
        self.assigneesPoints = {}
        ## Represents the points per dev in which milestone
        self.sprintsPointsDevs = {}
        ## Represents the points per status
        self.statusPoints = {}
        ## Represents the points per dev in which status
        self.statusPointsDevs = {}

        ## Represents the number of issues per milestones
        self.sprintsIssues = {}
        ## Represents the number of issues per status
        self.statusIssues = {}
        ## Represents the number of issues per dev
        self.assigneesIssues = {}
        ## Represents the number of issues per dev in which milestone
        self.sprintsIssuesDevs = {}
        ## Represents the number of issues per dev in which status
        self.statusIssuesDevs = {}

        ## General events
        self.events = []

    def mapEvents(self):
        print("Iniciando mapeamento")
        startTimeEventsMap = datetime.now()
        print("TimeEventsMap")
        print(startTimeEventsMap)
        evo = []
        issues = []
        try:
            for e in self.gRepo.get_issues_events():
                event = {}
                if (e.event == "labeled" or e.event == "unlabeled") and e.issue.number not in issues:
                        if e.raw_data.get('label').get('name').rfind("-") != -1:
                                try:
                                        if int(e.raw_data.get("label").get("name").split(" - ")[0]) > 0:
                                                print("Issue #" + str(e.issue.number) + " deslocado para o estado: " + str(e.raw_data.get("label").get("name").split(" - ")[1]))
                                                points = -1
                                                try:
                                                        print(e.issue.title)
                                                        if e.issue.title.rfind("- PT") != -1:
                                                                points = int(e.issue.title.split(" - PT")[1])
                                                        elif e.issue.title.rfind("- pt") != -1:
                                                                points = int(e.issue.title.split(" - pt")[1])
                                                        elif e.issue.title.rfind("- Pt") != -1:
                                                                points = int(e.issue.title.split(" - Pt")[1])
                                                        else:
                                                                print("++++SEM PONTOS++++")
                                                except:
                                                        pass
                                                print(points)
                                                event = {
                                                'issue':e.issue.number,
                                                'actor':e.actor.login,
                                                'date':str(e.created_at),
                                                'status':e.raw_data.get('label').get('name').split(" - ")[0],
                                                'points':points
                                                }
                                                evo.append(event)
                                                issues.append(e.issue.number)
                                except:
                                        pass
        except:
            pass
        print(datetime.now() - startTimeEventsMap)
        print(len(evo))
        return evo

    def getMappedEvents(self):
        PyMongoDB.connectMongo()

        eventsColl = PyMongoDB.getEventsColl()
        if eventsColl.find({"repo_name": str(self.gRepo.name)}).count() == 1:
            print("Eventos já mapeados: ")
            
            eventsData = eventsColl.find_one({"repo_name": self.gRepo.name})

            evo = eventsData.get('evo')
            #print(eventsColl)
            #print(evo)
            print("Last updated: " + str(eventsData.get('last_update')))
            
        else:
            print("Iniciando mapeamendo do repo: " + str(self.gRepo.name))
            try:
                evo = self.mapEvents()
                print(len(evo))
                print("Repo mapeado")
                mappedEvents = {'repo_name':self.gRepo.name,
                         'evo':evo,
                         'last_update':str(datetime.now())}
                print(mappedEvents.keys())
                issue_id = eventsColl.insert_one(mappedEvents).inserted_id
                print("Colleção adicionada: " + str(issue_id))

                try:
                    # http://stackoverflow.com/questions/15415709/update-json-file
                    # http://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
                    # https://docs.python.org/2/tutorial/inputoutput.html
                    with open('event_' + str(datetime.now()) + '.txt', 'w') as outfile:
                        json.dump(mappedEvents, outfile)
                except:
                    print("Erro no arquivo de dump")
            
            except:
                print("Erro ao adicionar os dados ao banco de dados")
        return evo
