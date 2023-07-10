#https://www.mongodb.com/compatibility/mongoengine-pymongo
#https://www.tutorialspoint.com/mongoengine/mongoengine_quick_guide.htm

from flask import Flask, render_template, request, redirect, flash, jsonify
from mongoengine import connect
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly
import datetime

from formClasses import *
from analytics import *

app = Flask(__name__)
app.config.from_pyfile('config.py')

#Connect to MongoDB Atlas cluster
DBHOST = app.config['DBHOST']
DBNAME = app.config['DBNAME']
hostString = DBHOST + DBNAME
connect(host=hostString)

analytics = pointsAnalytics()

# Define a route to render the user form
@app.route('/', methods=['GET', 'POST'])
def index():
    #Create leader board table
    leaderboardTable = analytics.generateLeaderBoard()

    #Generate divergence plots
    fig = analytics.createDivergencePlots()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', leaderboardTable=leaderboardTable, graphJSON=graphJSON)

#Define route to fly page
@app.route('/flies', methods=['GET', 'POST'])
def flies():
    print('Fn flies')
    form = fly_kills_form(request.form)
    if request.method == 'POST' and form.validate():
        print('Request and validated')
        print(form.dow.data.isoformat())
        fKills = fly_kills(winner = form.winner.data,
                           dow = form.dow.data.isoformat(),
                           points = form.points.data)
        fKills.save()

        flash('New Winner Added!', 'success')
        return redirect('/')

    return render_template('flies.html', form=form)


@app.route('/boardgame', methods=['GET', 'POST'])
def boardgames():
    print('Fn boardgame')
    newWinnerGameForm = board_games_winner_form(request.form)

    if request.method == 'POST' and newWinnerGameForm.validate():
        print('Add new board game winner')
        newWinner = board_games_winner(dow = newWinnerGameForm.dow.data.isoformat(),
                                       winner = newWinnerGameForm.winner.data,
                                       points = newWinnerGameForm.points.data,
                                       game = newWinnerGameForm.game.data)
        newWinner.save()
        flash('New Winner Added!', 'success')
        return redirect('/')
    
    return render_template('boardgames.html',
                           board_games_winner_form = newWinnerGameForm)


#Chia Seeds
@app.route('/chiaseeds', methods=['GET', 'POST'])
def chiaseeds():
    print('Fn chiaseeds')
    chiaSeedsForm = chia_seeds_form(request.form)

    if request.method == 'POST' and chiaSeedsForm.validate():
        print('Chia seed found')
        chiaWinner = chia_seeds(dow = chiaSeedsForm.dow.data.isoformat(),
                                winner = chiaSeedsForm.winner.data,
                                points = chiaSeedsForm.points.data)
        chiaWinner.save()
        flash('New Winner Added!', 'success')
        return redirect('/')
    
    return render_template('chiaseeds.html', form = chiaSeedsForm)


#Push ups
@app.route('/addPushups', methods=['GET', 'POST'])
def addPushups():
    print('Fn addPushups')

    form = push_ups_form(request.form)

    if request.method == 'POST' and form.validate():
        push_ups_done_correctly = push_ups(dateAdded = form.dateAdded.data.isoformat(),
                                           count = form.count.data,
                                           winner = form.winner.data)
        push_ups_done_correctly.save()
        flash('Push ups Added', 'success')
        return redirect('/')

    return render_template('addPushUps.html', form=form)

#Load Push up data to display on website
@app.route('/load_data', methods=['POST'])
def load_data():
    print('load_data')
    start_date = request.json['start_date']
    end_date = request.json['end_date']
    dBs = request.json['dBs']

    response = []

    if 'pushups' in dBs:
        data = push_ups.objects(dateAdded__gte=start_date, dateAdded__lte=end_date).order_by('-dateAdded')

        for entry in data:
            response.append({
                'dateAdded': entry.dateAdded,
                'count': entry.count,
                'winner': entry.winner,
                'type': 'Push ups'
            })

    if 'flies' in dBs:
        data = fly_kills.objects(dow__gte=start_date, dow__lte=end_date).order_by('-dow')

        for entry in data:
            response.append({
                'dateAdded': entry.dow,
                'winner': entry.winner,
                'type': 'Flies',
                'points': entry.points
            })
            

    if 'games' in dBs:
        data = board_games_winner.objects(dow__gte=start_date, dow__lte=end_date).order_by('-dow')

        for entry in data:
            response.append({
                'dateAdded': entry.dow,
                'winner': entry.winner,
                'type': 'Games',
                'points': entry.points
            })

    if 'chiaseeds' in dBs:
        data = chia_seeds.objects(dow__gte=start_date, dow__lte=end_date).order_by('-dow')

        for entry in data:
            response.append({
                'dateAdded': entry.dow,
                'winner': entry.winner,
                'type': 'Chiaseeds',
                'points': entry.points
            })

    if 'misc' in dBs:
        data = misc_points.objects(dow__gte=start_date, dow__lte=end_date).order_by('-dow')

        for entry in data:
            response.append({
                'dateAdded': entry.dow,
                'winner': entry.winner,
                'type': 'Miscellaneous',
                'points': entry.points
            })

    sorted_response = sorted(response, key=lambda x: x['dateAdded'], reverse=True)

    #print(response)

    #Need to figure out how to order 
    return jsonify(sorted_response)

