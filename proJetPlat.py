import time
import json

from datetime import datetime, date, time, timedelta
import operator

from chartFileHelper import ChartFileHelper
from timeEstimator import Estimator
from gitMapper import GitMapper
from gitEventMapper import GitEventMapper
from timesheetsRepository import TimesheetsRepository
from timesheet import Timesheet


from pyMongoDB import PyMongoDB 
from github import Github

from flask import Flask, render_template, session, redirect, url_for, escape, request
app = Flask(__name__)

print("********************************************")
print("Welcome to ProJet analytics dashboard trace")
print("ProJet v0.0.5")
print(str(datetime.now()))
print("********************************************")
print("\n")

################################################################# 
#                    DataBase Mongo 
#################################################################

PyMongoDB.connectMongo()

################################################################# 
#                        VARIABLES 
#################################################################
gOrg = ""
gRepo = ""

graphsURLs = []
eventGraphsURLs = []

repoLabels = []

# GitHub trace variables
mapEvents = False

totalPoints = 0
totalIssues = 0
totalIssuesWithPoints = 0
totalIssuesWithoutPoints = 0
totalPullRequest = 0

## Represents the points per milestones
sprintsPoints = {}
## Represents the points per dev
assigneesPoints = {}
## Represents the points per dev in which milestone
sprintsPointsDevs = {}
## Represents the points per status
statusPoints = {}
## Represents the points per dev in which status
statusPointsDevs = {}

## Represents the number of issues per milestones
sprintsIssues = {}
## Represents the number of issues per status
statusIssues = {}
## Represents the number of issues per dev
assigneesIssues = {}
## Represents the number of issues per dev in which milestone
sprintsIssuesDevs = {}
## Represents the number of issues per dev in which status
statusIssuesDevs = {}

## General events
events = []
evo = []

sessionStartTime = 0

syncDays = 6


################################################################################################################### 
#                    GITHUB - MAPPER 
#################################################################           
def issueMapper(i):
    
    global totalPoints
    global totalIssues
    global totalIssuesWithPoints
    global totalIssuesWithoutPoints
    global totalPullRequest
    
    global sprintsPoints
    global assigneesPoints
    global sprintsPointsDevs
    global statusPoints
    global statusPointsDevs
    
    global sprintsIssues
    global assigneesIssues
    global sprintsIssuesDevs
    global statusIssues
    global statusIssuesDevs

    global events

    
    MAX_POINTS = 100

    ## Get sprint if the issue is milestones
    
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
                totalIssuesWithoutPoints = totalIssuesWithoutPoints + 1
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
            totalIssuesWithPoints = totalIssuesWithPoints + 1
            ## Milestone points
            if list(sprintsPoints.keys()).count(sprint) == 1:
                sprintsPoints[sprint] = sprintsPoints[sprint] + pt
            else:
                sprintsPoints[sprint] = pt
            ## Assignees points
            if list(assigneesPoints.keys()).count(developer) == 1:
                assigneesPoints[developer] = assigneesPoints[developer] + pt
            else:
                assigneesPoints[developer] = pt
            ## Assignees points per sprint
            if list(sprintsPointsDevs.keys()).count(sprint) == 1:
                if list(sprintsPointsDevs[sprint].keys()).count(developer) == 1:
                    sprintsPointsDevs[sprint][developer] = sprintsPointsDevs[sprint][developer] + pt
                else:
                    sprintsPointsDevs[sprint].update({developer: pt})
            else:
                sprintsPointsDevs[sprint] = {developer: pt}
            ## Status labels points 
            for l in i.get_labels():
                status = l.name
                if status.rfind("-") != -1:
                    if list(statusPoints.keys()).count(status) == 1:
                        statusPoints[status] = statusPoints[status] + pt
                    else:
                        statusPoints[status] = pt
                ## Assignees points per status
                if list(statusPointsDevs.keys()).count(status) == 1:
                    if list(statusPointsDevs[status].keys()).count(developer) == 1:
                        statusPointsDevs[status][developer] = statusPointsDevs[status][developer] + pt
                    else:
                        statusPointsDevs[status].update({developer: pt})
                else:
                    statusPointsDevs[status] = {developer: pt}
        except:
            print("Problema nos pontos da issue #" + str(i.number) + " " + str(i.title))
            print("!_________________________!_________________________!")
    else:
        print("Pull request: issue #" + str(i.number))
        totalPullRequest = totalPullRequest + 1
        #print(str(i.body))
        #print(i.body.split("- #")[1])
        print("\n")
        
    try:
        ## Total number of issues
        totalIssues = totalIssues + 1
        ## Milestone number of tasks
        if list(sprintsIssues.keys()).count(sprint) == 1:
            sprintsIssues[sprint] = sprintsIssues[sprint] + 1
        else:
            sprintsIssues[sprint] = 1
        ## Assignees number of tasks
        if list(assigneesIssues.keys()).count(developer) == 1:
            assigneesIssues[developer] = assigneesIssues[developer] + 1
        else:
            assigneesIssues[developer] = 1
        ## Assignees number of tasks per sprint
        if list(sprintsIssuesDevs.keys()).count(sprint) == 1:
            if list(sprintsIssuesDevs[sprint].keys()).count(developer) == 1:
                sprintsIssuesDevs[sprint][developer] = sprintsIssuesDevs[sprint][developer] + 1
            else:
                sprintsIssuesDevs[sprint].update({developer: 1})
        else:
            sprintsIssuesDevs[sprint] = {developer: 1}    
        ## Status labels number of tasks
        for l in i.get_labels():
            status = l.name
            print("Labels: " + status)
            ## Status labels
            if status.rfind("-") != -1:
                if list(statusIssues.keys()).count(status) == 1:
                    statusIssues[status] = statusIssues[status] + 1
                else:
                    statusIssues[status] = 1
            ## Assignees number of tasks per status
            if list(statusIssuesDevs.keys()).count(status) == 1:
                if list(statusIssuesDevs[status].keys()).count(developer) == 1:
                    statusIssuesDevs[status][developer] = statusIssuesDevs[status][developer] + 1
                else:
                    statusIssuesDevs[status].update({developer: 1})
            else:
                statusIssuesDevs[status] = {developer: 1}
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
        events.append(issueEvent.copy())
        print("Appending issue #" + str(i.number) + "events")
        print(str(len(events)))
    print("Issue mapeada")
    print("\n")

