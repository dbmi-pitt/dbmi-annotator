from flask import Flask, render_template, request, json, session, flash, redirect, url_for, make_response
from forms import SignUpForm, SignInForm
from models import db
from models import User, Activation
import time, uuid, datetime
import sys, random, string, os
from export.exportPDDIAnnotation import exportAnnotationToCSV

## initialize
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = 'dbmi-annotator-test'

app.config.from_pyfile('config.py')

db.init_app(app)

from app import *

sys.stdout = sys.stderr
if __name__ == '__main__':
    app.run(port=5050, debug=True)


## define root and corresponding request handler
@app.route("/",methods=['POST','GET'])
def main():
    
    if 'email' in request.cookies:
        print 'DEBUG:' + str(request.cookies['email'])
    else: 
        print 'DEUBG:' + str(request.cookies)
    
    return render_template('index.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    
    form = SignUpForm()
    currEmail = request.cookies.get('email')

    if currEmail:
        return redirect(url_for('main'))

    if form.validate() == False:
        return render_template('signup.html', form=form)
    else:
		# get current date and time
		# create uuid for user
		currentDate = datetime.datetime.utcnow()
		uid = uuid.uuid4()

		## add activation
		expireTime = datetime.datetime.utcnow() + datetime.timedelta(days=10)
		newact = Activation(code_generator(),uid, expireTime)
		db.session.add(newact)
		db.session.commit()

		## add new user
		newuser = User(uid, form.username.data, 0, 0, form.email.data, 0, currentDate, currentDate, newact.id, form.password.data)
		db.session.add(newuser)
		db.session.commit()

		response = make_response(redirect(url_for('main')))
		response.set_cookie('email', form.email.data)

		session['email'] = form.email.data
        
		return response


@app.route('/signIn', methods=['POST','GET'])
def signIn():
    form = SignInForm()
    
    if 'email' in session:
        return redirect(url_for('main'))

    if form.validate() == False:
        return render_template('signin.html', form=form)
    else:

        session['email'] = form.email.data

        response = make_response(redirect(url_for('main')))  
        response.set_cookie('email',form.email.data)

        return response


@app.route('/signOut')
def signOut():
 
    if 'email' not in session:
        return redirect(url_for('signIn'))

    response = make_response(redirect(url_for('main')))
    response.set_cookie('email', '', expires=0)
    session.pop('email', None)
    
    return response
    #return redirect(url_for('main'))


def code_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