#Misc
@app.route('/misc', methods=['GET', 'POST'])
def misc():
    print('Fn misc')
    form = misc_points_form(request.form)

    if request.method == 'POST' and form.validate():
        miscWinner = misc_points(dow = form.dow.data.isoformat(),
                               winner = form.winner.data,
                               points = form.points.data,
                               reason = form.reason.data)
        miscWinner.save()
        flash('New Winner Added!', 'success')
        return redirect('/')
    
    return render_template('misc.html', form=form)


#Users Page
@app.route('/viewAllFamilyMembers', methods=['GET', 'POST'])
def viewAllFamilyMembers():

    userList = []
    for user in family_members.objects:
        userList.append(user)

    return render_template('viewAllFamilyMembers.html', users=userList)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    '''
    Add board game. Add family member.
    '''
    newGameForm = board_game_add_form(request.form)
    form = family_member_form(request.form)
    if request.method == 'POST' and newGameForm.validate():
        print('Add new board game')
        newBoardGame = board_games(game = newGameForm.game.data,
                                   dateAdded = newGameForm.dateAdded.data.isoformat())
        newBoardGame.save()

        flash('New Board Game Added', 'success')
        return redirect('/')

    
    if request.method == 'POST' and form.validate():
        print('Request and validated')
        user = family_members(firstName = form.firstName.data,
                             middleName = form.middleName.data,
                             lastName = form.lastName.data,
                             nickName = form.nickName.data,
                             email = form.email.data,
                             dob = form.dob.data.isoformat(),
                             mf = form.mf.data,
                             admin = form.admin.data,
                             pictureFilename = form.pictureFilename.data,
                             familyRelationship = form.familyRelationship.data)
        user.save()
        flash('User created successfully!', 'success')
        return redirect('/')

    return(render_template('settings.html', board_game_add_form = newGameForm,
                           form=form))

#Edit User (Must provide ?id=...)
@app.route('/editFamilyMember', methods=['GET', 'POST'])
def editFamilyMember():

    if request.method == 'GET':
        userID = request.args.get('id')

        #Verify ID to edit was provided
        if userID == None:
            flash('No user ID provided', 'danger')
            return redirect('/')
    
        #Get user data from DB by ID
        userInfoFromDB = family_members.objects.get(id=userID)

        #Create form to push to HTML
        form = family_member_form()

        #Set HTML form to have defaults from the DB
        form.firstName.default = userInfoFromDB.firstName
        form.middleName.default = userInfoFromDB.middleName
        form.lastName.default = userInfoFromDB.lastName
        form.nickName.default = userInfoFromDB.nickName
        form.email.default = userInfoFromDB.email
        form.dob.default = datetime.datetime.strptime(userInfoFromDB.dob , '%Y-%m-%d')
        form.admin.default = userInfoFromDB.admin
        form.mf.default = userInfoFromDB.mf
        form.pictureFilename.default = userInfoFromDB.pictureFilename
        form.familyRelationship.default = userInfoFromDB.familyRelationship

        #Update form so defaults take affect
        form.process()
    
        return render_template('editFamilyMember.html', form=form)

    #On request: process form. See addFamilyMember
    if request.method == 'POST':
        form = family_member_form(request.form)

        if form.validate():
            userID = request.args.get('id')
            family_members.objects(id=userID).update(firstName = form.firstName.data,
                                                    middleName=form.middleName.data,
                                                    lastName=form.lastName.data,
                                                    nickName=form.nickName.data,
                                                    email=form.email.data,
                                                    dob=form.dob.data.isoformat(),
                                                    admin=form.admin.data,
                                                    mf=form.mf.data,
                                                    pictureFilename=form.pictureFilename.data,
                                                    familyRelationship=form.familyRelationship.data)

            flash('User updated', 'success')
            return redirect('viewAllFamilyMembers')

        else:
            flash('Error validating from', 'danger')
            return redirect('viewAllFamilyMembers')
        