#################################################################
#                    GITHUB - Logger    
#################################################################

def printLog() :
    global totalPoints
    global totalIssues
    global totalPullRequest
    
    global sprintsPoints
    global assigneesPoints
    global sprintsPointsDevs
    global statusPoints
    global statusPointsDevs
    
    global sprintsIssues
    global assigneesIssues
    global sprintsIssuesDevs
    global statusIssues
    global statusIssuesDevs
    
    print("Pontos totais: " + str(totalPoints))
    for sP in sprintsPoints:
        print("Pontos totais do sprint " + str(sP) + ": " + str(sprintsPoints[sP]))
    for aP in assigneesPoints:
        print("Pontos totais do colaborador: " + str(aP) + ": " + str(assigneesPoints[aP]))
    for sDP in sprintsPointsDevs:
        print("Pontos do colaborador no sprint: " + str(sDP) + ": " + str(sprintsPointsDevs[sDP]))
    for stP in statusPoints:
        print("Pontos por status: " + str(stP) + ": " + str(statusPoints[stP]))
    for stPD in statusPointsDevs:
        print("Pontos do colaborador no status: " + str(stPD) + ": " + str(statusPointsDevs[stPD]))
    print("\n")

    print("Numero de tarefas totais: " + str(totalIssues))
    print("Numero de tarefas como Pull Request: " + str(totalPullRequest))
    for sI in sprintsIssues:
        print("Numero de tarefas totais do sprint " + str(sI) + ": " + str(sprintsIssues[sI]))
    for aI in assigneesIssues:
        print("Numero de tarefas totais do colaborador: " + str(aI) + ": " + str(assigneesIssues[aI]))
    for sID in sprintsIssuesDevs:
        print("Numero de tarefas do colaborador no sprint: " + str(sID) + ": " + str(sprintsIssuesDevs[sID]))
    for stI in statusIssues:
        print("Numero de tarefas por status: " + str(stI) + ": " + str(statusIssues[stI]))
    for stID in statusIssuesDevs:
        print("Numero de tarefas do colaborador no status: " + str(stID) + ": " + str(statusIssuesDevs[stID]))
    print("Quantidade de issues com eventos: " + str(len(events)))
                
    print("\n")
    #####################
    #Estimator.estimate()
    print("\n")



