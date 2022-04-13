from crypt import methods
from email.message import EmailMessage
from enum import unique
from errno import EACCES
from modulefinder import Module
from nis import cat
from operator import mod
from os import EX_CANTCREAT
from sqlite3 import Date
from unittest.result import STDERR_LINE
from flask import Flask, send_from_directory, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
# from apiHandler import ApiHandler
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy.sql import text, func, select
import pymysql
import pymysql.cursors
import ast
import json
import sys
import datetime

app = Flask(__name__)
CORS(app)
api = Api(app)

username = 'dillonreid15'
password = 'peerreview!'
userpass = 'mysql+pymysql://' + username + ':' + password + '@'


servername = 'dr-hons-peer-review-dbinstance.csrxetjagrne.eu-west-2.rds.amazonaws.com'
dbname = '/dr_hons_peer_review_db'
sslca = '?ssl_ca=global-bundle.pem'

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + servername + dbname + sslca
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'drhonspeerreview@gmail.com'
app.config['MAIL_PASSWORD'] = 'Hermes1609'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

db = SQLAlchemy(app)

class TestData(db.Model):
    __tablename__ = 'tbl_test_data'
    _id = db.Column(db.Text, primary_key=True)
    _index = db.Column(db.Integer)
    age = db.Column(db.Integer)
    fullname = db.Column(db.Text)
    email = db.Column(db.Text)
    phone = db.Column(db.Text)
    address = db.Column(db.Text)
    registered = db.Column(db.Text)   

class ModuleAssignedUsers(db.Model): 
    __tablename__ = 'ModuleAssignedUsers' 
    ModuleAssignedUserID = db.Column(db.Integer, primary_key=True)
    ModuleID = db.Column(db.Text)
    Email = db.Column(db.Text)

class Modules(db.Model):
    __tablename__ = 'Modules'
    ModuleID = db.Column(db.Text, primary_key=True)
    ModuleName = db.Column(db.Text)

class ReviewForm(db.Model):
    __tablename__ = 'ReviewForm'
    ReviewID = db.Column(db.Integer, primary_key=True)
    ReviewName = db.Column(db.Text)
    Visibility = db.Column(db.Text)
    DateDue = db.Column(db.Text)
    SubmittedFormJSON = db.Column(db.JSON)
    AssignedID = db.Column(db.Integer)

class ReviewFormAssignedTeams(db.Model):
    __tablename__ = 'ReviewFormAssignedTeams'
    ReviewFormAssignedTeamsID = db.Column(db.Integer, primary_key=True)
    TeamID = db.Column(db.Integer)
    ReviewID = db.Column(db.Integer)
    NoOfStudentsCompleted = db.Column(db.Integer)
    NoOfStudentsAssigned = db.Column(db.Integer)
    HasTeamCompleted = db.Column(db.Text)

class StudentAssignedTeams(db.Model): 
    __tablename__ = 'StudentAssignedTeams' 
    AssignmentID = db.Column(db.Integer, primary_key=True)
    TeamID = db.Column(db.Integer)
    Email = db.Column(db.Text)
    ModulatedMark = db.Column(db.Integer)
    ModulatedGrade = db.Column(db.Text)

class Teams(db.Model): 
    __tablename__ = 'Teams' 
    TeamsID = db.Column(db.Integer, primary_key=True)
    TeamName = db.Column(db.Text)
    ModuleID = db.Column(db.Integer)
    GroupMark = db.Column(db.Integer)
    GroupGrade = db.Column(db.Text)   
    AssessmentID = db.Column(db.Integer)

class User(db.Model): 
    __tablename__ = 'User' 
    Email = db.Column(db.Text, primary_key=True)
    IsStudent = db.Column(db.Integer)
    FullName = db.Column(db.Text)

class LecturerAssignedForm(db.Model):
    __tablename__ = 'LecturerAssignedForms'
    AssignedID = db.Column(db.Integer, primary_key=True)
    CreatedFormJSON = db.Column(db.JSON)
    Email = db.Column(db.Text)
    CreatedFormName = db.Column(db.Text)
    AssessmentID = db.Column(db.Integer)

class Assessment(db.Model):
    __tablename__ = 'Assessment'
    AssessmentID = db.Column(db.Integer, primary_key=True)
    AssessmentName = db.Column(db.Text)
    ModuleID = db.Column(db.Text)
    Email = db.Column(db.Text)

class AssessmentAssignedUsers(db.Model):
    __tablename__ = 'AssessmentAssignedUsers'
    AssignmentID = db.Column(db.Integer, primary_key=True)
    AssessmentID = db.Column(db.Integer)
    Email = db.Column(db.Text)


@app.route('/')
def testpage():
    try: 
        testdata = TestData.query.all()
        return '<h1>Connected to db :)</h1>'
    except Exception as e:
        print("\nThe error:\n" + str(e) + "\n here we finish")
        return '<h1>Not connected to db :(</h1>'

def moduleAssignedUser_serializer(moduleAssignedUser):
    return {
        'ModuleAssignedUserID' : moduleAssignedUser.ModuleAssignedUserID,
        'ModuleID' : moduleAssignedUser.ModuleID,
        'Email' : moduleAssignedUser.Email
    }

def modules_serializer(modules):
    return {
        'ModuleID' : modules.ModuleID,
        'ModuleName' : modules.ModuleName
    }    

def reviewForm_serializer(reviewForm):
    return {
        'ReviewID' : reviewForm.ReviewID,
        'ReviewName' : reviewForm.ReviewName,
        'Visibility' : reviewForm.Visibility,
        'DateDue' : reviewForm.DateDue,
        'SubmittedFormJSON' : reviewForm.SubmittedFormJSON,
        'AssignedID' : reviewForm.AssignedID
        # SubmittedFormJSON
    }        

