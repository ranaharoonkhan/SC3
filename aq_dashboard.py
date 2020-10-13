from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq
import requests


APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\HP.LAPTOP-P2BK7MFS\\Desktop\\sc3\db.sqlite3'
DB = SQLAlchemy(APP)
#DB.init_app(APP) 

api = openaq.OpenAQ()
status, body = api.measurements(city='Los Angeles', parameter='pm25')
results= body['results']
r_list=[]
for r in results:
    r=str(r).split(',')
    utc = r[2][17:37]
    value = r[4][9:12]
    r_list.append(tuple([utc,int(value)]))


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        #s = 'Time: %r --- Value: %r \n' % (self.datetime, self.value)
        s= '\n'.join % (self.datetime, self.value)
        return s


@APP.route('/')
def root():
    risky_area = Record.query.filter(Record.value > 9).all()
    return  str(risky_area)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    for i in r_list:
        data = Record(datetime=i[0],value=i[1])
        DB.session.add(data)
            
    DB.session.commit()
    
    return 'Data refreshed!'