#################################################################
#                    GITHUB - MAPPER    
#################################################################
def repoMapper(gRepo):
    global repoLabels

    global totalPoints
    global totalIssues
    global totalIssuesWithPoints
    global totalIssuesWithoutPoints
    global totalPullRequest
    
    global sprintsPoints
    global assigneesPoints
    global sprintsPointsDevs
    global statusPoints
    global statusPointsDevs
    
    global sprintsIssues
    global assigneesIssues
    global sprintsIssuesDevs
    global statusIssues
    global statusIssuesDevs

    global events


    totalPoints = 0
    totalIssues = 0
    totalIssuesWithPoints = 0
    totalIssuesWithoutPoints = 0
    totalPullRequest = 0
    
    sprintsPoints = {}
    assigneesPoints = {}
    sprintsPointsDevs = {}
    statusPoints = {}
    statusPointsDevs = {}
    
    sprintsIssues = {}
    statusIssues = {}
    assigneesIssues = {}
    sprintsIssuesDevs = {}
    statusIssuesDevs = {}
    events = []
    
    try:
        issueId = ""
        if issueId == "":
            ## Lookup for all issues in repo
            lookup = True
            issueCounter = 1
            while lookup == True:
                try:
                    issue = gRepo.get_issue(issueCounter)
                    issueMapper(issue)
                    print("issue mapped")
                    issueCounter = issueCounter + 1
                except:
                    print("Last issue")
                    lookup = False
            for labels in gRepo.get_labels():
                repoLabels.append({"name" : labels.name, "color": labels.color})        
        else:
            issue = gRepo.get_issue(issueId)
            issueMapper(issue)
        printLog()
    except:
        print("Issue não existe")
 


###################################################################################################################
#                        Dashboar data    
#################################################################

def startMetrics():
    
    global gRepo

    global totalPoints
    global totalIssues
    global totalPullRequest
    global totalIssuesWithPoints
    global totalIssuesWithoutPoints
    
    global sprintsPoints
    global sprintsIssues
    
    global assigneesPoints
    global assigneesIssues
    
    global statusPoints
    global statusIssues

    global sprintsPointsDevs
    global sprintsIssuesDevs
    
    global statusPointsDevs
    global statusIssuesDevs

    global events
    global repoLabels

    global syncDays

    global evo

##    metrics = {}
##    try:
##        metrics = GitMapper.startMetrics(gRepo,PyMongoDB)
##    except Exception as e:
##        print("GitMapper error: " + str(e))
##    print(metrics.keys())


    try:
        print("Events Map")
        gEM = GitEventMapper(gRepo)
        evo = gEM.getMappedEvents()
    except Exception as e:
        print("GitEventsMapper error: " + str(e))
    
    print("\n")
    print("\n")
    print("\n")
    i=0
    print("Colaboradores do repositorio:")
    #for x in gRepo.get_collaborators():
    #    print(x.login)
    print("Alocáveis do repositorio:")
    #for x in gRepo.get_assignees():
    #    print(x.login)
    print("\n")
               
    startTimeMetrics = datetime.now()
    print("TimeMetrics")
    print(startTimeMetrics)
    print("\n")
    issuesColl = PyMongoDB.getIssuesColl()
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")

    print(sprintsPointsDevs)
    
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    

    lastUpdate = ""
    outDated = False
    alreadyMapped = issuesColl.find({"repo_name": str(gRepo.name)}).count() == 1
    if alreadyMapped:
        print("Existe repo mapeado: ")
        
        issuesData = issuesColl.find_one({"repo_name": gRepo.name})
        
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
        print(sprintsPointsDevs)
        statusPointsDevs = issuesData.get('status_points_devs')
        statusIssuesDevs = issuesData.get('status_issues_devs')

        events = issuesData.get('events')
        repoLabels = issuesData.get('repoLabels')

        lastUpdate = issuesData.get('last_update')
        print("Last updated: " + str(lastUpdate))
        outDated = datetime.strptime(lastUpdate, '%Y-%m-%d %H:%M:%S.%f') < datetime.now() - timedelta(days=syncDays)
        if outDated:
            print("Passou de" + str(syncDays) + "dias")
        else:
            print("Dentro do periodo de atualização")
        
    if not alreadyMapped or outDated:
        print("Iniciando mapeamendo do repo: " + str(gRepo.name))
        try:
            repoMapper(gRepo)
            print("Repo mapeado")
            issueMapped = {'repo_name':gRepo.name,
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
                     'repoLabels':repoLabels,
                     'last_update':str(startTimeMetrics)}
            print(issueMapped.keys())
            issue_id = issuesColl.insert_one(issueMapped).inserted_id
            print("Colleção adicionada: " + str(issue_id))

            try:
                # http://stackoverflow.com/questions/15415709/update-json-file
                # http://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
                # https://docs.python.org/2/tutorial/inputoutput.html
                with open('issueMappedDumpJSON.txt', 'w') as outfile:
                    json.dump(issueMapped, outfile)
            except:
                print("Erro no arquivo de dump")
        
        except:
            print("Erro ao adicionar os dados ao banco de dados")
    print(datetime.now() - startTimeMetrics)
    print("\n")



