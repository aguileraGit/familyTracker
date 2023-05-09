import pandas as pd
import plotly.graph_objects as go
import plotly
from formClasses import *

'''
Thought process has changed on this. Originally, the process was to get allll data and
process it using Pandas. It has moved to using mongoengine syntax to query. For the most
part, each function pulls data and generates HTML to display it.

self.pointCollectionList maintains the collections that actually contain points.
'''

class pointsAnalytics:

    def __init__(self):
        self.pointCollectionList = [fly_kills, board_games_winner, chia_seeds, misc_points]


    def generateLeaderBoard(self):
        #leaderBoard = self.combinedPointsDF.groupby('winner')['points'].sum().reset_index()
        
        #Call self.getPointsbyUser() and get a dict of users and points
        pointsByUsers = self.getPointsbyUser()

        #Drop in DF
        leaderBoardDF = pd.DataFrame(pointsByUsers, index=[0]).transpose()

        #Make pretty
        leaderBoardDF.rename( columns={0 :'Points'}, inplace=True )
        leaderBoardDF.index.names = ['Name']
        leaderBoardDF.sort_values(by=['Points'], inplace=True, ascending=False)
        
        leaderBoardHTML = leaderBoardDF.to_html(classes=["table table-bordered table-striped table-hover"])

        return leaderBoardHTML
    
    def getPointsbyUser(self):
        '''
        # Define the list of collections to query
        pointCollectionList = [FlyKill, BoardGame, ChiaSeed, MiscPoints]

        # Create a dictionary to hold the total points for each winner
        winners = {}

        # Query each collection for documents and sum the points for each winner
        for collection in pointCollectionList:
            for doc in collection.objects:
                winner = doc.winner
                points = doc.points
                if winner not in winners:
                    winners[winner] = points
                else:
                    winners[winner] += points

        # Print the total points for each winner
        for winner, points in winners.items():
            print(f"{winner}: {points}")
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
        
        print(merged_results)
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
            orientation='h',
        ))

        # Add the negative bars
        fig.add_trace(go.Bar(
            x=[item['nValue'] for item in divergenceList],
            y=[item['category'] for item in divergenceList],
            orientation='h',
            )
        )

        # Set the layout
        fig.update_layout(
            title='Point Comparisons',
            barmode='relative',
            bargap=0.1,
            showlegend=False,
            xaxis=dict(
                title='Value',
                #range=[-150, 150],
                #tickvals=[-150, -100, -50, 0, 50, 100, 150],
                #ticktext=['-150', '-100', '-50', '0', '50', '100', '150']
            )
        )

        return fig