def reviewFormAssignedTeams_serializer(reviewFormAssignedteams):
    return {
        'ReviewFormAssignedTeamsID' : reviewFormAssignedteams.ReviewFormAssignedTeamsID,
        'TeamID' : reviewFormAssignedteams.TeamID,
        'ReviewID' : reviewFormAssignedteams.ReviewID,
        'NoOfStudentsCompleted' : reviewFormAssignedteams.NoOfStudentsCompleted,
        'NoOfStudentsAssigned': reviewFormAssignedteams.NoOfStudentsAssigned,
        'HasTeamCompleted' : reviewFormAssignedteams.HasTeamCompleted
    }    

def studentAssignedTeams_serializer(studentAssignedTeams):
    return {
        'AssignmentID' : studentAssignedTeams.AssignmentID,
        'TeamID' : studentAssignedTeams.TeamID,
        'Email' : studentAssignedTeams.Email,
        'ModulatedMark' : studentAssignedTeams.ModulatedMark,
        'ModulatedGrade' : studentAssignedTeams.ModulatedGrade
    } 

def teams_serializer(teams):
    return {
        'TeamsID' : teams.TeamsID,
        'TeamName' : teams.TeamName,
        'ModuleID' : teams.ModuleID,
        'GroupMark' : teams.GroupMark,
        'GroupGrade' : teams.GroupGrade,
        'AssessmentID': teams.AssessmentID    
    }  

def user_serializer(user):
    return {
        'Email' : user.Email,
        'IsStudent' : user.IsStudent,
        'FullName' : user.FullName,
    }     

def lecturerassignedforms_serializer(lecturerassignedforms):
    return {
        'AssignedID' : lecturerassignedforms.AssignedID,
        'CreatedFormJSON' : lecturerassignedforms.CreatedFormJSON,
        'Email' : lecturerassignedforms.Email,
        'CreatedFormName' : lecturerassignedforms.CreatedFormName,
        'AssessmentID' : lecturerassignedforms.AssessmentID
    }    

def assessment_serializer(assessment):
    return {
        'AssessmentID' : assessment.AssessmentID,
        'AssessmentName' : assessment.AssessmentName,
        'ModuleID' : assessment.ModuleID,
        'Email' : assessment.Email
    }    


# ---------- COMPLETED / ADD SECURITY ---------- 
#Adds user to dataabase, only includes data available through 
#Microsoft authentication, Email, and name, from which I can also 
#get whether they're staff or a student
@app.route('/usercheck', methods=['GET', 'POST'])
def checkUserAccount():
    if request.method == 'POST':
        try:
            #change request byte object into a dict
            #get the user with matching email in DB
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            user_to_validate = User.query.filter(User.Email==req_data['Email']).first()
            if not user_to_validate:
                email = req_data['Email']
                isStudent = req_data['IsStudent']
                fullname = req_data['FullName']
                # print(email, file=sys.stderr)
                # print(isStudent, file=sys.stderr)
                userToAdd = User(Email=email, IsStudent=isStudent, FullName=fullname)

                db.session.add(userToAdd)
                db.session.commit()
                return { 'Message' : 'User now added to database'}
            if user_to_validate:    
                return { 'Message' : 'User already registered'}
        except:
            raise Exception("Cannot retrieve user")
    else:
        return {'Message':'Expected post'}            

#This is used to assign students teams, classes, and modules if none exists
#For testing purposes, can be deleted before use in a production environment
# ---------- STILL TO BE COMPLETED ---------- 
@app.route('/checkforstudentdata', methods=['GET', 'POST'])
def checkStudentData():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            email = req_data["Email"]
            modules = ModuleAssignedUsers.query.filter_by(Email=email).first()
            teams = StudentAssignedTeams.query.filter_by(Email=email).first()
            if modules or teams == None:
                #generate test data
                listOfModuleIDs = Modules.query.with_entities(Modules.ModuleID)

                for x in listOfModuleIDs:
                    userToInsert = ModuleAssignedUsers(ModuleID=x, Email=email)
                    db.session.add(userToInsert)
                    db.session.commit()

                return { 'Message' : 'Sample data successfully added' }          
            
            else:  
                return {'Message' : 'User has valid data'}
            #return jsonify([*])
        except:
            raise Exception("Failed to retrieve user")
    else:
        return {'Message':'Expected post'}            
       
#Get list of modules for signed in user,
#works for both students and staff as Emails are assigned to ModuleId's
#Regardless of whether or not they're a student or staff
@app.route('/getmymodules', methods=['GET', 'POST'])
def getMyModules():
    if request.method == 'POST':
        try: 
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            email = req_data['Email']
            listofTest =[]
            for row in ModuleAssignedUsers.query.with_entities(ModuleAssignedUsers.ModuleID).filter(ModuleAssignedUsers.Email == email).all():
                listofTest.append(row)

            listToPass = [i[0] for i in listofTest]

            listOfModules = Modules.query.filter(Modules.ModuleID.in_(listToPass)).all()

            return jsonify([*map(modules_serializer, listOfModules)])
        except: 
            raise Exception("Failed to retrieve Modules")
    else:
        return {'Message':'Expected post'}                

@app.route('/getlecturersformodule', methods=['GET', 'POST'])
def getLecturersForModule():
    if request.method == 'POST':
        try:
            req_data=ast.literal_eval(request.data.decode('utf-8'))
            moduleID = req_data['ModuleID']
            email = req_data['Email']
            listOfEmail = []
            for row in ModuleAssignedUsers.query.with_entities(ModuleAssignedUsers.Email).filter(ModuleAssignedUsers.ModuleID == moduleID).all():
                listOfEmail.append(row)

            listOfEmail = [i[0] for i in listOfEmail]
            ListOfUsersFromEmail = User.query.filter(User.Email.in_(listOfEmail), User.IsStudent == 0, User.Email != email).all()

            # print(email, file=sys.stderr)
            # print(ListOfUsersFromEmail, file=sys.stderr)
            return jsonify([*map(user_serializer, ListOfUsersFromEmail)])
        except:
            raise Exception("Failed to recieve lecturers")
    else:
        return {'Message':'Expected post'} 