###################################################################################################################
#                        RENDERER - AREA CHART
#################################################################

def eventChart():
    global evo
    dataPoints = []
    dataIssues = []
    i = 0
    e = evo.copy()
    print("#Eventos: " + str(len(e)))
    while i < len(e):
        pointsQA = 0
        issuesQA = 0
        pointsDone = 0
        issuesDone = 0
        d = datetime.strptime(e[i].get('date'), '%Y-%m-%d %H:%M:%S').strftime('%m-%d')
        

        if int(e[i].get('status')) == 4:
            issuesQA = issuesQA + 1
            if  int(e[i].get('points')) > 0:
                pointsQA = pointsQA + e[i].get('points')
            else:
                print("SEM ESTIMATIVA")
        elif int(e[i].get('status')) == 4:
            issuesDone = issuesDone + 1
            if  int(e[i].get('points')) > 0:
                pointsDone = pointsDone + e[i].get('points')
            else:
                print("SEM ESTIMATIVA")
        
        lookupEvents = False
        j = i + 1
        while lookupEvents and j < len(e):
            
            if d == datetime.strptime(e[j].get('date'), '%Y-%m-%d %H:%M:%S').strftime('%m-%d'):
                print("B")
                if int(e[j].get('status')) == 4:
                    issuesQA = issuesQA + 1
                    if  int(e[j].get('points')) > 0:
                        pointsQA = pointsQA + e[j].get('points')
                    else:
                        print("SEM ESTIMATIVA")
                elif int(e[j].get('status')) == 4:
                    issuesDone = issuesDone + 1
                    if  int(e[j].get('points')) > 0:
                        pointsDone = pointsDone + e[j].get('points')
                    else:
                        print("SEM ESTIMATIVA")
                print(len(e))
                print("Issue: " + str(e[j].get('issue')))
                del e[j]
                print(len(e))
            else:
                lookupEvents = False
                j = j + 1
        dataPoints.append({ 'y': d, 'a': pointsQA, 'b': pointsDone })
        dataIssues.append({ 'y': d, 'a': issuesQA, 'b': issuesDone })
        i = i + 1
    return dataPoints

#################################################################
#                        RENDERER
#################################################################

