import matplotlib.pyplot as plt
import numpy as np
import operator
import time
import json
import matplotlib.dates as mdates
from pyMongoDB import PyMongoDB 
from timeEstimator import Estimator
from datetime import datetime
from imgurpython import ImgurClient
from github import Github
from flask import Flask, render_template, session, redirect, url_for, escape, request
app = Flask(__name__)

print("********************************************")
print("Welcome to ProJet analytics dashboard trace")
print("ProJet v0.0.4")
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

# GitHub trace variables
mapEvents = False
uploadImage = False
plotChartsLocally = False

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

################################################################# 
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
        else:
            issue = gRepo.get_issue(issueId)
            issueMapper(issue)
        printLog()
    except:
        print("Issue não existe")
        
#################################################################
#                        CHARTS
#################################################################
        
def authenticateImgur():
    client_id = 'b50f2d93f8d16b0'
    client_secret = 'bfc148a6e9b61923f8b6d5db7db6c6d940a48f29'
    
    client = ImgurClient(client_id, client_secret)
    client.set_user_auth('6f5d0cf446bf216b9617e7a29bf637c212812fcc', '8b4641ffdf4c0cb66984466624f326461cf49600')
    #https://api.imgur.com/oauth2/authorize?client_id=8fbf5c5728003fa&response_type=pin

    #client = ImgurClient(client_id, client_secret)
    
    # Authorization flow, pin example (see docs for other auth types)
    #authorization_url = client.get_auth_url('pin')

    #print("Go to the following URL: {0}".format(authorization_url))

    # Read in the pin, handle Python 2 or 3 here.
    #pin = input("Enter pin code: ")

    # ... redirect user to `authorization_url`, obtain pin (or code or token) ...
    #authorization_url = client.get_auth_url('pin')
    #credentials = client.authorize(pin, 'pin')
    #client.set_user_auth(credentials['access_token'], credentials['refresh_token'])
    #client.set_user_auth('6f5d0cf446bf216b9617e7a29bf637c212812fcc', '8b4641ffdf4c0cb66984466624f326461cf49600')
    

    #print("Authentication successful! Here are the details:")
    #print("   Access token:  {0}".format(credentials['access_token']))
    #print("   Refresh token: {0}".format(credentials['refresh_token']))

    return client


#################################################################
#                        CHARTS
#################################################################

