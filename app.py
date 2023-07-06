from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import requests
import os
import pickle
import numpy as np
from markupsafe import Markup
from utils.fertilizer import fertilizer_dict
from sqlalchemy import create_engine, text
from database import register_user, retrive_hashed_password, store_feedback
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':

    username = request.form['username']
    email = request.form['email']

    password = request.form['password']
    hashed_password = pbkdf2_sha256.hash(password)


    register_user(username, email, hashed_password)

    return redirect('/login')

  return render_template('register.html')


@app.route('/login', methods =['GET', 'POST'])
def login():
  if request.method=='POST':
    email = request.form['email']
    entered_password = request.form['password']
    hashed_password = retrive_hashed_password(email)
    if pbkdf2_sha256.verify(entered_password, hashed_password):
     
      return redirect('index')
    else:
      wrong_credentials = True
      return render_template('auth.html', res = wrong_credentials)
  return render_template('auth.html')

# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
def home():
  return render_template('unauth_index.html')
  
@app.route('/index')
def hello():
  return render_template('index.html')


@app.route("/CropRecommendation")
def crop():
  return render_template("CropRecommendation.html")


@app.route('/crop_prediction', methods=['POST'])
def crop_prediction():
  if request.method == 'POST':
    labels = {
      0: 'apple',
      1: 'banana',
      2: 'blackgram',
      3: 'chickpea',
      4: 'coconut',
      5: 'coffee',
      6: 'cotton',
      7: 'grapes',
      8: 'jute',
      9: 'kidneybeans',
      10: 'lentil',
      11: 'maize',
      12: 'mango',
      13: 'mothbeans',
      14: 'mungbean',
      15: 'muskmelon',
      16: 'orange',
      17: 'papaya',
      18: 'pigeonpeas',
      19: 'pomegranate',
      20: 'rice',
      21: 'watermelon'
    }

    crop_recommendation_model = pickle.load(open('models/pipe.pkl', 'rb'))

    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['potassium'])
    ph = float(request.form['ph'])
    rainfall = float(request.form['rainfall'])
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    my_prediction = crop_recommendation_model.predict(data)
    final_prediction = my_prediction[0]
    crop_name = labels[final_prediction]
    return render_template('crop-result.html',
                           prediction=crop_name,
                           pred='img/crop/' + crop_name + '.jpg')


@app.route("/FertilizerRecommendation")
def fertilizer():
  return render_template("FertilizerRecommendation.html")


@app.route("/PesticideRecommendation", methods=['GET', 'POST'])
def pesticide():
  if request.method == 'POST':
    file = request.files['image']
    filename = file.filename

    file_path = os.path.join('static/user_uploaded', filename)
    file.save(file_path)

    url = 'https://us-central1-crop-recommendation-cnn.cloudfunctions.net/predict'

    payload = {'file': open(file_path, 'rb')}

    response = requests.post(url, files=payload)
    pest_name = response.text.split(':')[1].strip().lower()
    l = len(pest_name)
    pest_name = pest_name[1:l - 2]
    print(pest_name)
    return render_template(f"{pest_name}.html", pred=pest_name)

  return render_template("PesticideRecommendation.html")


@app.route('/fertilizer-predict', methods=['POST'])
def fertilizer_recommend():
  if request.method == 'POST':
    crop_name = str(request.form['cropname'])
    N_filled = int(request.form['nitrogen'])
    P_filled = int(request.form['phosphorous'])
    K_filled = int(request.form['potassium'])

    df = pd.read_csv('Data/Crop_NPK.csv')

    N_desired = df[df['Crop'] == crop_name]['N'].iloc[0]
    P_desired = df[df['Crop'] == crop_name]['P'].iloc[0]
    K_desired = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = N_desired - N_filled
    p = P_desired - P_filled
    k = K_desired - K_filled

    if n < 0:
      key1 = "NHigh"
    elif n > 0:
      key1 = "Nlow"
    else:
      key1 = "NNo"

    if p < 0:
      key2 = "PHigh"
    elif p > 0:
      key2 = "Plow"
    else:
      key2 = "PNo"

    if k < 0:
      key3 = "KHigh"
    elif k > 0:
      key3 = "Klow"
    else:
      key3 = "KNo"

    abs_n = abs(n)
    abs_p = abs(p)
    abs_k = abs(k)

    response1 = Markup(str(fertilizer_dict[key1]))
    response2 = Markup(str(fertilizer_dict[key2]))
    response3 = Markup(str(fertilizer_dict[key3]))
    return render_template('Fertilizer-Result.html',
                           recommendation1=response1,
                           recommendation2=response2,
                           recommendation3=response3,
                           diff_n=abs_n,
                           diff_p=abs_p,
                           diff_k=abs_k)





if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