#Upload JSON of form created by lecturer
@app.route('/uploadform', methods=['GET', 'POST'])
def uploadForm():
    if request.method == 'POST':
        try:
            req_data=ast.literal_eval(request.data.decode('utf-8'))
            content = req_data['Form']
            y = json.loads(content)
            email = y['email']
            createdformname = y['name']
            assessmentid = y['assessmentid']
            # print(email, file=sys.stderr)
            # print(createdformname, file=sys.stderr)
            toupload = LecturerAssignedForm(CreatedFormJSON = content, Email = email, CreatedFormName = createdformname, AssessmentID = assessmentid)
            db.session.add(toupload)
            db.session.flush()
            id = toupload.AssignedID
            db.session.commit()
            # print(str(toupload.AssignedID))
            return (str(toupload.AssignedID))
        except:
            raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

#Upload JSON of form created by lecturer

@app.route('/uploadformteam', methods=['GET', 'POST'])
def uploadFormTeam():
    if request.method == 'POST':
        try:
            req_data=ast.literal_eval(request.data.decode('utf-8'))
            content = req_data['Form']
            form = json.loads(content)
            assessmentid = form['AssessmentID']
            assignedid = form['AssignedID']
            teams = form['Teams']
            duedate = form['DueDate']
            duetime = form['DueTime']
            date = duedate + ' ' + duetime + ':00'
            date_time_obj = datetime.datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
            moduleID = Assessment.query.with_entities(Assessment.ModuleID).filter(Assessment.AssessmentID == assessmentid)
            assessmentName = Assessment.query.with_entities(Assessment.AssessmentName).filter(Assessment.AssessmentID == assessmentid)
            uniqueTeamNames = []
            for x in teams:
                uniqueTeamNames.append(x['teamname'])
            uniqueTeamNames = set(uniqueTeamNames)

            try:
                for x in uniqueTeamNames:
                    #create teams
                    team = Teams(TeamName = x, ModuleID = moduleID, AssessmentID = assessmentid)
                    db.session.add(team)
                    db.session.flush()
                    teamid = team.TeamsID
                    db.session.commit()

                    #create review form for team
                    reviewform = ReviewForm(ReviewName = assessmentName, Visibility = 1, DateDue = date_time_obj, AssignedID = assignedid)
                    db.session.add(reviewform)
                    db.session.flush()
                    reviewid = reviewform.ReviewID
                    db.session.commit()

                    noOfStudensPerTeam = 0
                    for y in teams:
                        if y['teamname'] == x:
                            noOfStudensPerTeam += 1

                    reviewassignedteam = ReviewFormAssignedTeams(TeamID = teamid, ReviewID = reviewid, NoOfStudentsCompleted = 0, NoOfStudentsAssigned = noOfStudensPerTeam, HasTeamCompleted = 0)
                    db.session.add(reviewassignedteam)
                    db.session.commit()

                    #assign students to teams
                    for z in teams:
                        if z['teamname'] == x:
                            student = StudentAssignedTeams(TeamID = teamid, Email = z['email'])
                            db.session.add(student)
                            db.session.commit()

            except:
                raise Exception("Failed to create")

            return { 'Message': 'Upload Successfuly'}

        except:
            raise Exception("Failed to upload form")
    else: 
        return {'Message':'Expected POST'}

# load form created by lecturer
@app.route('/loadunsubmittedform', methods=['GET', 'POST'])
def loadUnsubmittedForm():
    if request.method == 'POST':
        try:
            req_data=ast.literal_eval(request.data.decode('utf-8'))
            assignedID = req_data['AssignedID']

            return jsonify([*map(lecturerassignedforms_serializer, LecturerAssignedForm.query.filter(LecturerAssignedForm.AssignedID == assignedID))])
        except:
            raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 


#Upload JSON of assignment created by lecturer
@app.route('/createassignment', methods=['GET', 'POST'])
def createAssignment():
    if request.method == 'POST':
        try:
            req_data=ast.literal_eval(request.data.decode('utf-8'))
            content = req_data['Form']
            y = json.loads(content)
            email = y['creatoremail']
            assessmentname = y['assessmentname']

            listofassignee = y['lecturersformodule']
            moduleid = y['moduleid']
            # print(listofassignee, file=sys.stderr)
            # print(createdformname, file=sys.stderr)
            touploadassessment = Assessment(AssessmentName = assessmentname, ModuleID = moduleid, Email = email)      
            db.session.add(touploadassessment)
            db.session.flush()
            id = touploadassessment.AssessmentID
            db.session.commit()

            for x in listofassignee:
                touploadassessmentassignedusers = AssessmentAssignedUsers(AssessmentID = id, Email = x['email'])
                db.session.add(touploadassessmentassignedusers)
                db.session.commit()
            return (str(touploadassessment.AssessmentID))
        except:
            raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

#Return list of students for assignment
@app.route('/loadstudentsforassignment', methods=['GET', 'POST'])
def getMyAssessment():
    if request.method == 'POST':
        try: 
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            assessmentid = req_data['AssessmentID']

            moduleID = Assessment.query.with_entities(Assessment.ModuleID).filter(Assessment.AssessmentID == assessmentid)

            listOfUsers = []
            for row in ModuleAssignedUsers.query.with_entities(ModuleAssignedUsers.Email).filter(ModuleAssignedUsers.ModuleID == moduleID).all():
                listOfUsers.append([row[0]])

            listOfUsers = [i[0] for i in listOfUsers]

            users = User.query.filter(User.Email.in_(listOfUsers), User.IsStudent == 1).all()


            return jsonify([*map(user_serializer, users)])
        except: 
            raise Exception("Failed to retrieve Modules")
    else:
        return {'Message':'Expected POST'}   

