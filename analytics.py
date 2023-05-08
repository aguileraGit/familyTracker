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
        self.miscDF = None

        self.pointCollectionList = [fly_kills, board_games_winner, chia_seeds, misc_points]


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


    def getMiscData(self):
        dataToAppend = []
        for obj in misc_points.objects():
            item = {'dow': obj.dow,
                    'winner': obj.winner,
                    'points': obj.points}
            dataToAppend.append(item)

        self.miscDF = pd.DataFrame(dataToAppend)


    def getCombinePointData(self):
        self.getChiaseedData()
        self.getFlyData()
        self.getBoardGameData()
        self.getMiscData()

        self.combinedPointsDF = pd.concat([self.chiaSeedDF,
                                           self.flyDataDF,
                                           self.boardGameDF,
                                           self.miscDF], axis=0)
        
        #Cast points to ints
        self.combinedPointsDF['points'] = pd.to_numeric(self.combinedPointsDF['points'])

        # Reset index
        self.combinedPointsDF = self.combinedPointsDF.reset_index(drop=True)


    def generateLeaderBoard(self):
         leaderBoard = self.combinedPointsDF.groupby('winner')['points'].sum().reset_index()

        #Need to drop index

         leaderBoardHTML = leaderBoard.to_html(classes=["table table-bordered table-striped table-hover"])

         return leaderBoardHTML
    
    def quickPointsTotal(self):
        '''
        Quickly retrieves points for users using mongodb-like syntax.
        This does not rely on pulling down data to DF and parsing.
        Returns dict of names and points.
        I don't actually know how to do this. - GPT wrote this.
        https://www.tutorialspoint.com/mongoengine/mongoengine_querying_database.htm
        '''
        
        # Aggregate the points by user using the "group" method
        pipeline = [
            {"$group": {"_id": "$winner", "total_points": {"$sum": {"$toInt": "$points"}}}}
        ]

        # Execute the aggregation pipeline for the "misc_points" collection
        misc_points_results = misc_points.objects.aggregate(*pipeline)

        # Execute the aggregation pipeline for the "fly_kills" collection
        fly_kills_results = fly_kills.objects.aggregate(*pipeline)

        board_game_results = board_games_winner.objects.aggregate(*pipeline)

        chia_seeds_results = chia_seeds.objects.aggregate(*pipeline)

        # Merge the results of both collections by user
        merged_results = {}

        for result in misc_points_results:
            merged_results[result['_id']] = result['total_points']

        for result in fly_kills_results:
            user = result['_id']
            if user in merged_results:
                merged_results[user] += result['total_points']
            else:
                merged_results[user] = result['total_points']

        for result in board_game_results:
            user = result['_id']
            if user in merged_results:
                merged_results[user] += result['total_points']
            else:
                merged_results[user] = result['total_points']

        for result in chia_seeds_results:
            user = result['_id']
            if user in merged_results:
                merged_results[user] += result['total_points']
            else:
                merged_results[user] = result['total_points']


        # Print the results
        #for user, total_points in merged_results.items():
            #print(f"user: {user}, totalPoints: {total_points}")
        
        #print(merged_results)
        #print(type(merged_results))
        
        return merged_results

    def collectAllData(self):
        data = []

        for collection in self.pointCollectionList:
            for item in collection.objects:
                data.append(item.to_mongo())
        
        df = pd.DataFrame(data)

        print(df)

    def createDivergencePlots(self):

        # Get users in DF - membersDF
        #List of dict. Each dict contains the information to query the Users
        # DB and store the values to plot later one
        divergenceList = []

        #Parents vs Kids
        divergenceList.append({'category': 'Parents vs Kids',
            'qType': 'familyRelationship',
            'pQuery': ['brother', 'sister'],
            'pNames': None,
            'pValue': None,
            'nQuery': ['mother', 'father'],
            'nNames': None,
            'nValue': None},
        )
        
        #Brothers vs Sister
        divergenceList.append({'category': 'Brothers vs Sisters',
            'qType': 'familyRelationship',
            'pQuery': ['brother'],
            'pNames': None,
            'pValue': None,
            'nQuery': ['sister'],
            'nNames': None,
            'nValue': None},
        )

        #Mom vs Dad
        divergenceList.append({'category': 'Mom vs Dad',
            'qType': 'familyRelationship',
            'pQuery': ['mother'],
            'pNames': None,
            'pValue': None,
            'nQuery': ['father'],
            'nNames': None,
            'nValue': None},
        )

        #Query DB and get back 
        for query in divergenceList:
            if query['qType'] == 'familyRelationship':
                #Preform Query
                temp = family_members.objects(familyRelationship__in=query['pQuery'])
                query['pNames'] = temp.values_list('firstName')
                
                temp = family_members.objects(familyRelationship__in=query['nQuery'])
                query['nNames'] = temp.values_list('firstName')

            elif query['qType'] == 'sex':
                temp = family_members.objects(mf__in=query['pQuery'].values_list('firstName'))
                query['pNames'] = temp.values_list('firstName')

                temp = family_members.objects(mf__in=query['nQuery'].values_list('firstName'))
                query['nNames'] = temp.values_list('firstName')

            elif query['qType'] == 'dob':
                pass
            else:
                pass
                #qType could be a query
            
        #Use list of names to query all pointCollections and sum points
        for query in divergenceList:
            query['pValue'] = 0
            for collection in self.pointCollectionList:
                temp = collection.objects(winner__in=query['pNames'])
                for doc in temp:
                    query['pValue'] += int(doc.points)

            query['nValue'] = 0
            for collection in self.pointCollectionList:
                temp = collection.objects(winner__in=query['nNames'])
                for doc in temp:
                    query['nValue'] += int(doc.points)

        print(divergenceList)

        # Calculate the total for each category
        for item in divergenceList:
            item['nValue'] = item['nValue'] * -1
            item['Total'] = item['pValue'] + abs(item['nValue'])

        # Create the figure
        fig = go.Figure()

        # Add the positive bars
        fig.add_trace(go.Bar(
            x=[item['pValue'] for item in divergenceList],
            y=[item['category'] for item in divergenceList],
            name='Positive',
            orientation='h',
            marker=dict(
                color='green'
            )
        ))

        # Add the negative bars
        fig.add_trace(go.Bar(
            x=[item['nValue'] for item in divergenceList],
            y=[item['category'] for item in divergenceList],
            name='Negative',
            orientation='h',
            marker=dict(
                color='red'
            )
        ))

        # Set the layout
        fig.update_layout(
            title='Diverging Stacked Bar Chart',
            barmode='relative',
            bargap=0.1,
            xaxis=dict(
                title='Value',
                #range=[-150, 150],
                #tickvals=[-150, -100, -50, 0, 50, 100, 150],
                #ticktext=['-150', '-100', '-50', '0', '50', '100', '150']
            )
        )

        return fig