def renderDashboard(org, repo):
    global graphsURLs
    global eventGraphsURLs
    global gRepo
    global gOrg

    global totalPoints
    global totalIssues
    global totalPullRequest
    global totalIssuesWithPoints
    global totalIssuesWithoutPoints
    
    global sprintsPoints
    global assigneesPoints
    global sprintsPointsDevs
    global statusPoints
    global statusPointsDevs
    
    global sprintsIssues
    global assigneesIssues
    global sprintsIssuesDevs
    global statusIssues
    global statusIssuesDevs

    global repoLabels

    global evo
    
    print(org)
    print(repo)
    print("Iniciando dashboard")
    print(gOrg)
    print(gRepo)

    print(graphsURLs)
    a = "Comparação por colaborador"
    b = "Comparação por sprint"

    orgs = ["AAa","BBb","cCC","dDD"]
     
    charts = []
    try:
        charts.append(graphsURLs[0])
        charts.append(graphsURLs[1])
        charts.append(graphsURLs[2])
        charts.append(graphsURLs[3])
        charts.append(graphsURLs[4])
        charts.append(graphsURLs[5])
 
    except:
        g0=0
        g1=0
        g2=0
        g3=0
        g4=0
        g5=0
      
    issuesIndicators = []
    issuesIndicators.append(totalIssues)
    issuesIndicators.append(totalIssues - totalPullRequest)
    issuesIndicators.append(totalPullRequest)
    issuesIndicators.append(totalPoints)
    issuesIndicators.append(totalIssuesWithPoints)
    issuesIndicators.append(totalIssuesWithoutPoints)

    print("Events graphs")
    print(eventGraphsURLs)
    try:
        charts.append(eventGraphsURLs[0])
        charts.append(eventGraphsURLs[1])
        charts.append(eventGraphsURLs[2])
        charts.append(eventGraphsURLs[3])
    except:
        g6=0
        g7=0
        g8=0
        g9=0

    devs=1
    taskId=2
    taskPoints=3
    created_at=4
    working=5
    done=6
    
    labelsBarA = 'Issues'
    labelsBarB = 'Points'
    
    dataBarChartAssignees = []
    barChartsAssignees = {'assignees':[assigneesIssues, assigneesPoints ]}
    for key, value in barChartsAssignees.items():
        barA = sorted(value[0].items(), key=operator.itemgetter(0))
        barB = sorted(value[1].items(), key=operator.itemgetter(0))
        print(barA)
        print(barB)
        if len(value[0]) > 0 and len(value[1]) > 0:
            i = 0
            j = 0
            while j < len(barA) and i < len(barB) :
                bA = barA[j]
                bB = barB[i]
                if bA[0] == bB[0]:
                    print(str(bA[0]) + " " + str(bB[0]))
                    dataBarChartAssignees.append({ 'y': bA[0],
                                               'a': bA[1], 'b': bB[1] })
                    i = i + 1
                    j = j + 1
                elif len(barA) > len(barB):
                    j = j + 1
                elif len(barA) < len(barB):
                    i = i + 1
                else:
                    print("Bar chart parity error")
                
    dataBarChartStatus = []
    barChartsStatus = {'status':[statusIssues, statusPoints]}
    for key, value in barChartsStatus.items():
        barA = sorted(value[0].items(), key=operator.itemgetter(0))
        barB = sorted(value[1].items(), key=operator.itemgetter(0))
        print(barA)
        print(barB)
        if len(value[0]) > 0 and len(value[1]) > 0:
            i = 0
            j = 0
            while j < len(barA) and i < len(barB) :
                bA = barA[j]
                bB = barB[i]
                if bA[0] == bB[0]:
                    print(str(bA[0]) + " " + str(bB[0]))
                    dataBarChartStatus.append({ 'y': bA[0],
                                               'a': bA[1], 'b': bB[1] })
                    i = i + 1
                    j = j + 1
                elif len(barA) > len(barB):
                    dataBarChartStatus.append({ 'y': bA[0],
                                               'a': bA[1], 'b': 0 })
                    j = j + 1
                elif len(barA) < len(barB):
                    dataBarChartStatus.append({ 'y': bA[0],
                                               'a': 0, 'b': bB[1] })
                    i = i + 1
                else:
                    print("Bar chart parity error")

    donutSprintsPointsChart = []
    for dSPC in sorted(sprintsPoints.items(), key=operator.itemgetter(0)):
        donutSprintsPointsChart.append({'label':dSPC[0],'value':dSPC[1]})

    donutSprintsIssuesChart = []
    for dSIC in sorted(sprintsIssues.items(), key=operator.itemgetter(0)):
        donutSprintsIssuesChart.append({'label':dSIC[0],'value':dSIC[1]})

    data = eventChart()

    repoLabels = repoLabels
    
    print("\n")
    print("To render:")
    print(repoLabels)

    return render_template('dashboard.html', user=session['username'],
                           render=True, orgs=orgs,
                           issuesIndicators=issuesIndicators,
                           org=org, repo=repo, a=a, b=b,
                           charts=charts,
                           devs=devs,taskId=taskId,taskPoints=taskPoints,
                           created_at=created_at,working=working,done=done,
                           dataBarChartAssignees=dataBarChartAssignees,
                           dataBarChartStatus=dataBarChartStatus,
                           labelsBarA=labelsBarA,labelsBarB=labelsBarB,
                           donutSprintsPointsChart=donutSprintsPointsChart,
                           donutSprintsIssuesChart=donutSprintsIssuesChart,
                           areaQADone=data,
                           statusIssuesDevs=statusIssuesDevs,
                           statusPointsDevs=statusPointsDevs,
                           repoLabels=repoLabels)




