from flask import Flask, render_template, request, redirect, flash
from mongoengine import connect, Document, StringField, EmailField, DynamicDocument, DateTimeField, BooleanField, IntField 
from wtforms import Form, StringField, validators, DateTimeField, BooleanField, SelectField, IntegerField 
from wtforms.fields import DateField

'''
MongoDB Classes must be 'synced' with WTForm Classes. Since MongoDB Forms are dynamic, not
 all syncing happens when the form is defined. Look at routes for final format.
'''

#------------- Point Assignments: [(value, label)] -------------#
pointsFlys = [(3, 'One Shot - One Kill'), (1, 'Multiple Whacks')]
pointsGames = [(3, 'First Place'), (1, 'Second Place')]
pointsChiaSeeds = [(1, 'Found Chia Seed'), (0, 'Incorrect Guess'), (1, 'Point to Cook')]

#------------- Family Members -------------#
class family_members(DynamicDocument):
    firstName = StringField(required=True)
    middelName = StringField(required=True)
    lastName = StringField(required=True)
    nickName = StringField(required=False)
    email = StringField(required=False)
    dob = DateTimeField(required=True)
    admin = BooleanField(required=False)
    pictureFilename = StringField(required=False)

# Define a form for creating new users
class family_member_form(Form):
    firstName = StringField('First Name', [validators.DataRequired()])
    middleName = StringField('Middle Name', [validators.DataRequired()])
    lastName = StringField('Last Name', [validators.DataRequired()])
    nickName = StringField('Nickname', [validators.Optional()])
    email = StringField('Email', [validators.Email(), validators.Optional()])
    dob = DateField('Date of Birth', [validators.DataRequired()], format='%Y-%m-%d')
    admin = BooleanField('Admin', [validators.Optional()])
    mf = SelectField('Male or Female', choices=[('m', 'Male'), ('f', 'Female')]) 
    pictureFilename = StringField('Picture filename', [validators.Optional()])


#------------- Fly Kills -------------#
class fly_kills(DynamicDocument):
    dow = DateTimeField(required=True)

class fly_kills_form(Form):
    dow = DateField('Date of Kill', [validators.DataRequired()], format='%Y-%m-%d')
    winner = SelectField()
    points = SelectField('Points', choices=pointsFlys)

    def __init__(self, *args, **kwargs):
        self.winner.kwargs['choices'] = [user.firstName for user in family_members.objects]
        Form.__init__(self, *args, **kwargs)


#------------- Actual Games -------------#
class board_games(DynamicDocument):
    game = StringField(required=True)
    dateAdded = DateTimeField(required=True)

class board_game_add_form(Form):
    game = StringField('Game Name', [validators.DataRequired()])
    dateAdded = DateField('Date Added', [validators.DataRequired()], format='%Y-%m-%d')


#------------- Game Wins -------------#
class board_games_winner(DynamicDocument):
    dow = DateTimeField(required=True)

class board_games_winner_form(Form):
    dow = DateField('Date of win', [validators.DataRequired()], format='%Y-%m-%d')
    winner = SelectField()
    game = SelectField()
    points = SelectField('Points', choices=pointsGames)

    def __init__(self, *args, **kwargs):
        self.winner.kwargs['choices'] = [user.firstName for user in family_members.objects]
        self.game.kwargs['choices'] = [bName.game for bName in board_games.objects]
        Form.__init__(self, *args, **kwargs)


#------------- Chia Seeds -------------#
class chia_seeds(DynamicDocument):
    dow = DateTimeField(required=True)

class chia_seeds_form(Form):
    dow = DateField('Date Chia Seeds Found', [validators.DataRequired()], format='%Y-%m-%d')
    winner = SelectField()
    points = SelectField('Points', choices=pointsChiaSeeds)

    def __init__(self, *args, **kwargs):
        self.winner.kwargs['choices'] = [user.firstName for user in family_members.objects]
        Form.__init__(self, *args, **kwargs)


#------------- Push Ups -------------#
class push_ups(DynamicDocument):
    dateAdded = DateTimeField(required=True)
    count = IntField(required=True)

class push_ups_form(Form):
    dateAdded = DateField('Date completed')
    count = IntegerField('Number of Push ups', [validators.DataRequired()])
    winner = SelectField()
    
    def __init__(self, *args, **kwargs):
        self.winner.kwargs['choices'] = [user.firstName for user in family_members.objects]
        Form.__init__(self, *args, **kwargs)
                     

#------------- Misc -------------#
class miscPoints(DynamicDocument):
    dow = DateTimeField(required=True)
    winner = SelectField(required=True)

class miscPoints_form(Form):
    dow = DateField('Date', [validators.DataRequired()], format='%Y-%m-%d')
    winner = SelectField()
    points = IntegerField('Number of Points', [validators.DataRequired()])
    reason = StringField('Reason for Points', [validators.Optional()])

    def __init__(self, *args, **kwargs):
        self.winner.kwargs['choices'] = [user.firstName for user in family_members.objects]
        Form.__init__(self, *args, **kwargs)