@app.route('/getmyassessmentsstudent', methods=['GET', 'POST'])
def getStudentAssignments():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            email = req_data['Email']

            listOfTeamID = []
            for row in StudentAssignedTeams.query.with_entities(StudentAssignedTeams.TeamID).filter(StudentAssignedTeams.Email == email).all():
                listOfTeamID.append(row)
            listOfTeamID = [i[0] for i in listOfTeamID]
        
            listOfReviewID = []
            for row in ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID.in_(listOfTeamID)).all():
                listOfReviewID.append(row)
            listOfReviewID = [i[0] for i in listOfReviewID]

            # reviewForms = ReviewForm.query.filter(ReviewForm.ReviewID.in_(listOfReviewID)).all()
            return jsonify([*map(reviewForm_serializer, ReviewForm.query.filter(ReviewForm.ReviewID.in_(listOfReviewID)).all())])

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}

@app.route('/loadform', methods=['GET', 'POST'])
def getMyForm():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            reviewid = req_data['ReviewID']
            email = req_data['Email']

            assignedid = ReviewForm.query.with_entities(ReviewForm.AssignedID).filter(ReviewForm.ReviewID == reviewid).first()
            assessmentid = LecturerAssignedForm.query.with_entities(LecturerAssignedForm.AssessmentID).filter(LecturerAssignedForm.AssignedID == assignedid[0]).first()
            teamids = []
            for row in Teams.query.with_entities(Teams.TeamsID).filter(Teams.AssessmentID == assessmentid[0]).all():
                teamids.append(row)
            teamids = [i[0] for i in teamids]

            teamid = StudentAssignedTeams.query.with_entities(StudentAssignedTeams.TeamID).filter(StudentAssignedTeams.TeamID.in_(teamids)).filter(StudentAssignedTeams.Email == email).first()
            
            reviewform = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid)
            lecturerassignedform = LecturerAssignedForm.query.filter(LecturerAssignedForm.AssignedID == assignedid[0])

            emails = []
            for row in StudentAssignedTeams.query.with_entities(StudentAssignedTeams.Email).filter(StudentAssignedTeams.TeamID == teamid[0]).all():
                emails.append(row)
            emails = [i[0] for i in emails]

            users = User.query.filter(User.Email.in_(emails))
            

            return jsonify([*map(reviewForm_serializer, reviewform)], [*map(lecturerassignedforms_serializer, lecturerassignedform)], [*map(user_serializer, users)])

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}

#Currently unused
@app.route('/updatereview', methods=['GET', 'POST'])
def updateMyReview():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            reviewid = req_data['ReviewID']

            assignedid = ReviewForm.query.with_entities(ReviewForm.AssignedID).filter(ReviewForm.ReviewID == reviewid).first()
            assessmentid = LecturerAssignedForm.query.with_entities(LecturerAssignedForm.AssessmentID).filter(LecturerAssignedForm.AssignedID == assignedid[0]).first()
            teamid = Teams.query.with_entities(Teams.TeamsID).filter(Teams.AssessmentID == assessmentid[0]).first()
            
            reviewform = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid)
            lecturerassignedform = LecturerAssignedForm.query.filter(LecturerAssignedForm.AssignedID == assignedid[0])

            emails = []
            for row in StudentAssignedTeams.query.with_entities(StudentAssignedTeams.Email).filter(StudentAssignedTeams.TeamID == teamid[0]).all():
                emails.append(row)
            emails = [i[0] for i in emails]

            users = User.query.filter(User.Email.in_(emails))
            

            # reviewForms = ReviewForm.query.filter(ReviewForm.ReviewID.in_(listOfReviewID)).all()
            # return jsonify([*map(reviewForm_serializer, reviewform)], [*map(lecturerassignedforms_serializer, lecturerassignedform)], [*map(user_serializer, users)])

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}


@app.route('/deleteunfinished', methods=['GET', 'POST'])
def deleteUnfinished():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            assessmentid = req_data['AssessmentID']


            assessmentToDelete = Assessment.query.filter(Assessment.AssessmentID == assessmentid).first()
            db.session.delete(assessmentToDelete)
            db.session.commit()

            existsAssignedForm = db.session.query(db.exists().where(AssessmentAssignedUsers.AssessmentID == assessmentid)).scalar()
            if existsAssignedForm:
                assessmentAssignedUsersToDelete = AssessmentAssignedUsers.query.filter(AssessmentAssignedUsers.AssessmentID == assessmentid).all()
                for x in assessmentAssignedUsersToDelete:
                    db.session.delete(x)
                    db.session.commit()

            existsAssignedForm = db.session.query(db.exists().where(LecturerAssignedForm.AssessmentID == assessmentid)).scalar()
            if existsAssignedForm:
                lecturerAssignedFormToDelete = LecturerAssignedForm.query.filter(LecturerAssignedForm.AssessmentID == assessmentid).first()
                db.session.delete(lecturerAssignedFormToDelete)
                db.session.commit()

            return {'Message' : 'Unused content successfully deleted'}

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}