######################################################## TIMESHEET CRUD ###########################################################
#                            LIST
#################################################################


def load_all_items_from_database(repository):
    print("Loading all items from database:")
    timesheets = repository.read()
    at_least_one_item = False
    for p in timesheets:
        at_least_one_item = True
        tmp_timesheet = Timesheet.build_from_json(p)
        print("ID = {} | User = {} | Date = {}".
              format(tmp_timesheet._id,tmp_timesheet.user, tmp_timesheet.date))
    if not at_least_one_item:
        print("No items in the database")

#################################################################
#                           CREATE
#################################################################

def test_create(repository, new_timesheet):
    print("\n\nSaving new_timesheet to database")
    repository.create(new_timesheet)
    print("new_timesheet saved to database")
    print("Loading new_timesheet from database")
    db_timesheets = repository.read(timesheet_id=new_timesheet._id)
    for p in db_timesheets:
        timesheet_from_db = Timesheet.build_from_json(p)
        print("new_timesheet = {}".format(timesheet_from_db.get_as_json()))

#################################################################
#                           UPDATE
#################################################################

def test_update(repository, new_timesheet):
    print("\n\nUpdating new_timesheet in database")
    repository.update(new_timesheet)
    print("new_timesheet updated in database")
    print("Reloading new_timesheet from database")
    db_timesheets = repository.read(timesheet_id=new_timesheet._id)
    for p in db_timesheets:
        timesheet_from_db = Timesheet.build_from_json(p)
        print("new_timesheet = {}".format(timesheet_from_db.get_as_json()))

#################################################################
#                           DELETE
#################################################################

def test_delete(repository, timesheet):
    print("\n\nDeleting timesheet to database")
    repository.delete(timesheet)
    print("timesheets deleted from database")
    print("Trying to reload timesheets from database")
    db_timesheets = repository.read(timesheet_id=timesheet._id)
    found = False
    for p in db_timesheets:
        found = True
        timesheet_from_db = Timesheet.build_from_json(p)
        print("timesheet = {}".format(timesheet_from_db.get_as_json()))

    if not found:
        print("Item with id = {} was not found in the database".format(timesheet._id))

#################################################################
#                            LIST
#################################################################


def load_all_items_by_user(repository, user):
    timesheetsViewModel = []
    print("Loading all items from database with user key:")
    timesheets = repository.getByUser(user)
    at_least_one_item = False
    for p in timesheets:
        at_least_one_item = True
        tmp_timesheet = Timesheet.build_from_json(p)
        timesheetsViewModel.append({'date':tmp_timesheet.date,
                                    'project':tmp_timesheet.project,
                                    'begin':tmp_timesheet.begin,
                                    'end':tmp_timesheet.end,
                                    'activity':tmp_timesheet.activity,
                                    'issue':tmp_timesheet.issue,
                                    'comment':tmp_timesheet.comment})
        
        print("ID = {} | User = {} | Date = {}".format(tmp_timesheet._id,
                                                       tmp_timesheet.user,
                                                       tmp_timesheet.date))
    if not at_least_one_item:
        print("No items in the database")
    return timesheetsViewModel



###################################################################################################################
#                       PROJET WEB PLAT AUTH
#################################################################

def auth():
    if 'username' in session:
        print("User in session")
        return True
    else:
        return False

