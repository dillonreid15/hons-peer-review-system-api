from crypt import methods
from email.message import EmailMessage
from enum import unique
from modulefinder import Module
from operator import mod
from os import EX_CANTCREAT
from sqlite3 import Date
from flask import Flask, send_from_directory, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
# from apiHandler import ApiHandler
from flask_sqlalchemy import SQLAlchemy
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

servername = 'dr-hons-peer-review-dbinstance.crpwaqlxefnd.eu-west-2.rds.amazonaws.com'
dbname = '/dr_hons_peer_review_db'
sslca = '?ssl_ca=global-bundle.pem'

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + servername + dbname + sslca
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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
        'TeamsID' : teams.TeamID,
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
            return jsonify([*map(reviewForm_serializer, reviewform)], [*map(lecturerassignedforms_serializer, lecturerassignedform)], [*map(user_serializer, users)])

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}

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



            # reviewForms = ReviewForm.query.filter(ReviewForm.ReviewID.in_(listOfReviewID)).all()
            return {'Message' : 'Unused content successfully deleted'}

        except:
            raise Exception("Failed to get assessments")
    else: 
        return {'Message':'Expected POST'}

#loadReviewFormStudent

#getMyTeamStudent

#submitTeamPropositionStudent

#updateTeamPropositionLecturer

#setPropositionRestraint

#getStudentDetails