@app.route('/studentupdateform', methods=['GET', 'POST'])
def updateMyReviewStudent():
    if request.method == 'POST':
        try:
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            reviewid = req_data['ReviewID']
            formJSON = req_data['FormCat']

            email = formJSON[0]['Email']

            formToUpdate = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid).first()
            jsontoupdate = ReviewForm.query.with_entities(ReviewForm.SubmittedFormJSON).filter(ReviewForm.ReviewID == reviewid).first()
            teamToUpdate = ReviewFormAssignedTeams.query.filter(ReviewFormAssignedTeams.ReviewID == reviewid).first()
            noComp = teamToUpdate.NoOfStudentsCompleted
            if jsontoupdate[0] == None:
                formToUpdate.SubmittedFormJSON = formJSON
                db.session.commit()
                teamToUpdate.NoOfStudentsCompleted = 1
                db.session.commit()
            elif jsontoupdate[0] != None:
                toUpdate = []
                noCheck = 0
                for x in jsontoupdate[0]:
                    if x['Email'] == email:
                        noCheck = 1
                        toUpdate.extend(formJSON)
                    elif x['Email'] != email:
                        toUpdate.extend(x)
                if noCheck == 0:
                    teamToUpdate.NoOfStudentsCompleted = noComp + 1
                    db.session.commit()
                formToUpdate.SubmittedFormJSON = toUpdate
                db.session.commit()


            return {'Message':'Test'}
        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}


@app.route('/updateform', methods=['GET', 'POST'])
def updateForm():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                content = req_data['Form']
                form = json.loads(content)
                assessmentid = form['assessmentid']
                x = LecturerAssignedForm.query.filter(LecturerAssignedForm.AssessmentID == assessmentid).first()
                x.CreatedFormJSON = content
                db.session.commit()
                return {'Message': 'Successfully updated'}
            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/loadlecturerhomeforms', methods=['GET', 'POST'])