#################################################################
#                           PROJET WEB
#################################################################

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    uploadImage = False
    plotChartsLocally = True
    
    global gRepo
    org = ""
    repo = ""
    issueId = ""
    if auth():
        if request.method == 'POST':
            print("Nova pesquisa")
            org = request.form['org']
            repo = request.form['repo']
            plotChartsLocally = 'locally' in request.form
            
            #issueId = request.form['issueId']
            #if len(issueId) <= 0:
            print(org)
            print(repo)
            #print(len(issueId))
            try:
                g = Github(session['username'], session['password'])
                gOrg = g.get_organization(org)
                print("Existe Org ")
                gRepo = gOrg.get_repo(repo)
                print("Existe Repositório")
                try:
                    print("\n")
                    startMetrics()
                    printLog()
                    if plotChartsLocally:
                        print("Metrics-->Charts")
                        ChartFileHelper.generateCharts(totalPoints, totalIssues,
                                                       totalPullRequest, sprintsIssues,
                                                       assigneesIssues, statusIssues,
                                                       sprintsIssuesDevs,statusIssuesDevs,
                                                       sprintsPoints, assigneesPoints,
                                                       statusPoints, sprintsPointsDevs,
                                                       statusPointsDevs,
                                                       events, graphsURLs,
                                                       eventGraphsURLs, uploadImage)
                    print("Metrics-->Render")
                except:
                    print("Ocorreu um erro")
            except:
                print("Erro org ou repo")
                
        return renderDashboard(org, repo)
    else:
        return redirect(url_for('index'))
            
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/timesheet', methods=['GET', 'POST'])
def timesheet():

    if auth():
        timesheetsViewModel = []
        repository = TimesheetsRepository()

        if request.method == 'POST':
    

            print("TimeSheetPost")

            try:
                
                project = request.form['project']
                begin = request.form['begin']
                end = request.form['end']
                activity = request.form['activity']
                issue = request.form['issue']
                comment = request.form['comment']

                #create new_timesheet and read back from database
                new_timesheet = Timesheet.build_from_json({"user":session['username'],
                                                           "date":datetime.now().strftime("%Y-%m-%d"),
                                                           "project":project, 
                                                            "begin":begin,
                                                            "end":end, 
                                                            "activity":activity,
                                                            "issue":issue, 
                                                            "comment":comment})

                test_create(repository, new_timesheet)

            
                #update new_timesheet and read back from database
                new_timesheet.begin = 350
                test_update(repository, new_timesheet)

                #delete new_timesheet and try to read back from database
                #test_delete(repository, new_timesheet)
                
                
                print("Rendered timesheet!")
            except:
                print("Fail!")
                
        #display all items from DB
        load_all_items_from_database(repository)

            
        dateCalendar = datetime.now().strftime("%Y-%m-%d")
        timesheetsViewModel = load_all_items_by_user(repository, session['username'])
        return render_template('timesheet.html',
                               user = session['username'],
                               timesheetsViewModel=timesheetsViewModel,
                               dateCalendar=dateCalendar)
    else:
        return redirect(url_for('index'))
        
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/test', methods=['GET', 'POST'])
def test():
    if auth():
        return render_template('test.html')
    else:
        return redirect(url_for('index'))
        
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/')
def index():
    if auth():
        return redirect(url_for('dashboard'))
    return render_template('unauthorized.html')
        
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/auth', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    
        startTimePostLogin = datetime.now()
        print("TimePostLogin")
        print(startTimePostLogin)
        try:
            login = Github(request.form['username'],request.form['password']).get_user().login
            session['username'] = login
            session['password'] = request.form['password']
            user = {'username':login,'last_login':startTimePostLogin}
            usersColl = PyMongoDB.getUsersColl()
            user_id = usersColl.insert_one(user).inserted_id
            print("Usuário adicionado: " + str(user_id))

        except:
            print("Fail!")
            print(datetime.now() - startTimePostLogin)
            return redirect(url_for('index'))
        
        print(datetime.now() - startTimePostLogin)
        return redirect(url_for('index'))
    return render_template('auth.html')

#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

       
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/logout')
def logout():
    if auth():
        # remove the username from the session if it's there
        session.pop('username', None)
        session.pop('password', None)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()

