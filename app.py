from flask import Flask, send_from_directory, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
# from apiHandler import ApiHandler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
import pymysql.cursors
import ast

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


@app.route('/')
def testpage():
    try: 
        testdata = TestData.query.all()
        return '<h1>Connected to db :)</h1>'
    except Exception as e:
        print("\nThe error:\n" + str(e) + "\n here we finish")
        return '<h1>Not connected to db :(</h1>'
