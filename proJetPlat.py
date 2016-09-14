import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from imgurpython import ImgurClient
from github import Github
from flask import Flask, render_template, session,redirect, url_for, escape, request
app = Flask(__name__)


print("********************************************")
print("Welcome to ProJet analytics dashboard trace")
print("ProJet v0.0.4")
print("********************************************")
print("\n")


################################################################# 
#                        VARIABLES 
#################################################################
gOrg = ""
gRepo = ""

graphsURLs = []

# GitHub trace variables
printEvents = False

totalPoints = 0
totalIssues = 0
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

################################################################# 
#                    GITHUB - MAPPER 
#################################################################           
def issueMapper(i):
    
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
    
    MAX_POINTS = 100
    
    ## Get sprint if the issue is milestones
    sprint = i.milestone
    if sprint == None:
        sprint = "Nenhum sprint associado"
    else:
        sprint = sprint.title
    print("Sprint da issue: " + sprint)
    ## Get assignee if the issue is assigned
    developer = i.assignee
    if developer == None:
        developer = "Nenhum colaborador associado"
    else:
        developer = developer.login
    print("Colaborador envolvido na issue: " + developer)
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
            print("Problema nos pontos da issue #" + str(i.number) +" "+str(i.title))
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
        
    ## Events track
    print("Aberta em: " + str(i.created_at))
    if printEvents == True:
        for e in i.get_events():
            if e.event == "assigned" or e.event == "unassigned":
                actor = e.raw_data.get("assigner").get("login")
            else:
                actor = e.actor.login
            print(str(e.event) + " por " + str(actor) + " em: " + str(e.created_at))
            if e.event == "closed" or e.event == "reopened":
                print(" Fechada em: " + str(i.closed_at))
            elif e.event == "labeled" or e.event == "unlabeled":
                if (e.raw_data.get("label").get("name").rfind("-") != -1):
                    if int(e.raw_data.get("label").get("name").split(" - ")[0]) > 0:
                        print(" Deslocado para o estado: " + str(e.raw_data.get("label").get("name").split(" - ")[1]))
                else:
                    print(" (Des)Associada ao label: " + str(e.raw_data.get("label").get("name")))
            elif e.event == "milestoned" or e.event == "demilestoned":
                print(" (Des)Associada ao sprint: " + str(e.raw_data.get("milestone").get("title")))
            elif e.event == "assigned" or e.event == "unassigned":
                print(" (Des)Associado ao colaborador: " + str(e.raw_data.get("assignee").get("login")))
                print(" Pelo colaborador: " + str(e.raw_data.get("assigner").get("login")))
            elif e.event == "renamed":
                print(" Nome alterado de: " + str(e.raw_data.get("rename").get("from")))
                print(" Para: " + str(e.raw_data.get("rename").get("to")))
    
    print("\n")

#################################################################
#                    GITHUB - MAPPER    
#################################################################
def points(gRepo):

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
    
    try:
        issue = ""
        #issue = input("Issue(opt): ")
        if issue == "":
            ## Lookup for all issues in repo
            lookup = True
            issueCounter = 1
            while lookup == True:
                try:
                    issue = gRepo.get_issue(issueCounter)
                    issueMapper(issue)
                    issueCounter = issueCounter + 1
                except:
                    lookup = False
                
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
        else:
            issue = gRepo.get_issue(int(issue))
            issueMapper(issue)
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

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,'%d' % int(height),ha='center', va='bottom')

#################################################################
#                        CHARTS
#################################################################
def simplePlot(x,y):

    plt.plot(x, y)

    plt.xlabel('time (s)')
    plt.ylabel('voltage (mV)')
    plt.title('About as simple as it gets, folks')
    plt.grid(True)
    plt.savefig("simpleChart.png", bbox_inches='tight')
    plt.clf()

#################################################################
#                        CHARTS
#################################################################

def pieChart(pie):
    print(str(pie))
    labels = pie.keys()
    print(labels)
    total = sum(pie.values())
    fracs = [v / total for v in pie.values()]
    print(fracs)
    
    plt.pie(fracs ,labels=labels, autopct='%1.1f%%', shadow=False, startangle=70)
    plt.axis('equal')
    plt.savefig('foo.png', bbox_inches='tight')
    plt.clf()

