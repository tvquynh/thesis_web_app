#app.py
from flask import Flask, render_template, request, jsonify
#from flask_mysqldb import MySQL,MySQLdb #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from werkzeug.utils import secure_filename
import os
from datetime import datetime
#-------------
from ember.features import PEFeatureExtractor
import numpy as np
import pandas as pd
import time
import lightgbm as lgb

 
app = Flask(__name__)
         
app.secret_key = "caircocoders-ednalan"
         
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'testingdb'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mysql = MySQL(app) 
 
app.config['UPLOAD_FOLDER'] = 'static/uploads'
   
# ALLOWED_EXTENSIONS = set(['acm', 'ax', 'cpl', 'dll','drv', 'efi', 'exe ', 'mui','ocx', 'scr', 'sys ', 'tsp','*'])
   
# def allowed_file(filename):
#  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def index(): 
    return render_template('index.html')
 
@app.route("/upload",methods=["POST","GET"])
def upload():
    file = request.files['uploadFile']
    filename = secure_filename(file.filename)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filenameimage = file.filename
        print (filenameimage)
        today = datetime.today() 
        # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cur.execute("INSERT INTO uploads (file_name,upload_time) VALUES (%s,%s)",[filenameimage,today])
        # mysql.connection.commit()       
        # cur.close()-----------
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        #file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        # file.save(file_path) # Then save the file
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #-----ML
        #Create column header
        columns = []
        for i in range(0,2381):
            feature = "f" + str(i)
            columns.append(feature)
        #Load selected features
        df_features = pd.read_csv('select_features.csv')
        select_features = df_features["0"]
        #Load model
        save_model = "PS-20M_lgb_1511-features_classifier.txt"
        #save_model = "lightgbm.model"

        gbm = lgb.Booster(model_file=save_model) 
        print ("Model", save_model, "is loaded")
        extractor = PEFeatureExtractor()
        # file_path = file_path.replace("/","\\")
        data = open(file_path,"rb").read()
        features = np.array(extractor.feature_vector(data), dtype=np.float32).reshape(1,-1)
        data = pd.DataFrame(features, columns=columns)
        selected_data = data[select_features]
        preds = gbm.predict(selected_data)
        file_stats = os.stat(file_path)
        if preds < 0.5:
            filenameimage = "nomalware.png"
            detected = " a goodware (^_^)"  
        else:
             detected = " a malware"
             filenameimage = "malware.jpg"
        result = file_path.rsplit('/', 1)[-1] + " is " + detected + " - File size is " + str(file_stats.st_size / (1024)) + " kilobytes"
        data = []

        # ------------------------------
        msg  = 'File successfully uploaded ' + file.filename + ' to the database!'
    else:
        msg  = 'Invalid Upload'
    return jsonify({'htmlresponse': render_template('response.html', msg=result, filenameimage=filenameimage)})
 
if __name__ == "__main__":
    app.run(debug=True)