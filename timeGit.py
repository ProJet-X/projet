from github import Github
from pyMongoDB import PyMongoDB
import json

class TimeGit:

    def getTimeGenData(repo=None, userSearch = 'xanderayes'):
        timesheetGit = PyMongoDB.getTimeSheetsGitColl()
        if repo == None:
            print("Pass a git object")
        else :
            try:
                timesheet = []
                print("TimesheetGit")
                alreadyMapped = timesheetGit.find({"username": userSearch}).count() > 1
                if alreadyMapped:
                    print("Dados atualizados")
                    timesheet = timesheetGit.find_one({"username": str(userSearch)})
                    print("Dados: " + str(timesheet))
            except Exception as e:
                print("Ocorreu um erro com o banco de dados!")
                
            try:
                print("Atualizando dados...")
                
                issueList = repo.get_issues()
                for issue in issueList:
                    
                    if issue.title.find(userSearch) != -1:
                        for comment in issue.get_comments():
                            print(comment)
                            if comment.user.login == userSearch:
                                data = comment.body
                                print(str(data))
                                
                                try:
                                    jsonData = json.loads(comment.body)
                                    print(jsonData)
                                    try:
                                        if jsonData != None and len(jsonData) > 0:
                                            issue_id = timesheetGit.insert_one(jsonData).inserted_id
                                            print("Doc adicionado: " + str(issue_id))
                                    except Exception as e:
                                        print(e)
                                        pass
                                except Exception as e:
                                    print(e)
                                    pass
                                print(PyMongoDB.countTimeSheetsGit())
                                
                              

                                
                                if data != None and len(data) > 0:
                                    timesheet.append(data)
                                print(PyMongoDB.countTimeSheetsGit())
                                print("\n")
                return timesheet
                
            except Exception as e:
                 print("Ocorreu um erro com o Git: " + str(e))
        