#################################################################
#                        CHARTS    
#################################################################_____
#                           |                             |     |_a_b_| with legends! 
# Could be simple bar graph |__:__:__ or a multiBar per x |__::__::____
#http://matplotlib.org/examples/api/barchart_demo.html
def barChart(bars):
    print(str(bars))
    # a bar plot with errorbars
    labelsX = bars.keys()
    print(labelsX)
    means = bars.values()
    print(means)
    N = len(bars.keys())

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(ind, means, width, color='r')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Scores')
    ax.set_title('Scores by group and gender')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(labelsX)
    plt.savefig('bar.png', bbox_inches='tight')
    plt.clf()

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

    global graphsURLs
    
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
        pieChart(pie)
        image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\foo.png', anon=False)
        link_img = image['link']
        print("Uploaded")
        print(link_img)
        graphsURLs.append(link_img)

    barCharts = [assigneesIssues, statusIssues, assigneesPoints, statusPoints]
    for bar in barCharts:
        barChart(bar)
        image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\bar.png', anon=False)
        link_img = image['link']
        print("Uploaded")
        print(link_img)
        graphsURLs.append(link_img)

    
    #stackedBarCharts = [sprintsIssuesDevs, statusIssuesDevs, sprintsPointsDevs, statusPointsDevs]
    #for stackedBar in stackedBarCharts:
    #    link_img = stackedBarChart(bar)
    #    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\foo1.png', anon=False)
    #    link_img = image['link']
    #    print(link_img)
    #    graphsURLs.append(link_img)

    
    print(datetime.now() - startTimeGraphs)
    
#################################################################
#                        PROCESS    
#################################################################

def startMetrics(gRepo):
    global printEvents

    i=0
    print("Colaboradores do repositorio:")
    for x in gRepo.get_collaborators():
        print(x.login)
    print("Alocáveis do repositorio:")
    for x in gRepo.get_assignees():
        print(x.login)
    print("\n")
    #print("Print events?")
    #v = input("(y/Y)(opt)?: ")
    #if v == "y" or v == "Y":
    #    printEvents = True
    #else:
    #    printEvents = False
    startTimeMetrics = datetime.now()
    print("TimeMetrics")
    print(startTimeMetrics)
    points(gRepo)
    print(datetime.now() - startTimeMetrics)
    print("\n")

    
#################################################################
#                        RENDERER
#################################################################

def renderDashboard(org, repo):
    global graphsURLs
    global gRepo
    global gOrg

    global totalPoints
    global totalIssues
    global totalPullRequest
    
    print(org)
    print(repo)
    print("Iniciando dashboard")
    print(gOrg)
    print(gRepo)

    print(graphsURLs)
    a = "Pontos por desenvolvedor"
    b = "Numero de tarefas por sprint"
    try:
        g0=graphsURLs[0]
        g1=graphsURLs[1]
        g2=graphsURLs[2]
        g3=graphsURLs[3]
        g4=graphsURLs[4]
        g5=graphsURLs[5]
        g6=0
        g7=0
        g8=0
        g9=0
    except:
        g0=0
        g1=0
        g2=0
        g3=0
        g4=0
        g5=0
        g6=0
        g7=0
        g8=0
        g9=0
    
    issues=totalIssues
    tasks=totalIssues - totalPullRequest
    pullRequests=totalPullRequest
    points=totalPoints

    print(issues, tasks, pullRequests, points, org, repo, a, b,
          g0, g1, g2, g3, g4, g5, g6, g7, g8, g9)  
    return render_template('dashboard.html', render=True, issues=issues, tasks=tasks,
                           pullRequests=pullRequests, points=points,
                           org=org, repo=repo, a=a, b=b,
                           gA=g0, gB=g1, gC=g2, gD=g3, gE=g4,
                           gF=g5, gG=g6, gH=g7, gI=g8, gJ=g9)

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
#                       PROJET WEB PLAT
#################################################################

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    org = ""
    repo = ""
    if auth():
        if request.method == 'POST':
            print("Nova pesquisa")
            org = request.form['org']
            repo = request.form['repo']
            print(org)
            print(repo)

            #org = "TesteProGest"
            #repo = "progest"
            #org = "indigotech"
            #repo = "br-pro120-geniantis-android"
            try:
                g = Github(session['username'], session['password'])
                gOrg = g.get_organization(org)
                print("Existe Org ")
                gRepo = gOrg.get_repo(repo)
                print("Existe Repositório")
                try:
                    print("\n")
                    startMetrics(gRepo)
                except:
                    print("Ocorreu um erro")
                generateCharts()
            except:
                print("Erro org ou repo")
                
        return renderDashboard(org, repo)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    
        startTimePostLogin = datetime.now()
        print("TimePostLogin")
        print(startTimePostLogin)
        try:
            g = Github(request.form['username'],request.form['password'])
            login = g.get_user().login
            session['username'] = login
            session['password'] = request.form['password']
        
        except:
            print("Fail!")
            print(datetime.now() - startTimePostLogin)
            return redirect(url_for('index'))
        print(datetime.now() - startTimePostLogin)
        return redirect(url_for('index'))
    return render_template('login.html')

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
#app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()

