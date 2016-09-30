import time
import json

from imgurpython import ImgurClient

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

import operator
from datetime import datetime

class ChartFileHelper(object):

    """docstring for ChartFileHelper"""
    def __init__(self, arg):
        super(ChartFileHelper, self).__init__()
        self.arg = arg
        
    graphsURLs = []
    eventGraphsURLs = []

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

    def lineChart(x,y,labelX="time",labelY="event",title=None, uploadImage=False):

        print("Line chart")    
        plt.plot(x, y)
        plt.xlabel(labelX)
        plt.ylabel(labelY)
        plt.title(title)
        plt.grid(True)
        print("Line ploted")
        if uploadImage == True:
            plt.savefig('lineCharts\simpleChart.png', bbox_inches='tight')
        else:
            plt.savefig('lineCharts\simpleChart_' + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
        plt.clf()
        print("Line saved")

    #################################################################
    #                        CHARTS
    #################################################################

    def pieChart(pie, uploadImage=False):

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
            plt.savefig("pieCharts\pie.png", bbox_inches='tight')
        else:
            plt.savefig("pieCharts\pie_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
        print("Pie saved")


    #################################################################
    #                        CHARTS    
    #################################################################_____
    #                           |                             |     |_a_b_| with legends! 
    # Could be simple bar graph |__:__:__ or a multiBar per x |__::__::____
    #  http://matplotlib.org/examples/api/barchart_demo.html
    def barChart(barA, barB, legendA="A", legendB="B", yLable='Scores', uploadImage=False):
        
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
                plt.savefig("barCharts\bar_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight')
        except:
            plt.savefig("barTest_" + str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")), bbox_inches='tight' )
        print("Bar saved")


    #################################################################
    #                        CHARTS    
    ################################################################# 
        
    def stackedBarChart(stackedBars, uploadImage=False):    
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

    def generateCharts(totalPoints, totalIssues,
                        totalPullRequest, sprintsIssues,
                        assigneesIssues, statusIssues,
                        sprintsIssuesDevs,statusIssuesDevs,
                        sprintsPoints, assigneesPoints,
                        statusPoints, sprintsPointsDevs,
                        statusPointsDevs,
                        events, graphsURLs,
                        eventGraphsURLs, uploadImage=False):
        
        startTimeAuthImgur = datetime.now()
        print("AuthImgurTime")
        print(startTimeAuthImgur)
        try:
            client = authenticateImgur()
        except:
            print("Imgur auth problem")
        print("Final AuthImgurTime")
        print(datetime.now() - startTimeAuthImgur)
        
        startTimeGraphs = datetime.now()
        print("GraphsTime")
        print(startTimeGraphs)
        #percents = [totalPoints, totalIssues, totalPullRequest]
        
        try:
            pieCharts = [sprintsIssues, sprintsPoints]
            for pie in pieCharts:
                
                pieChart(sorted(pie.items(), key=operator.itemgetter(0)))
                
                if uploadImage == True:
                    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\pieCharts\\foo.png', anon=False)
                    link_img = image['link']
                    print("Pie uploaded")
                    print(link_img)
                    graphsURLs.append(link_img)
                    print("Pie appended")
        except:
            print("Pie chart error!")

        try:    
            barCharts = {'assignees':[assigneesIssues, assigneesPoints ],'status':[statusIssues, statusPoints]}
            for key, value in barCharts.items():      
                print(value[0])
                print(value[1])
                barA = sorted(value[0].items(), key=operator.itemgetter(0))
                barB = sorted(value[1].items(), key=operator.itemgetter(0))
                barChart(barA, barB, "Tarefas", "Pontos")
                if uploadImage == True:
                    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\barCharts\\bar.png', anon=False)
                    link_img = image['link']
                    print("Bar uploaded")
                    print(link_img)
                    graphsURLs.append(link_img)
                    print("Bar appended")
        except:
            print("Bar chart error!")

        
        #stackedBarCharts = [sprintsIssuesDevs, statusIssuesDevs, sprintsPointsDevs, statusPointsDevs]
        #for stackedBar in stackedBarCharts:
        #    link_img = stackedBarChart(bar)
        #    image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\foo1.png', anon=False)
        #    link_img = image['link']
        #    print(link_img)
        #    graphsURLs.append(link_img)

        try: 
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
                            image = client.upload_from_path('C:\\Users\\vinic\\Projects\\projet\\lineCharts\\simpleChart.png', anon=False)
                            print(image)
                            link_img = image['link']
                            print("Line uploaded")
                            print(link_img)
                            eventGraphsURLs.append(link_img)
                            print("Line appended")
                            
                    except:
                        print("Simple chart error")
        except:
            print("Line chart error!")
            
        print("Final graficos")
        print(datetime.now() - startTimeGraphs)
        
