from crypt import methods
from email.message import EmailMessage
from modulefinder import Module
from os import EX_CANTCREAT
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


class Class(db.Model):
    __tablename__ = 'Class'
    ClassID = db.Column(db.Integer, primary_key=True)
    ClassName = db.Column(db.Text)
    ModuleID = db.Column(db.Text)

class ClassAssignedUsers(db.Model):
    __tablename__ = 'ClassAssignedUsers'
    AssignmentID = db.Column(db.Integer, primary_key=True)
    ClassID = db.Column(db.Integer)
    Email = db.Column(db.Text)

class CourseAssignedStudents(db.Model):
    __tablename__ = 'CourseAssignedStudents'
    AssignmentID = db.Column(db.Integer, primary_key=True)
    UCASID = db.Column(db.Text)
    Email = db.Column(db.Text)    

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
    DateCreated = db.Column(db.Text)
    StructureID = db.Column(db.Integer)
    SumittedFormJSON = db.Column(db.JSON)
    IsTeamAssignment = db.Column(db.Integer)

class ReviewFormAssignedTeams(db.Model):
    __tablename__ = 'ReviewFormAssignedTeams'
    ReviewFormAssignedTeamsID = db.Column(db.Integer, primary_key=True)
    TeamID = db.Column(db.Integer)
    ReviewID = db.Column(db.Integer)
    NoOfStudentsCompleted = db.Column(db.Integer)
    NoOfStudentsAssigned = db.Column(db.Integer)
    HasTeamCompleted = db.Column(db.Text)

class ReviewFormStructure(db.Model): 
    __tablename__ = 'ReviewFormStructure'
    StructureID = db.Column(db.Integer, primary_key=True)
    StructureName = db.Column(db.Text)
    FormStructureJSON = db.Column(db.JSON)

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
    ClassID = db.Column(db.Integer)
    GroupMark = db.Column(db.Integer)
    GroupGrade = db.Column(db.Text)   

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
    ReviewID = db.Column(db.Integer)

class ClassAssessment(db.Model):
    __tablename__ = 'ClassAssessment'
    AssessmentID = db.Column(db.Integer, primary_key=True)
    ClassID = db.Column(db.Integer)
    AssessmentName = db.Column(db.Text)


@app.route('/')
def testpage():
    try: 
        testdata = TestData.query.all()
        return '<h1>Connected to db :)</h1>'
    except Exception as e:
        print("\nThe error:\n" + str(e) + "\n here we finish")
        return '<h1>Not connected to db :(</h1>'

def class_serializer(classes):
    return {
        'ClassID' : classes.ClassID,
        'ClassName' : classes.ClassName,
        'ModuleID' : classes.ModuleID
    }

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
        'DateDue' : reviewForm.DataDue,
        'DateCreated' : reviewForm.DataCreated,
        'StructureID' : reviewForm.StructureID,
        'IsTeamAssignment' : reviewForm.IsTeamAssignment
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

def reviewFormStructure_serializer(reviewFormStructure):
    return {
        'StructureID' : reviewFormStructure.StructureID,
        'StructureName' : reviewFormStructure.StructureName,
        # FormStructureJSON
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
        'ClassID' : teams.ClassID,
        'GroupMark' : teams.GroupMark,
        'GroupGrade' : teams.GroupGrade        
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
        'ReviewID' : lecturerassignedforms.ReviewID
    }    

def classassessment_serializer(classassement):
    return {
        'AssessmentID' : classassement.AssessmentID,
        'ClassID' : classassement.ClassID,
        'AssessmentName' : classassement.AssessmentName,
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
            classes = ClassAssignedUsers.query.filter_by(Email=email).first()
            modules = ModuleAssignedUsers.query.filter_by(Email=email).first()
            teams = StudentAssignedTeams.query.filter_by(Email=email).first()
            courseAssignedStudents = StudentAssignedTeams.query.filter.by("Email=email").first()
            if modules or classes or teams == None:
                #generate test data
                listOfModuleIDs = Modules.query.with_entities(Modules.ModuleID)

                for x in listOfModuleIDs:
                    userToInsert = ModuleAssignedUsers(ModuleID=x, Email=email)
                    db.session.add(userToInsert)
                    db.session.commit()

                courseUser = CourseAssignedStudents(UCASID='G400', Email=email)
                db.session.add(courseUser)
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

#Return list of classes for given ModuleID
@app.route('/getclassesformodule', methods=['GET', 'POST'])
def getMyClasses():
    if request.method == 'POST':
        try: 
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            moduleid = req_data['ModuleID']
            return jsonify([*map(class_serializer, Class.query.filter(Class.ModuleID == moduleid))])
        except: 
            raise Exception("Failed to retrieve Modules")
    else:
        return {'Message':'Expected post'}        

#Return list of assessments for given Class
@app.route('/getassessmentsformodule', methods=['GET', 'POST'])
def getMyAssessments():
    if request.method == 'POST':
        try: 
            req_data = ast.literal_eval(request.data.decode('utf-8'))
            moduleid = req_data['ModuleID']
            listofAssessments =[]
            for row in ModuleAssignedUsers.query.with_entities(ModuleAssignedUsers.ModuleID).filter(ModuleAssignedUsers.Email == email).all():
                listofAssessments.append(row)

            listToPass = [i[0] for i in listofAssessments]


            return jsonify([*map(classassessment_serializer, ClassAssessment.query.filter(ClassAssessment.ClassID == classid))])
        except: 
            raise Exception("Failed to retrieve Modules")
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
            # print(email, file=sys.stderr)
            # print(createdformname, file=sys.stderr)
            toupload = LecturerAssignedForm(CreatedFormJSON = content, Email = email, CreatedFormName = createdformname)
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
            print(ListOfUsersFromEmail, file=sys.stderr)
            return jsonify([*map(user_serializer, ListOfUsersFromEmail)])
        except:
            raise Exception("Failed to recieve lecturers")
    else:
        return {'Message':'Expected post'} 

# @app.route('/createteam', methods=['GET', 'POST'])
# def createTeam():
#     if request.method == 'POST':
#         try:
            
#         except: 
#             raise Exception("Failed to create teams")
#     else:
#         return {'Message':'Expected post'}

#getMyReviewFormListStudents

#loadReviewFormStudent

#getMyTeamStudent

#createReviewFormLecturer

#createTeamsLecturer

#submitTeamPropositionStudent

#updateTeamPropositionLecturer

#setPropositionRestraint

#getStudentDetails