def lineChart(x,y,labelX="time",labelY="event",title=None):
    global uploadImage

    print("Line chart")    
    plt.plot(x, y)
    plt.xlabel(labelX)
    plt.ylabel(labelY)
    plt.title(title)
    plt.grid(True)
    print("Line ploted")
    if uploadImage == True:
        plt.savefig('images\simpleChart.png', bbox_inches='tight')
    else:
        plt.savefig('images\simpleChart_' + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
    plt.clf()
    print("Line saved")

#################################################################
#                        CHARTS
#################################################################

def pieChart(pie):
    global uploadImage

    print("Pie chart")    
    print(str(pie))
    try:
        labels = pie.keys()
    except:
        labels = [k for k, v in pie]

    print(labels)
    try:
        total = sum(pie.values())
        fracs = [v / total for v in pie.values()]
    except:
        total = sum([v for k, v in pie])
        fracs = [v / total for v in [v for k, v in pie]]

    print(fracs)
    plt.clf()
    plt.pie(fracs ,labels=labels, autopct='%1.1f%%', shadow=False, startangle=70)
    plt.axis('equal')
    print("Pie ploted")
    if uploadImage == True:
        plt.savefig("images\pie.png", bbox_inches='tight')
    else:
        plt.savefig("images\pie_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
    print("Pie saved")


#################################################################
#                        CHARTS    
#################################################################_____
#                           |                             |     |_a_b_| with legends! 
# Could be simple bar graph |__:__:__ or a multiBar per x |__::__::____
#  http://matplotlib.org/examples/api/barchart_demo.html
def barChart(barA, barB, legendA="A", legendB="B" ,yLable='Scores'):
    global uploadImage
    
    print("Bar chart")
    print(barA)
    print(barB)
    try:
        labelsX = barA.keys()
        N = len(barA.keys())
    except:
        labelsX = [k for k, v in barA]
        N = len(barA)
        
    print(labelsX)
    try:
        meansA = barA.values()
    except:
        meansA = [v for k, v in barA]
    print(meansA)
    
    
    try:
        meansB = barB.values()
    except:
        meansB = [v for k, v in barB]
    print(meansB)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, meansA, width, color='r')

    rects2 = ax.bar(ind + width, meansB, width, color='y')

    # add some text for labels, title and axes ticks
    ax.set_ylabel(yLable)
    ax.set_title('Scores by group and gender')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(labelsX)
    ax.legend((rects1[0], rects2[0]), (legendA, legendB))

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%d' % int(height),ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    print("Bar ploted")
    try:
        if uploadImage == True:
            plt.savefig("bar.png", bbox_inches='tight')
        else:
            plt.savefig("images\bar_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
    except:
        plt.savefig("barTest_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight' )
    print("Bar saved")


#################################################################
#                        CHARTS    
################################################################# 
    
def stackedBarChart(stackedBars):    
    # a stacked bar plot with errorbars
    labelsX = stackedBars.keys()
    print(labels)
    means = stackedBars.values()
    print(means)
    N = len(stackedBars.keys())
    
    menMeans = (20, 35, 30, 35, 27)
    womenMeans = (25, 32, 34, 20, 25)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35        # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, menMeans, width, color='r', yerr=menStd)
    p2 = plt.bar(ind, womenMeans, width, color='y', bottom=menMeans, yerr=womenStd)

    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    plt.xticks(ind + width/2., labelsX)
    plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Men', 'Women'))

    plt.show()

    
#################################################################    
#                        CHARTS        
#################################################################





#################################################################    
#                        CHARTS        
#################################################################

def generateCharts():
    global totalPoints
    global totalIssues
    global totalPullRequest

    global sprintsIssues
    global assigneesIssues
    global statusIssues
    global sprintsIssuesDevs
    global statusIssuesDevs
    
    global sprintsPoints
    global assigneesPoints
    global statusPoints
    global sprintsPointsDevs
    global statusPointsDevs

    global events
    
    global graphsURLs
    global eventGraphsURLs
    global uploadImage
    
    try:
        client = authenticateImgur()
    except:
        print("Imgur auth problem")
    startTimeGraphs = datetime.now()
    print("TimeGraphs")
    print(startTimeGraphs)
    #percents = [totalPoints, totalIssues, totalPullRequest]


    pieCharts = [sprintsIssues, sprintsPoints]
    for pie in pieCharts:
        pieChart(sorted(pie.items(), key=operator.itemgetter(0)))
        if uploadImage == True:
            image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\images\\foo.png', anon=False)
            link_img = image['link']
            print("Pie uploaded")
            print(link_img)
            graphsURLs.append(link_img)
            print("Pie appended")

    barCharts = {'assignees':[assigneesIssues, assigneesPoints ],'status':[statusIssues, statusPoints]}
    for key, value in barCharts.items():      
        print(value[0])
        print(value[1])
        barA = sorted(value[0].items(), key=operator.itemgetter(0))
        barB = sorted(value[1].items(), key=operator.itemgetter(0))
        barChart(barA, barB, "Tarefas", "Pontos")
        if uploadImage == True:
            image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\images\\bar.png', anon=False)
            link_img = image['link']
            print("Bar uploaded")
            print(link_img)
            graphsURLs.append(link_img)
            print("Bar appended")

    
    #stackedBarCharts = [sprintsIssuesDevs, statusIssuesDevs, sprintsPointsDevs, statusPointsDevs]
    #for stackedBar in stackedBarCharts:
    #    link_img = stackedBarChart(bar)
    #    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\foo1.png', anon=False)
    #    link_img = image['link']
    #    print(link_img)
    #    graphsURLs.append(link_img)
    time = []
    eventStatus = []
    eventTag = []
    print("events " + str(len(events)))
    for issueEvent in events:
        for eventID, eventData in issueEvent:
            for eD in eventData:
                print(eventID)
                print(eventData)
                if eventData['event'] == "labeled" or eventData['event'] == "unlabeled":
                    print(eventData['event'])
                    try:
                        print("Over here")      
                        if (eventData['detail']['status'].rfind("-") != -1):
                            print("Status :" + str(status))
                            if int(eventData['detail']['status'].split(" - ")[0]) >= 0:
                                
                                eventStatus.append(int(status.split(" - ")[0]))
                                
                        else:
                            eventStatus.append(status)

                        date_string = str(eventData['created_at'])
                        print("Date " + str(date_string))
                        try:
                            int_time = int(time.mktime(datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").timetuple()))
                            print("int_time: " + str(int_time))
                            time.append(str(int_time))
                        except:
                            time.append(str(date_string))
                        print("here")
                            
                    except:
                        print("Error map events to charts")
                        #eventTag.append(eventData)
                        #time.append(str(eventData['created_at']))
                        
                else:
                    print("!!!!!!")
                    
                print("Time:")
                print(str(len(time)))
                print("EventStatus")
                print(str(len(eventStatus)))
                print("EventTag")
                print(str(len(eventTag)))
                print("EventGraphsURLs")
                print(str(len(eventGraphsURLs)))
            try:
                if len(time) > 0 and len(eventStatus) > 0:
                    print(time[0])
                    print(len(eventStatus))
                    lineChart(time, eventStatus)
                    print("Ploted")
                if uploadImage == True:
                    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\images\\simpleChart.png', anon=False)
                    print(image)
                    link_img = image['link']
                    print("Line uploaded")
                    print(link_img)
                    eventGraphsURLs.append(link_img)
                    print("Line appended")
                    
            except:
                print("Simple chart error")

                
    print("Final graficos")
    print(datetime.now() - startTimeGraphs)
    
#################################################################
#                        PROCESS    
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
    
    i=0
    print("Colaboradores do repositorio:")
    for x in gRepo.get_collaborators():
        print(x.login)
    print("Alocáveis do repositorio:")
    for x in gRepo.get_assignees():
        print(x.login)
    print("\n")
               
    startTimeMetrics = datetime.now()
    print("TimeMetrics")
    print(startTimeMetrics)
    print("\n")
    issuesColl = PyMongoDB.getIssuesColl()
    if issuesColl.find({"repo_name": str(gRepo.name)}).count() == 1:
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

        statusPointsDevs = issuesData.get('status_points_devs')
        statusIssuesDevs = issuesData.get('status_issues_devs')

        events = issuesData.get('events')
        print("Last updated: " + str(issuesData.get('last_update')))
        
    else:
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
                     'last_update':str(startTimeMetrics)}
            print(issueMapped.keys())
            issue_id = issuesColl.insert_one(issueMapped).inserted_id
            print("Colleção adicionada: " + str(issue_id))
            # http://stackoverflow.com/questions/15415709/update-json-file
            # http://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
            # https://docs.python.org/2/tutorial/inputoutput.html
            #with open('issueMappedDumpJSON.txt', 'w') as outfile:
            #    json.dump(issueMapped, outfile)
        except:
            print("Erro ao adicionar os dados ao banco de dados")
    print(datetime.now() - startTimeMetrics)
    print("\n")

    
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
    
    print(org)
    print(repo)
    print("Iniciando dashboard")
    print(gOrg)
    print(gRepo)

    print(graphsURLs)
    a = "Comparação por colaborador"
    b = "Comparação por sprint"
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

    data = [
    { 'y': '2006', 'a': 100, 'b': 90 },
    { 'y': '2007', 'a': 100,  'b': 65 },
    { 'y': '2008', 'a': 75,  'b': 40 },
    { 'y': '2009', 'a': 75,  'b': 65 },
    { 'y': '2010', 'a': 75,  'b': 40 },
    { 'y': '2011', 'a': 75,  'b': 65 },
    { 'y': '2012', 'a': 300, 'b': 90 }
  ]
    xkey = 'y'
    ykeys = ['a', 'b'],
    orgs = ["AAa","BBb","cCC","dDD"]
    labels = ['Series AAA', 'Series BBB']

    donutSprintsPointsChart = []
    for dSPC in sorted(sprintsPoints.items(), key=operator.itemgetter(0)):
        donutSprintsPointsChart.append({'label':dSPC[0],'value':dSPC[1]})

    print("\n")
    print("To render:")
    print(orgs, issuesIndicators, org, repo, a, b,charts, donutSprintsPointsChart)
    return render_template('dashboard.html', render=True, orgs=orgs,
                           issuesIndicators=issuesIndicators,
                           org=org, repo=repo, a=a, b=b,
                           charts=charts,
                           devs=devs,taskId=taskId,taskPoints=taskPoints,
                           created_at=created_at,working=working,done=done,
                           data=data,xkey=xkey,ykeys=ykeys,labels=labels,
                           donutSprintsPointsChart=donutSprintsPointsChart)

#################################################################
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

    global gRepo
    PyMongoDB.connectMongo()
    org = ""
    repo = ""
    issueId = ""
    if auth():
        if request.method == 'POST':
            print("Nova pesquisa")
            org = request.form['org']
            repo = request.form['repo']
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
                        generateCharts()
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

@app.route('/timesheet')
def timesheet():
    return render_template('timesheet.html')
        
            
#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

@app.route('/test')
def test():
    return render_template('404.html')
        


        
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

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))

#################################################################
#                      FLASK - WEB PLATFORM
#################################################################

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()