def getLecCreatedHome():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                email = req_data['Email']

                # ASSESSMENTS LECTURER HAS CREATED
                myAssessmentsIDs = []
                for row in LecturerAssignedForm.query.with_entities(LecturerAssignedForm.AssessmentID).filter(LecturerAssignedForm.Email == email):
                    myAssessmentsIDs.append(row)
                myAssessmentsIDs = [i[0] for i in myAssessmentsIDs]

                teamsIDMyAssessments = []
                for row in Teams.query.with_entities(Teams.TeamsID).filter(Teams.AssessmentID.in_(myAssessmentsIDs)):
                    teamsIDMyAssessments.append(row)
                teamsIDMyAssessments = [i[0] for i in teamsIDMyAssessments]

                reviewIDsMyAssessment = []
                for row in ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID.in_(teamsIDMyAssessments)):
                    reviewIDsMyAssessment.append(row)
                reviewIDsMyAssessment = [i[0] for i in reviewIDsMyAssessment]

                reviewFormsMyAssessments = ReviewForm.query.filter(ReviewForm.ReviewID.in_(reviewIDsMyAssessment)).all()

                return jsonify([*map(reviewForm_serializer, reviewFormsMyAssessments)])

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/loadlecturerassignedform', methods=['GET', 'POST'])
def getLecAssignedHome():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                email = req_data['Email']

                # ASSESSMENTS LECTURER HAS BEEN ASSIGNED TO
                assessmentsAssignedIDs = []
                for row in AssessmentAssignedUsers.query.with_entities(AssessmentAssignedUsers.AssessmentID).filter(AssessmentAssignedUsers.Email == email):
                    assessmentsAssignedIDs.append(row)
                assessmentsAssignedIDs = [i[0] for i in assessmentsAssignedIDs]

                teamsIDAssignedAssessments = []
                for row in Teams.query.with_entities(Teams.TeamsID).filter(Teams.AssessmentID.in_(teamsIDAssignedAssessments)):
                    teamsIDAssignedAssessments.append(row)
                teamsIDAssignedAssessments = [i[0] for i in teamsIDAssignedAssessments]

                reviewIDsAssignedAssessment = []
                for row in ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID.in_(teamsIDAssignedAssessments)):
                    reviewIDsAssignedAssessment.append(row)
                reviewIDsAssignedAssessment = [i[0] for i in reviewIDsAssignedAssessment]

                reviewFormsAssignedAssessments = ReviewForm.query.filter(ReviewForm.ReviewID.in_(reviewIDsAssignedAssessment)).all()


                return jsonify ([*map(reviewForm_serializer, reviewFormsAssignedAssessments)])

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/loadteamsforassignment', methods=['GET', 'POST'])
def getTeamsAssignment():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                assignedid = req_data['FormID']

                assessmentid = LecturerAssignedForm.query.with_entities(LecturerAssignedForm.AssessmentID).filter(LecturerAssignedForm.AssignedID == assignedid).first()
                assessment = Assessment.query.filter(Assessment.AssessmentID == assessmentid[0])

                reviewids = []
                for row in ReviewForm.query.with_entities(ReviewForm.ReviewID).filter(ReviewForm.AssignedID == assignedid):
                    reviewids.append(row)
                reviewids = [i[0] for i in reviewids]

                teamids = []
                for row in ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.TeamID).filter(ReviewFormAssignedTeams.ReviewID.in_(reviewids)):
                    teamids.append(row)
                teamids = [i[0] for i in teamids]

                ReviewFormAssignedTeamsToReturn = ReviewFormAssignedTeams.query.filter(ReviewFormAssignedTeams.ReviewID.in_(reviewids)).all()

                teamsToReturn = Teams.query.filter(Teams.TeamsID.in_(teamids)).all()


                return jsonify ([*map(reviewFormAssignedTeams_serializer, ReviewFormAssignedTeamsToReturn)], [*map(teams_serializer, teamsToReturn)], [*map(assessment_serializer, assessment)] )

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/getteamassignment', methods=['GET', 'POST'])
def getTeamForAssignment():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                teamid = req_data['TeamID']

                team = Teams.query.filter(Teams.TeamsID == teamid)
                students = StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID == teamid).all()
                reviewid = ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID == teamid)
                assignedid = reviewform = ReviewForm.query.with_entities(ReviewForm.AssignedID).filter(ReviewForm.ReviewID == reviewid)
                lecturerassignedform = LecturerAssignedForm.query.filter(LecturerAssignedForm.AssignedID == assignedid)
                reviewform = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid)

                return jsonify ([*map(teams_serializer, team)], [*map(studentAssignedTeams_serializer, students)], [*map(reviewForm_serializer, reviewform)], [*map(lecturerassignedforms_serializer, lecturerassignedform)])

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/updategrades', methods=['GET', 'POST'])
def updateGrades():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                catList = req_data['CatList']
                teamid = req_data['TeamID']
                lecMark = req_data['LecMark']
                lecGrade = req_data['LecGrade']

                #update mark and grade for team
                team = Teams.query.filter(Teams.TeamsID == teamid).first()
                team.GroupMark = lecMark
                db.session.commit()
                team.GroupGrade = lecGrade
                db.session.commit()

                #update submittedForm
                reviewid = ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID == teamid).first()
                review = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid[0]).first()
                review.SubmittedFormJSON = catList
                db.session.commit()

                #update mark and grade for each team member

                #get list of emails from team
                emails = []
                for row in StudentAssignedTeams.query.with_entities(StudentAssignedTeams.Email).filter(StudentAssignedTeams.TeamID == teamid):
                    emails.append(row)
                emails = [i[0] for i in emails]

                assignedid = ReviewForm.query.with_entities(ReviewForm.AssignedID).filter(ReviewForm.ReviewID == reviewid[0]).first()
                structure = LecturerAssignedForm.query.with_entities(LecturerAssignedForm.CreatedFormJSON).filter(LecturerAssignedForm.AssignedID == assignedid[0]).first()
                struc = json.loads(structure[0])

                listofCatAndWeighting = []
                for x in struc['column-list']:
                    print(x, file=sys.stderr)
                    if x['CategoryType'] == 'TeamMarked':
                        listofCatAndWeighting.append(x)

                listofForms = []
                listofFormsLec = []
                for y in catList:
                    if 'Lec' in y:
                        listofFormsLec.append(y)
                    elif 'Email' in y:
                        listofForms.append(y)

                if len(listofForms) == 0:
                    newWeightings = []
                    for x in listofCatAndWeighting:
                        newWeightings.append({ 'NewWeight': x['Weighting'], 'Category': x['Category']})
                else:
                    newWeightings = []
                    for x in listofCatAndWeighting:
                        for student in listofForms:
                            for cat in student['Form']:
                                if cat['Category'] == x['Category']:
                                    newCatWeight = 0
                                    for email in emails:
                                        if student['Email'] == email:
                                            newCatWeight = newCatWeight + int(cat['SuggestedMark'])
                                        else:
                                            newCatWeight = newCatWeight + int(cat['Weighting'])
                                    newCatWeight = newCatWeight / len(emails)
                                    newWeightings.append({ 'NewWeight': newCatWeight, 'Category': cat['Category']})

                emailWithGradeToMod = []
                for email in emails:
                    emailWithGradeToMod.append({'Email': email, 'GradeToMod': 100})
                updatedEmailGrades = []
                #if there are no student submitted forms
                if len(listofForms) == 0:
                    #If there are no lecturer marked categories
                    if len(listofFormsLec) == 0:
                        for email in emails:
                            updatedEmailGrades.append({ 'Email': email, 'Mark': lecMark, 'Grade': lecGrade})
                        print(updatedEmailGrades, file=sys.stderr)
                    else:
                        #if there are lecturer marked categories
                        for x in listofFormsLec[0]['Form']:
                                if 'Mark' in x:
                                    for student in emailWithGradeToMod:
                                        student['GradeToMod'] =  student['GradeToMod'] - x['Weighting'] + x['Mark']
                                elif  'Student' in x:
                                    for stuInLecSub in x['Student']:
                                        for student in emailWithGradeToMod:
                                            if stuInLecSub['Email'] == student['Email']:
                                                student['GradeToMod'] =  student['GradeToMod'] - x['Weighting'] + stuInLecSub['Mark']
                    #print(emailWithGradeToMod, file=sys.stderr)
                    for x in emailWithGradeToMod:
                        multi = x['GradeToMod'] / 100
                        gradeToAdd = multi * lecMark
                        appliedGrade = 'F'
                        if (float(gradeToAdd)) > (float(89)) and (float(gradeToAdd))  < (float(100)):
                            appliedGrade = 'A1'
                        elif (float(gradeToAdd)) > (float(79)) and (float(gradeToAdd)) < (float(90)):
                            appliedGrade = 'A2'
                        elif (float(gradeToAdd)) > (float(69)) and (float(gradeToAdd)) < (float(80)):
                            appliedGrade = 'A3'
                        elif (float(gradeToAdd)) > (float(59)) and (float(gradeToAdd)) < (float(70)):
                            appliedGrade = 'B'
                        elif (float(gradeToAdd)) > (float(49)) and (float(gradeToAdd)) < (float(60)):
                            appliedGrade = 'C'
                        elif (float(gradeToAdd)) > (float(39)) and (float(gradeToAdd)) < (float(50)):
                            appliedGrade = 'D'
                        elif (float(gradeToAdd)) < (float(40)):
                            appliedGrade = 'F'   
                        updatedEmailGrades.append({'Email': x['Email'], 'Mark': gradeToAdd, 'Grade': appliedGrade})
                #if there are student submitted forms
                else:
                    emailsNotSubbed = []
                    catsWithSumOf = []
                    studWithMarkSum = []
                    for cat in listofCatAndWeighting:
                        catsWithSumOf.append({'Category': cat['Category'], 'Student': []})
                    for y in emails:
                        for x in catsWithSumOf:
                            x['Student'].append({'Email': y, 'MarkSum': 0})
                    for email in emails:
                        for x in listofForms:
                            if x['Email'] == email:
                                for cat in x['Form']:
                                    for student in cat['Student']:
                                        for catWithSum in catsWithSumOf:
                                            if catWithSum['Category'] == cat['Category']:
                                                for sumCatStudent in catWithSum['Student']:
                                                    if sumCatStudent['Email'] == student['Email']:
                                                        sumCatStudent['MarkSum'] = sumCatStudent['MarkSum'] + student['SuggestedMark']
                                            # print(cat['Category'])
                                            # print(student['Email'], file=sys.stderr)
                                            # print(student, file=sys.stderr)

                            else:
                                for cat in catsWithSumOf:
                                    for student in cat['Student']:
                                        student['MarkSum'] = student['MarkSum'] + 100/len(emails)
                                        #print(student, file=sys.stderr)
                                        #print(email, file=sys.stderr)
                    for x in catsWithSumOf:
                        for y in newWeightings:
                            if x['Category'] == y['Category']:
                                for z in x['Student']:
                                    newSum = 0
                                    newSum = (float(z['MarkSum'] / 100) * (float(y['NewWeight'])))
                                    z['MarkSum'] = newSum

                    for email in emails:
                        updatedEmailGrades.append({'Email': email, 'Mark': 0, 'Grade': 'F'})


                    for email in updatedEmailGrades:
                        for x in catsWithSumOf:
                            for y in x['Student']:
                                if y['Email'] == email['Email']:
                                    email['Mark'] = email['Mark'] + y['MarkSum']

                    #if there are no lecturers marked categories
                    if len(listofFormsLec) == 0:
                        print("removerrorhere")
                    #if there are lecturer marked categories
                    else:
                        for x in listofFormsLec[0]['Form']:
                            if 'Mark' in x:
                                for y in updatedEmailGrades:
                                    y['Mark'] = y['Mark'] + x['Mark']
                            if 'Student' in x:
                                for y in x['Student']:
                                    for z in updatedEmailGrades:
                                        if y['Email'] == z['Email']:
                                            z['Mark'] = z['Mark'] + y['Mark']
                                            

                    for marktoMulti in updatedEmailGrades:
                        marktoMulti['Mark'] = ((float(marktoMulti['Mark'] / 100)) * (float(lecMark)))
                        appliedGrade = 'F'
                        if (float(marktoMulti['Mark'])) > (float(89)) and (float(marktoMulti['Mark']))  < (float(100)):
                            marktoMulti['Grade'] = 'A1'
                        elif (float(marktoMulti['Mark'])) > (float(79)) and (float(marktoMulti['Mark'])) < (float(90)):
                            marktoMulti['Grade'] = 'A2'
                        elif (float(marktoMulti['Mark'])) > (float(69)) and (float(marktoMulti['Mark'])) < (float(80)):
                            marktoMulti['Grade'] = 'A3'
                        elif (float(marktoMulti['Mark'])) > (float(59)) and (float(marktoMulti['Mark'])) < (float(70)):
                            marktoMulti['Grade'] = 'B'
                        elif (float(marktoMulti['Mark'])) > (float(49)) and (float(marktoMulti['Mark'])) < (float(60)):
                            marktoMulti['Grade'] = 'C'
                        elif (float(marktoMulti['Mark'])) > (float(39)) and (float(marktoMulti['Mark'])) < (float(50)):
                            marktoMulti['Grade'] = 'D'
                        elif (float(marktoMulti['Mark'])) < (float(40)):
                            marktoMulti['Grade'] = 'F'   
                #print(updatedEmailGrades, file=sys.stderr)
                for student in updatedEmailGrades:   
                    print(student, file=sys.stderr)
                    studentToUpdate = StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID == teamid).filter(StudentAssignedTeams.Email == student['Email']).first()
                    studentToUpdate.ModulatedMark = student['Mark']
                    db.session.commit()
                    studentToUpdate.ModulatedGrade = student['Grade']
                    db.session.commit()
                                                                     

                return {'Message':'Testing Successful'}

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/getstudentforassignment', methods=['GET', 'POST'])
def getStudentForAssignment():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                teamid = req_data['TeamID']
                email = req_data['Email']


                team = Teams.query.filter(Teams.TeamsID == teamid)
                reviewid = ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.ReviewID).filter(ReviewFormAssignedTeams.TeamID == teamid)
                reviewform = ReviewForm.query.filter(ReviewForm.ReviewID == reviewid)

                return jsonify ([*map(reviewForm_serializer, reviewform)])

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/exportgrades', methods=['GET', 'POST'])
def exportStudentGrades():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                assignedid = req_data['FormID']

                reviewids = []
                for row in  ReviewForm.query.with_entities(ReviewForm.ReviewID).filter(ReviewForm.AssignedID == assignedid).all():
                    reviewids.append(row)
                reviewids = [i[0] for i in reviewids]

                reviewname = ReviewForm.query.with_entities(ReviewForm.ReviewName).filter(ReviewForm.AssignedID == assignedid).first()
                teamids = []
                for row in ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.TeamID).filter(ReviewFormAssignedTeams.ReviewID.in_(reviewids)).all():
                    teamids.append(row)
                teamids = [i[0] for i in teamids]
                emails  = []
                for row in StudentAssignedTeams.query.with_entities(StudentAssignedTeams.Email).filter(StudentAssignedTeams.TeamID.in_(teamids)).all():
                    emails.append(row)
                emails = [i[0] for i in emails]

                users = User.query.filter(User.Email.in_(emails)).all()
                teams = Teams.query.filter(Teams.TeamsID.in_(teamids)).all()
                students = StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID.in_(teamids)).all()



                return jsonify ([*map(studentAssignedTeams_serializer, students)], [*map(teams_serializer, teams)], [*map(user_serializer, users)])

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

