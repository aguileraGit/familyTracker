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
        
        leaderBoardHTML = leaderBoardDF.to_html(classes=["table table-bordered table-striped table-hover bg-white"],
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

        #Category must always be in the format A vs B. The plot traces
        # are pulled from this later on. The order in the plot follows
        # A=negative and B=positive.

        #Parents vs Kids
        divergenceList.append({'category': 'Kids vs Parents',
            'qType': 'familyRelationship',
            'nQuery': ['brother', 'sister'],
            'nNames': None,
            'nValue': None,
            'pQuery': ['mother', 'father'],
            'pNames': None,
            'pValue': None},
        )
        
        #Brothers vs Sister
        divergenceList.append({'category': 'Brothers vs Sisters',
            'qType': 'familyRelationship',
            'nQuery': ['brother'],
            'nNames': None,
            'nValue': None,
            'pQuery': ['sister'],
            'pNames': None,
            'pValue': None},
        )

        #Mom vs Dad
        divergenceList.append({'category': 'Mom vs Dad',
            'qType': 'familyRelationship',
            'nQuery': ['mother'],
            'nNames': None,
            'nValue': None,
            'pQuery': ['father'],
            'pNames': None,
            'pValue': None},
        )

        #Boys vs Girls
        divergenceList.append({'category': 'Girls vs Boys',
            'qType': 'sex',
            'nQuery': ['f'],
            'nNames': None,
            'nValue': None,
            'pQuery': ['m'],
            'pNames': None,
            'pValue': None},
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
            x=[item['pValue'] for item in divergenceList],
            y=[item['category'] for item in divergenceList],
            orientation='h',
            #name = [item['category'].split(' ')[0] for item in divergenceList]
        ))

        # Add the negative bars
        fig.add_trace(go.Bar(
            x=[item['nValue'] for item in divergenceList],
            y=[item['category'] for item in divergenceList],
            orientation='h',
            #name = [item['category'].split(' ')[2] for item in divergenceList]
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


    #This creates all the gauge/indicator plots on the coffee page. 
    def grindGauge(self, min=0, max=100, value=50, title='Grind Size', mode='gauge+number'):
        #https://plotly.com/python/gauge-charts/
        fig = go.Figure()
        
        fig.add_indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = value,
            mode = mode,
            title = {'text': title},
            
            gauge = {'axis': {'range': [min, max]},
                    'steps' : [
                        {'range': [min, value], 'color': "lightgray"},
                        {'range': [value, max], 'color': "lightgray"}
                        ],

                    'threshold': {
                        'line': { 'color': "black", 'width': 4 },
                        'thickness': 0.75,
                        'value': value}
                    }
        )
        
        return fig
    
    #Looks through all DBs with points and returns a dict of DB and total points per person.
    def getPieData(self, winner):
        results = {}
        points = 0
        for collection in self.pointCollectionList:
            for doc in collection.objects(winner=winner):
                points = int(doc.points) + points
                results[collection._get_collection_name()] = points

        return results


    def createPiePlot(self, labelList, valueList):
        labels = labelList
        values = valueList

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        
        return fig
    
    