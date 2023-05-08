#https://www.mongodb.com/compatibility/mongoengine-pymongo
#https://www.tutorialspoint.com/mongoengine/mongoengine_quick_guide.htm

from flask import Flask, render_template, request, redirect, flash
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
    #Needs to be removed
    analytics.getCombinePointData()

    #Needs to be updated to remove Pandas
    leaderboardTable = analytics.generateLeaderBoard()

    #Generate divergence plots
    fig = analytics.createDivergencePlots()
    print(fig)
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

        flash('User created successfully!', 'success')
        return redirect('/')

    return render_template('flies.html', form=form)


@app.route('/boardgame', methods=['GET', 'POST'])
def boardgames():
    print('Fn boardgame')
    newGameForm =  board_game_add_form(request.form)
    newWinnerGameForm = board_games_winner_form(request.form)

    if request.method == 'POST' and newGameForm.validate():
        print('Add new board game')
        newBoardGame = board_games(game = newGameForm.game.data,
                                   dateAdded = newGameForm.dateAdded.data.isoformat())
        newBoardGame.save()

        flash('New Board Game Added', 'success')
        return redirect('/')
    
    if request.method == 'POST' and newWinnerGameForm.validate():
        print('Add new board game winner')
        newWinner = board_games_winner(dow = newWinnerGameForm.dow.data.isoformat(),
                                       winner = newWinnerGameForm.winner.data,
                                       points = newWinnerGameForm.points.data)
        newWinner.save()
        flash('New Winner Added!', 'success')
        return redirect('/')

    return render_template('boardgames.html',
                           board_game_add_form = newGameForm,
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


@app.route('/addFamilyMember', methods=['GET', 'POST'])
def addFamilyMember():
    print('Fn addFamilyMember')
    form = family_member_form(request.form)
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

        # Redirect back to the index page
        flash('User created successfully!', 'success')
        return redirect('/')
    return render_template('addFamilyMember.html', form=form)


#Users Page
@app.route('/viewAllFamilyMembers', methods=['GET', 'POST'])
def viewAllFamilyMembers():

    userList = []
    for user in family_members.objects:
        userList.append(user)

    return render_template('viewAllFamilyMembers.html', users=userList)


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
        print('ID')
        print(request.args.get('id'))

        #Need to update this so it looks for ID and not firstname.

        if form.validate():
            family_members.objects(firstName=form.firstName.data).update(middleName=form.middleName.data,
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
    return dict(results = analytics.quickPointsTotal())


if __name__ == '__main__':
    app.run(debug=True, port=5001)
