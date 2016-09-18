
class ProGet(object):
    """docstring for ProGet"""
    def __init__(self, arg):
        super(ProGet, self).__init__()
        self.arg = arg
        
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
    eventGraphsURLs = []

    # GitHub trace variables
    printEvents = True

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

    ## Events of each issue
    eventActorTime = []
    ## General events
    events = []

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

        global events
        
        MAX_POINTS = 100

        ## Get sprint if the issue is milestones
        
        if i.milestone == None:
            sprint = "Unk Sprint "
        else:
            sprint = i.milestone.title
        print("Sprint da issue #" + str(i.number) + ": " + str(sprint))
        
        ## Get assignee if the issue is assigned
        if i.assignee == None:
            developer = "Unk Dev "
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
        eventActorTime.clear()
        eventActorTime.append({'event':'creation', 'created_at': str(i.created_at)})
        if printEvents == True:
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
        events.append(eventActorTime.copy())
        print("Appending events")
        print(str(len(events)))
        print("\n")

    #################################################################
    #                    GITHUB - MAPPER    
    #################################################################
    def mapIssues(gRepo):

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
                issue = gRepo.get_issue(issueId)
                issueMapper(issue)
        except:
            print("Issue não existe")

        return totalPoints, totalIssues, totalPullRequest, sprintsPoints, assigneesPoints, sprintsPointsDevs, 
        statusPoints, statusPointsDevs, sprintsIssues, assigneesIssues, sprintsIssuesDevs, statusIssues, statusIssuesDevs
            