#Most users are randomly generated, and in case of a randomly generated email being the same
# as a real email address, emails will only be sent to the signed in user
@app.route('/emailgrades', methods=['GET', 'POST'])
def emailStudentGrades():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                email = req_data['Email']
                assignedid = req_data['FormID']
                reviewids = []
                for row in  ReviewForm.query.with_entities(ReviewForm.ReviewID).filter(ReviewForm.AssignedID == assignedid).all():
                    reviewids.append(row)
                reviewids = [i[0] for i in reviewids]

                reviewname = ReviewForm.query.with_entities(ReviewForm.ReviewName).filter(ReviewForm.AssignedID == assignedid).first()
                for id in reviewids:

                    teamid = ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.TeamID).filter(ReviewFormAssignedTeams.ReviewID == reviewid[0]).first()
                    groupmark = Teams.query.with_entities(Teams.GroupMark).filter(Teams.TeamsID == teamid[0]).first()
                    groupgrade = Teams.query.with_entities(Teams.GroupGrade).filter(Teams.TeamsID == teamid[0]).first()
                    
                    students = []
                    for row in StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID == teamid[0]).all():
                        students.append(row)

                    for x in students:
                        if x.Email == email:
                            msg = Message(sender = 'drhonspeerreview@gmail.com', recipients = [email])
                            msg.body = 'Results for test: ' + reviewname[0] + 'User: ' + email + 'Group Mark: ' + str(groupmark[0]) + 'Group Grade: ' + groupgrade[0] + 'Your Individual Mark: ' + str(x.ModulatedMark) + 'Your Individual Grade: ' + x.ModulatedGrade
                            msg.html = '<b>Results for test:</b> ' + reviewname[0] + '<br>' + '<b>User:</b> ' + email + '<br>' + '<b>Group Mark:</b> ' + str(groupmark[0]) + '<br>' + '<b>Group Grade:</b> ' + groupgrade[0] + '<br>' + '<b>Your Individual Mark:</b> ' + str(x.ModulatedMark) + '<br>' + '<b>Your Individual Grade:</b> ' + x.ModulatedGrade
                            msgString = 'Results: ' + reviewname[0]
                            msg.subject = msgString
                            mail.send(msg)
                return {'Message': 'Success'}

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

