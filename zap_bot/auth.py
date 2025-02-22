import os
import jwt
from app import app, connection
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, make_response

@app.get('/login')
def login():
  access_token = request.cookies.get('access_token')

  if authenticate_token(access_token):
    return redirect(url_for('index'))

  message = request.args.get('message', default = '', type = str)

  return render_template('login.html', message = message)





@app.get('/authentication')
def authentication():
  user = request.args.get('user', type = str)
  pwd = request.args.get('pwd', type = str)

  if authenticate_user(user, pwd):
    payload = {}
    payload['username'] = user
    payload['password'] = pwd
    payload['exp'] = datetime.now() + timedelta(minutes = 60)
    encoded_jwt = jwt.encode(payload, os.environ['JWT_SECRET'], algorithm="HS256")
    response = make_response(redirect(url_for('index')))
    response.set_cookie('access_token', encoded_jwt)
    return response
  else:
    return redirect(url_for('login', message = 'Invalid Credentials'))





def authenticate_user(name, password):
  sql = "SELECT name, password FROM users WHERE name = ? AND password = ?"

  cursor = connection.cursor()
  cursor.execute(sql, (name, password))
  user = cursor.fetchall()
  cursor.close()

  return bool(user)





def authenticate_token(access_token):
  try:
    payload = jwt.decode(access_token, os.environ['JWT_SECRET'], algorithms=["HS256"])
  except:
    return False
  
  return authenticate_user(payload['username'], payload['password'])