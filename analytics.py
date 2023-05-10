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
        leaderBoardDF['Names'] = leaderBoardDF.index
        leaderBoardDF.sort_values(by=['Points'], inplace=True, ascending=False)
        leaderBoardDF = leaderBoardDF.loc[:, ['Names','Points']]
        
        leaderBoardHTML = leaderBoardDF.to_html(classes=["table table-bordered table-striped table-hover"],
                                                index_names=False, justify='left', index=False)

        return leaderBoardHTML
    
    def getPointsbyUser(self):
        # Create a dictionary to hold the total points for each winner
        winners = {}

        # Query each collection for documents and sum the points for each winner
        for collection in self.pointCollectionList:
            for doc in collection.objects:
                winner = doc.winner
                points = int(doc.points)
                if winner not in winners:
                    winners[winner] = int(points)
                else:
                    winners[winner] += int(points)

        # Print the total points for each winner
        #for winner, points in winners.items():
        #    print(f"{winner}: {points}")

        return winners


    def collectAllData(self):
        data = []

        for collection in self.pointCollectionList:
            for item in collection.objects:
                data.append(item.to_mongo())
        
        df = pd.DataFrame(data)

        print(df)

    def createDivergencePlots(self):

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

        #Boys vs Girls
        divergenceList.append({'category': 'Boys vs Girls',
            'qType': 'sex',
            'pQuery': ['f'],
            'pNames': None,
            'pValue': None,
            'nQuery': ['m'],
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
                temp = family_members.objects(mf__in=query['pQuery'])
                query['pNames'] = temp.values_list('firstName')

                temp = family_members.objects(mf__in=query['nQuery'])
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
            x=[d['pValue'] if d['nValue'] >= 0 else -d['pValue'] for d in divergenceList],
            y=[d['category'] for d in divergenceList],
            orientation='h',
            marker_color='#3faad1'
        ))

        # Add the negative bars
        fig.add_trace(go.Bar(
            x=[d['nValue'] if d['nValue'] >= 0 else 0 for d in divergenceList],
            y=[d['category'] for d in divergenceList],
            orientation='h',
            marker_color='#3faad1'
            ))

        # Set the layout
        fig.update_layout(
            title='Point Comparisons',
            barmode='relative',
            bargap=0.1,
            showlegend=False,
            xaxis=dict(
                tickvals=[d['nValue'] if d['nValue'] < 0 else d['pValue'] for d in divergenceList],
                ticktext=[str(abs(d['nValue'])) if d['nValue'] < 0 else str(d['pValue']) for d in divergenceList]
            )
        )

        return fig