#Most users are randomly generated, and in case of a randomly generated email being the same
# as a real email address, emails will only be sent to the signed in user
@app.route('/emailreminder', methods=['GET', 'POST'])
def emailStudentReminder():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                email = req_data['Email']
                assignedid = req_data['FormID']
                reviewids = []
                for row in  ReviewForm.query.with_entities(ReviewForm.ReviewID).filter(ReviewForm.AssignedID == assignedid).all():
                    reviewids.append(row)
                reviewids = [i[0] for i in reviewids]
                reviewname = ReviewForm.query.with_entities(ReviewForm.ReviewName).filter(ReviewForm.AssignedID == assignedid).first()

                for id in reviewids:

                    teamid = ReviewFormAssignedTeams.query.with_entities(ReviewFormAssignedTeams.TeamID).filter(ReviewFormAssignedTeams.ReviewID == id).first()
                    groupmark = Teams.query.with_entities(Teams.GroupMark).filter(Teams.TeamsID == teamid[0]).first()
                    groupgrade = Teams.query.with_entities(Teams.GroupGrade).filter(Teams.TeamsID == teamid[0]).first()
                    
                    students = []
                    for row in StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID == teamid[0]).all():
                        students.append(row)

                    for x in students:
                        if x.Email == email:
                            msg = Message(sender = 'drhonspeerreview@gmail.com', recipients = [email])
                            msg.body = 'Results for test: ' + reviewname[0] + ' User: ' + email + ' This is a reminder to complete your peer review form for this assignment' 
                            msg.html = '<b>Results for test:</b> ' + reviewname[0] + '<br>' + '<b>User:</b> ' + email + '<br>' + '<b>This is a reminder to complete your peer review form for this assignment</b> ' 
                            msgString = 'Results: ' + reviewname[0]
                            msg.subject = msgString
                            mail.send(msg)
                return {'Message': 'Success'}

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 


@app.route('/settocomplete', methods=['GET', 'POST'])
def setAssignmentToComplete():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                assignedid = req_data['FormID']
                reviewids = []
                for row in  ReviewForm.query.with_entities(ReviewForm.ReviewID).filter(ReviewForm.AssignedID == assignedid).all():
                    reviewids.append(row)
                reviewids = [i[0] for i in reviewids]
                for id in reviewids:
                    reviewToUpdate = ReviewForm.query.filter(ReviewForm.ReviewID == id).first()
                    reviewToUpdate.Visibility = 0
                    db.session.commit()

                return {'Message': 'Success'}

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 

@app.route('/updateindiv', methods=['GET', 'POST'])
def updateIndivGrade():
    if request.method == 'POST':
            try:
                req_data=ast.literal_eval(request.data.decode('utf-8')) 
                email = req_data['Email']
                teamid = req_data['TeamID']
                mark = req_data['Mark']

                grade = 'F'
                if (float(mark)) > (float(89)) and (float(mark))  < (float(100)):
                    grade = 'A1'
                elif (float(mark)) > (float(79)) and (float(mark)) < (float(90)):
                    grade = 'A2'
                elif (float(mark)) > (float(69)) and (float(mark)) < (float(80)):
                    grade = 'A3'
                elif (float(mark)) > (float(59)) and (float(mark)) < (float(70)):
                    grade = 'B'
                elif (float(mark)) > (float(49)) and (float(mark)) < (float(60)):
                    grade = 'C'
                elif (float(mark)) > (float(39)) and (float(mark)) < (float(50)):
                    grade = 'D'
                elif (float(mark)) < (float(40)):
                    grade = 'F'   
                
                studentToUpdate = StudentAssignedTeams.query.filter(StudentAssignedTeams.TeamID == teamid).filter(StudentAssignedTeams.Email == email).first()
                studentToUpdate.ModulatedMark = mark
                db.session.commit()
                studentToUpdate.ModulatedGrade = grade
                db.session.commit()

                return {'Message': 'Success'}

            except:
                raise Exception("Failed to upload")
    else:
        return {'Message':'Expected post'} 