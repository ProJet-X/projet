import time
import json

from datetime import datetime
import operator

from pyMongoDB import PyMongoDB 
from github import Github


class GitMapper(object):

    """docstring for GitMapper"""
    def __init__(self, gRepo):
        super(GitMapper, self).__init__()
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
		
################################################################# 
#                    GITHUB - MAPPER 
#################################################################           
    def issueMapper(self,i):
        
        MAX_POINTS = 100

        ## Get sprint if the issue is milestones
        print("here" + str(totalPoints))
        print(str(i))
        if i.milestone == None:
            sprint = "Unk Sprint"
        else:
            sprint = i.milestone.title
        print("Sprint da issue #" + str(i.number) + ": " + str(sprint))
        
        ## Get assignee if the issue is assigned
        if i.assignee == None:
            developer = "Unk Dev"
        else:
            developer = i.assignee.login
        print("Colaborador envolvido na issue #" + str(i.number) + ": " + str(developer))
        if i.raw_data.get("pull_request") == None:
            ## Issues under points process rules
            try:
                ## Extract points
                if i.title.rfind("- PT") != -1:
                    pt = int(i.title.split(" - PT")[1])
                elif i.title.rfind("- pt") != -1:
                    pt = int(i.title.split(" - pt")[1])
                elif i.title.rfind("- Pt") != -1:
                    pt = int(i.title.split(" - Pt")[1])
                else:
                    self.totalIssuesWithoutPoints = self.totalIssuesWithoutPoints + 1
                    print("Issue #" + str(i.number) + " sem estimativa de pontos de esforço:")
                ## Points validation
                if pt > MAX_POINTS:
                    print("Issue #" + str(i.number) + " com pontos acima do limite estipulado")       
                    print("Estimativa de: " + str(pt))
                    pt = MAX_POINTS
                    print("Pontuação alterada para: " + str(pt))
                elif pt < 0:
                    print("Issue com pontos negativos: " + str(pt))
                    pt = pt * int(-1)
                    print("Pontuação alterada para: " + str(pt))
                print("Pontos da issue #" + str(i.number) + ", " + str(i.title) + ": " + str(pt))
                totalPoints = totalPoints + pt
                self.totalIssuesWithPoints = self.totalIssuesWithPoints + 1
                ## Milestone points
                if list(self.sprintsPoints.keys()).count(sprint) == 1:
                    self.sprintsPoints[sprint] = self.sprintsPoints[sprint] + pt
                else:
                    self.sprintsPoints[sprint] = pt
                ## Assignees points
                if list(self.assigneesPoints.keys()).count(developer) == 1:
                    self.assigneesPoints[developer] = self.assigneesPoints[developer] + pt
                else:
                    self.assigneesPoints[developer] = pt
                ## Assignees points per sprint
                if list(self.sprintsPointsDevs.keys()).count(sprint) == 1:
                    if list(self.sprintsPointsDevs[sprint].keys()).count(developer) == 1:
                        self.sprintsPointsDevs[sprint][developer] = self.sprintsPointsDevs[sprint][developer] + pt
                    else:
                        self.sprintsPointsDevs[sprint].update({developer: pt})
                else:
                    self.sprintsPointsDevs[sprint] = {developer: pt}
                ## Status labels points 
                for l in i.get_labels():
                    status = l.name
                    if status.rfind("-") != -1:
                        if list(self.statusPoints.keys()).count(status) == 1:
                            self.statusPoints[status] = self.statusPoints[status] + pt
                        else:
                            self.statusPoints[status] = pt
                    ## Assignees points per status
                    if list(self.statusPointsDevs.keys()).count(status) == 1:
                        if list(self.statusPointsDevs[status].keys()).count(developer) == 1:
                            self.statusPointsDevs[status][developer] = self.statusPointsDevs[status][developer] + pt
                        else:
                            self.statusPointsDevs[status].update({developer: pt})
                    else:
                        self.statusPointsDevs[status] = {developer: pt}
            except:
                print("Problema nos pontos da issue #" + str(i.number) + " " + str(i.title))
                print("!_________________________!_________________________!")
        else:
            print("Pull request: issue #" + str(i.number))
            self.totalPullRequest = self.totalPullRequest + 1
            #print(str(i.body))
            #print(i.body.split("- #")[1])
            print("\n")
            
        try:
            ## Total number of issues
            self.totalIssues = self.totalIssues + 1
            ## Milestone number of tasks
            if list(self.sprintsIssues.keys()).count(sprint) == 1:
                self.sprintsIssues[sprint] = self.sprintsIssues[sprint] + 1
            else:
                self.sprintsIssues[sprint] = 1
            ## Assignees number of tasks
            if list(self.assigneesIssues.keys()).count(developer) == 1:
                self.assigneesIssues[developer] = self.assigneesIssues[developer] + 1
            else:
                self.assigneesIssues[developer] = 1
            ## Assignees number of tasks per sprint
            if list(self.sprintsIssuesDevs.keys()).count(sprint) == 1:
                if list(self.sprintsIssuesDevs[sprint].keys()).count(developer) == 1:
                    self.sprintsIssuesDevs[sprint][developer] = self.sprintsIssuesDevs[sprint][developer] + 1
                else:
                    self.sprintsIssuesDevs[sprint].update({developer: 1})
            else:
                self.sprintsIssuesDevs[sprint] = {developer: 1}    
            ## Status labels number of tasks
            for l in i.get_labels():
                status = l.name
                print("Labels: " + status)
                ## Status labels
                if status.rfind("-") != -1:
                    if list(self.statusIssues.keys()).count(status) == 1:
                        self.statusIssues[status] = self.statusIssues[status] + 1
                    else:
                        self.statusIssues[status] = 1
                ## Assignees number of tasks per status
                if list(self.statusIssuesDevs.keys()).count(status) == 1:
                    if list(self.statusIssuesDevs[status].keys()).count(developer) == 1:
                        self.statusIssuesDevs[status][developer] = self.statusIssuesDevs[status][developer] + 1
                    else:
                        self.statusIssuesDevs[status].update({developer: 1})
                else:
                    self.statusIssuesDevs[status] = {developer: 1}
        except:
            print("Problema com a issue #" + str(i.number) +" "+str(i.title))
            print("!______________!______________!______________!______________!")
            
        #### Events track
        print("Aberta em: " + str(i.created_at))
       
        if mapEvents == True:
            eventActorTime.clear()
            eventActorTime.append({'event':'creation', 'created_at': str(i.created_at)})
            for e in i.get_events():
                if e.event == "assigned" or e.event == "unassigned":
                    actor = e.raw_data.get("assigner").get("login")
                else:
                    actor = e.actor.login
                print(str(e.event) + " por " + str(actor) + " em: " + str(e.created_at))
                if e.event == "closed" or e.event == "reopened":
                    print(" Fechada em: " + str(i.closed_at))
                    detail = {'closed_at':str(i.closed_at)}
                elif e.event == "labeled" or e.event == "unlabeled":
                    if (e.raw_data.get("label").get("name").rfind("-") != -1):
                        if int(e.raw_data.get("label").get("name").split(" - ")[0]) > 0:
                            print(" Deslocado para o estado: " + str(e.raw_data.get("label").get("name").split(" - ")[1]))
                        detail = {'status':e.raw_data.get("label").get("name")}
                    else:
                        print(" (Des)Associada ao label: " + str(e.raw_data.get("label").get("name")))
                        detail = {'label':e.raw_data.get("label").get("name")}
                elif e.event == "milestoned" or e.event == "demilestoned":
                    print(" (Des)Associada ao sprint: " + str(e.raw_data.get("milestone").get("title")))
                    detail = {'milestone':e.raw_data.get("milestone").get("title")}
                elif e.event == "assigned" or e.event == "unassigned":
                    print(" (Des)Associado ao colaborador: " + str(e.raw_data.get("assignee").get("login")))
                    print(" Pelo colaborador: " + str(e.raw_data.get("assigner").get("login")))
                    detail = {'assignee':e.raw_data.get("assignee").get("login"), 'assigner':e.raw_data.get("assigner").get("login")}
                elif e.event == "renamed":
                    print(" Nome alterado de: " + str(e.raw_data.get("rename").get("from")))
                    print(" Para: " + str(e.raw_data.get("rename").get("to")))
                    detail = {'from':e.raw_data.get("rename").get("from"), 'to':e.raw_data.get("rename").get("to")}
                #print("Details " + str(detail))
                ## Events with actor and time
                eventActorTime.append({'event':e.event,'actor':actor,'created_at': str(e.created_at), 'detail':detail.copy()})
                #print("EAT " + str(eventActorTime))
            issueEvent = {str(i.number):eventActorTime.copy()}
            self.events.append(issueEvent.copy())
            print("Appending issue #" + str(i.number) + "events")
            print(str(len(self.events)))
        print("Issue mapeada")
        print("\n")

    #################################################################
    #                    GITHUB - Logger    
    #################################################################

    def printLog(self) :
        
        print("Pontos totais: " + str(totalPoints))
        for sP in self.sprintsPoints:
            print("Pontos totais do sprint " + str(sP) + ": " + str(self.sprintsPoints[sP]))
        for aP in self.assigneesPoints:
            print("Pontos totais do colaborador: " + str(aP) + ": " + str(self.assigneesPoints[aP]))
        for sDP in self.sprintsPointsDevs:
            print("Pontos do colaborador no sprint: " + str(sDP) + ": " + str(self.sprintsPointsDevs[sDP]))
        for stP in self.statusPoints:
            print("Pontos por status: " + str(stP) + ": " + str(self.statusPoints[stP]))
        for stPD in self.statusPointsDevs:
            print("Pontos do colaborador no status: " + str(stPD) + ": " + str(self.statusPointsDevs[stPD]))
        print("\n")

        print("Numero de tarefas totais: " + str(self.totalIssues))
        print("Numero de tarefas como Pull Request: " + str(self.totalPullRequest))
        for sI in self.sprintsIssues:
            print("Numero de tarefas totais do sprint " + str(sI) + ": " + str(self.sprintsIssues[sI]))
        for aI in self.assigneesIssues:
            print("Numero de tarefas totais do colaborador: " + str(aI) + ": " + str(self.assigneesIssues[aI]))
        for sID in self.sprintsIssuesDevs:
            print("Numero de tarefas do colaborador no sprint: " + str(sID) + ": " + str(self.sprintsIssuesDevs[sID]))
        for stI in self.statusIssues:
            print("Numero de tarefas por status: " + str(stI) + ": " + str(self.statusIssues[stI]))
        for stID in self.statusIssuesDevs:
            print("Numero de tarefas do colaborador no status: " + str(stID) + ": " + str(self.statusIssuesDevs[stID]))
        print("Quantidade de issues com eventos: " + str(len(self.events)))
        print("\n")
        #####################
        #Estimator.estimate()
        print("\n")



    #################################################################
    #                    GITHUB - MAPPER    
    #################################################################
    def repoMapper(gRepo):
        print("here")
        try:
            issueId = ""
            if issueId == "":
                ## Lookup for all issues in repo
                lookup = True
                issueCounter = 1
                while lookup == True:
                    try:
                        issue = gRepo.get_issue(issueCounter)
                        print(issue)
                        GitMapper.issueMapper(issue)
                        print("issue mapped")
                        issueCounter = issueCounter + 1
                    except:
                        print("Last issue")
                        lookup = False
            else:
                issue = gRepo.get_issue(issueId)
                issueMapper(issue)
            GitMapper.printLog()
        except:
            print("Issue não existe")
     
        
    #################################################################
    #                        PROCESS    
    #################################################################
    
    def startMetrics(self):
        PyMongoDB.connectMongo()
        issuesMapped = {}
        i=0
        print("Colaboradores do repositorio:")
        for x in self.gRepo.get_collaborators():
            print(x.login)
        print("Alocáveis do repositorio:")
        for x in self.gRepo.get_assignees():
            print(x.login)
        print("\n")
                   
        startTimeMetrics = datetime.now()
        print("TimeMetrics")
        print(startTimeMetrics)
        print("\n")
        issuesColl = PyMongoDB.getIssuesColl()
        if issuesColl.find({"repo_name": str(self.gRepo.name)}).count() == 1:
            print("Existe repo mapeado: ")
            
            issuesData = issuesColl.find_one({"repo_name": self.gRepo.name})
            
            totalPoints = issuesData.get('total_points')
            totalIssues = issuesData.get('total_issues')
            totalPullRequest = issuesData.get('total_pull_request')
            totalIssuesWithPoints = issuesData.get('total_issues_with_points')
            totalIssuesWithoutPoints = issuesData.get('total_issues_without_points')
            
            sprintsPoints = issuesData.get('sprints_points')
            sprintsIssues = issuesData.get('sprints_issues')
            
            statusPoints = issuesData.get('status_points')
            statusIssues = issuesData.get('status_issues')

            assigneesPoints = issuesData.get('assignees_points')
            assigneesIssues = issuesData.get('assignees_issues')

            sprintsPointsDevs = issuesData.get('sprints_points_devs')
            sprintsIssuesDevs = issuesData.get('sprints_issues_devs')

            statusPointsDevs = issuesData.get('status_points_devs')
            statusIssuesDevs = issuesData.get('status_issues_devs')

            events = issuesData.get('events')
            print("Last updated: " + str(issuesData.get('last_update')))
            issuesMapped = {'repo_name':self.gRepo.name,
                         'total_points':totalPoints,
                         'total_issues':totalIssues,
                         'total_pull_request':totalPullRequest,
                         'total_issues_with_points':totalIssuesWithPoints,
                         'total_issues_without_points':totalIssuesWithoutPoints,
                         'sprints_points':sprintsPoints,
                         'sprints_issues':sprintsIssues,
                         'status_points':statusPoints,
                         'status_issues':statusIssues,
                         'assignees_points':assigneesPoints,
                         'assignees_issues':assigneesIssues,
                         'sprints_points_devs':sprintsPointsDevs,
                         'sprints_issues_devs':sprintsIssuesDevs,
                         'status_points_devs':statusPointsDevs,
                         'status_issues_devs':statusIssuesDevs,
                         'events':events,
                         'last_update':str(startTimeMetrics)}
        else:
            print("Iniciando mapeamendo do repo: " + str(self.gRepo.name))
            try:
                try:
                    print("A")
                    self.repoMapper(self.gRepo)
                except Exception as e:
                    print("B" + str(e))
                    raise
                else:
                    print("C")
                    
                finally:
                    print("D")
                    try:
                        print("E")
                        self.repoMapper(self.gRepo)
                    except:
                        pass
                print("Repo mapeado")
                issuesMapped = {'repo_name':self.gRepo.name,
                         'total_points':totalPoints,
                         'total_issues':totalIssues,
                         'total_pull_request':totalPullRequest,
                         'total_issues_with_points':totalIssuesWithPoints,
                         'total_issues_without_points':totalIssuesWithoutPoints,
                         'sprints_points':sprintsPoints,
                         'sprints_issues':sprintsIssues,
                         'status_points':statusPoints,
                         'status_issues':statusIssues,
                         'assignees_points':assigneesPoints,
                         'assignees_issues':assigneesIssues,
                         'sprints_points_devs':sprintsPointsDevs,
                         'sprints_issues_devs':sprintsIssuesDevs,
                         'status_points_devs':statusPointsDevs,
                         'status_issues_devs':statusIssuesDevs,
                         'events':events,
                         'last_update':str(startTimeMetrics)}
                print(issuesMapped.keys())
                issue_id = issuesColl.insert_one(issuesMapped).inserted_id
                print("Colleção adicionada: " + str(issue_id))
                # http://stackoverflow.com/questions/15415709/update-json-file
                # http://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
                # https://docs.python.org/2/tutorial/inputoutput.html
                #with open('issuesMappedDumpJSON.txt', 'w') as outfile:
                #    json.dump(issuesMapped, outfile)
            except:
                print("Erro ao adicionar os dados ao banco de dados")
        print(datetime.now() - startTimeMetrics)
        print("\n")
        return issuesMapped
