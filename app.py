#https://www.mongodb.com/compatibility/mongoengine-pymongo
#https://www.tutorialspoint.com/mongoengine/mongoengine_quick_guide.htm

from flask import Flask, render_template, request, redirect, flash
from mongoengine import connect
import json
import datetime

from formClasses import *

app = Flask(__name__)
app.config.from_pyfile('config.py')

#Connect to MongoDB Atlas cluster
DBHOST = app.config['DBHOST']
DBNAME = app.config['DBNAME']
hostString = DBHOST + DBNAME
connect(host=hostString)


# Define a route to render the user form
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/addFamilyMember', methods=['GET', 'POST'])
def addFamilyMember():
    print('Fn addFamilyMember')
    form = family_member_form(request.form)
    if request.method == 'POST' and form.validate():
        print('Request and validated')

        print(type(form.dob.data))

        user = family_members(firstName = form.firstName.data,
                             lastName = form.lastName.data,
                             email = form.email.data,
                             dob = form.dob.data.isoformat(),
                             admin = form.admin.data)
        user.save()

        # Redirect back to the index page
        flash('User created successfully!', 'success')
        return redirect('/')
    return render_template('addFamilyMember.html', form=form)


#Define route to fly page
@app.route('/flies', methods=['GET', 'POST'])
def flies():
    print('Fn flies')
    form = fly_kills_form(request.form)
    if request.method == 'POST' and form.validate():
        print('Request and validated')
        print(form.dow.data.isoformat())
        fKills = fly_kills(firstName = form.winner.data,
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


#Users Page
@app.route('/viewAllFamilyMembers', methods=['GET', 'POST'])
def viewAllFamilyMembers():

    userList = []
    for user in family_members.objects:
        userList.append(user)

    return render_template('viewAllFamilyMembers.html', users=userList)


@app.context_processor
def pointsFlysToHTML():
    return dict(pointsFlys=pointsFlys)

@app.context_processor
def pointsGamesHTML():
    return dict(pointsGames=pointsGames)

@app.context_processor
def pointsChiaSeedsToHTML():
    return dict(pointsChiaSeeds=pointsChiaSeeds)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
