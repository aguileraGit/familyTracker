import pandas as pd
import plotly.graph_objects as go
import plotly
from formClasses import *


'''
Maybe use a decorator to refresh data for functions that need it. Only refreshes
 if data is stale (empty or older than 4 hours). Need function to refresh now.

Analytics page needs to be created. Page will not generate plots. It was use jQuery
 to call and render plots. I don't know how to do this.

 See: https://blog.heptanalytics.com/flask-plotly-dashboard/
'''

class pointsAnalytics:

    def __init__(self):
        '''
        To be called app.py runs. Functions in app.py then call Fns in class to avoid
        extra calls to the DB. 
        '''
        self.chiaseedDF = None
        self.flyDataDF = None
        self.boardGameDF = None
        self.combinedPointsDF = None


    def getChiaseedData(self):
        dataToAppend = []
        for obj in chia_seeds.objects():
            item = {'dow': obj.dow,
                    'winner': obj.winner,
                    'points': obj.points}
            dataToAppend.append(item)

        self.chiaSeedDF = pd.DataFrame(dataToAppend)


    def getFlyData(self):
        dataToAppend = []
        for obj in fly_kills.objects():
            item = {'dow': obj.dow,
                    'winner': obj.winner,
                    'points': obj.points}
            dataToAppend.append(item)

        self.flyDataDF = pd.DataFrame(dataToAppend)


    def getBoardGameData(self):
        dataToAppend = []
        for obj in board_games_winner.objects():
            item = {'dow': obj.dow,
                    'winner': obj.winner,
                    'points': obj.points}
            dataToAppend.append(item)

        self.boardGameDF = pd.DataFrame(dataToAppend)


    def getCombinePointData(self):
        self.getChiaseedData()
        self.getFlyData()
        self.getBoardGameData()

        self.combinedPointsDF = pd.concat([self.chiaSeedDF,
                                           self.flyDataDF,
                                           self.boardGameDF], axis=0)
        
        self.combinedPointsDF['points'] = pd.to_numeric(self.combinedPointsDF['points'])

        # Reset index
        self.combinedPointsDF = self.combinedPointsDF.reset_index(drop=True)


    def generateLeaderBoard(self):
         leaderBoard = self.combinedPointsDF.groupby('winner')['points'].sum().reset_index()

        #Need to drop index

         leaderBoardHTML = leaderBoard.to_html(classes=["table table-bordered table-striped table-hover"])

         return leaderBoardHTML
    
    





