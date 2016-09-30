class GitMapper(object):
    """docstring for GitMapper"""
    def __init__(self, arg):
        super(GitMapper, self).__init__()
        self.arg = arg
		
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