@app.route('/coffee', methods=['GET', 'POST'])
def coffee(): 
    #Create and pass dictonary to hold and pass all figure
    figsDivs = {}

    #Create div, format JSON, and add to figDivs
    brewTemp = analytics.grindGauge(min=202, max=204, value=204, title='Temperature')
    brewTemp = json.dumps(brewTemp['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['brewTemp'] = brewTemp

    ratio = analytics.grindGauge(min=0, max=32, value=16, title='Ratio', mode='number')
    ratio = json.dumps(ratio['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['ratio'] = ratio

    #Chemex Grind
    grindChemexFig = analytics.grindGauge(min=20, max=22, value=20)
    #Unsure why. Must get only the figure data and encode as JSON
    grindChemexFig = json.dumps(grindChemexFig['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['grindChemexFig'] = grindChemexFig

    #Pour Over Grind
    pourOverGrind = analytics.grindGauge(min=12, max=16, value=18)
    pourOverGrind = json.dumps(pourOverGrind['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['pourOverGrind'] = pourOverGrind

    #V60
    v60Grind = analytics.grindGauge(min=8, max=12, value=10)
    v60Grind = json.dumps(v60Grind['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['v60Grind'] = v60Grind

    #Moka Pot
    mokaPotGrind = analytics.grindGauge(min=5, max=7, value=6)
    mokaPotGrind = json.dumps(mokaPotGrind['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['mokaPotGrind'] = mokaPotGrind

    #Cold Brew Grind
    coldBrewGrind = analytics.grindGauge(min=22, max=26, value=24)
    coldBrewGrind = json.dumps(coldBrewGrind['data'], cls=plotly.utils.PlotlyJSONEncoder)
    figsDivs['coldBrewGrind'] = coldBrewGrind

    return render_template('coffee.html', figsDivs = figsDivs)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    #Get list of first names
    names = family_members.objects().distinct('firstName')
    
    #Default for initial page
    selectedName = names[0]

    figDivs = {}

    pieData = analytics.getPieData( selectedName )
    pieFig = analytics.createPiePlot(list(pieData.keys()), list(pieData.values()))
    pieFig = json.dumps(pieFig, cls=plotly.utils.PlotlyJSONEncoder)
    figDivs['pieData'] = pieFig

    #Sunburt plot does not display. Unsure why.
    #fig = analytics.generate_sunburst_chart(selectedName)
    #figDivs['sunBurst'] = json.dumps(fig['data'], cls=plotly.utils.PlotlyJSONEncoder)
    #figDivs['sunBurst'] = fig

    if request.method == 'POST':
        selectedName = request.form['name']

        pieData = analytics.getPieData(selectedName)
        pieFig = analytics.createPiePlot(list(pieData.keys()), list(pieData.values()))
        pieFig = json.dumps(pieFig, cls=plotly.utils.PlotlyJSONEncoder)
        figDivs['pieData'] = pieFig

        #fig = analytics.generate_sunburst_chart(selectedName)
        #figDivs['sunBurst'] = json.dumps(fig['data'], cls=plotly.utils.PlotlyJSONEncoder)
        #figDivs['sunBurst'] = fig

        return render_template('summary.html', names=names, figDivs = figDivs, selectedName = selectedName)
    
    return render_template('summary.html', names=names, figDivs = figDivs, selectedName = selectedName)


@app.context_processor
def pointsFlysToHTML():
    '''
    Pulled from formClasses.py
    Provides a access to how points are gained via HTML
    '''
    return dict(pointsFlys=pointsFlys)

@app.context_processor
def pointsGamesToHTML():
    '''
    Pulled from formClasses.py
    Provides a access to how points are gained via HTML
    '''
    return dict(pointsGames=pointsGames)

@app.context_processor
def pointsChiaSeedsToHTML():
    '''
    Pulled from formClasses.py
    Provides a access to how points are gained via HTML
    '''
    return dict(pointsChiaSeeds=pointsChiaSeeds)

@app.context_processor
def pointTotalsToHTML():
    return dict(results = analytics.getPointsbyUser())


if __name__ == '__main__':
    app.run(debug=True, port=5001)
