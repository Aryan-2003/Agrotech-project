from flask import Flask, render_template, request
import pandas as pd
import requests
import os
import base64

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def hello():
  return render_template('index.html')


@app.route("/login")
def login():
  return render_template('login.html')


@app.route("/CropRecommendation")
def crop():
  return render_template("CropRecommendation.html")


@app.route("/FertilizerRecommendation")
def fertilizer():
  return render_template("FertilizerRecommendation.html")


@app.route("/PesticideRecommendation", methods=['GET', 'POST'])
def pesticide():
  if request.method == 'POST':
    file = request.files['image']  # fetch input
    filename = file.filename

    file_path = os.path.join('static/user_uploaded', filename)
    file.save(file_path)

    url = 'https://us-central1-crop-recommendation-cnn.cloudfunctions.net/predict'

    payload = {'image': open(file_path, 'rb')}

    response = requests.post(url, files=payload)

    # Check the response
    print(response.status_code)
    print(response.json())

    # with open(file_path, 'rb') as file:
    #   file_data = file.read()
    # # print(file_data)
    # encoded_image = base64.b64encode(file_data).decode('utf-8')
    # payload = {
    #   'image': encoded_image,
    # }
    # print(file_path)
    # response = requests.post(url, json=payload)
    # print(response.status_code)
    # print(response.content)
    # a = requests.post(url, data=image_data)
    # print(a.content)
    # return a.json()
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


# @app.route("/predict", methods=['GET', 'POST'])
# def predict():
#   if request.method == 'POST':


@app.route("/feedback", methods=['GET', 'POST'])
def give_feedback():
  if request.method == 'POST':
    feed = request.form['given_feedback']
    return feed
  return render_template('feedback.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
