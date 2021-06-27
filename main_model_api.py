from flask import Flask
from flask import request
import flask
from flask_restful import Resource, Api, reqparse
import requests  # to get image from the web
import shutil  # to save it locally
import os
import urllib
import urllib.request
import json
# import re
# import json
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch
# import numpy as np

app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = True

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = './data/img'

class Model(Resource):

    def post(self):
        src_dir = os.getcwd()
        dest_dir = src_dir + "/img"
        image_url = request.form['image']
        image_description = request.form['image_description']
        if not image_url:
            return "<h1>It didnt't work./p>"
        else:
            filename = image_url.split("/")[-1]
            fullfilename = os.path.join(UPLOAD_FOLDER, filename)
            file_ending = image_url.split(".")[-1]
            only_filename = filename.split(".")[0]
            print(only_filename)
            if self.validate_file(filename):
                response = requests.get(image_url, stream=True)
                urllib.request.urlretrieve(image_url, fullfilename) #"10001"+ "." + file_ending)

            json_file = self.create_json(file_ending, only_filename, image_description)

            return "<h1>It worked.</p>"


    def validate_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def calculate_score(self):
        print("test")

    def create_json(self, file_ending, only_filename, image_description):
        data = {}
        data['id'] = only_filename
        data['img'] = "img/" + only_filename + "." + file_endingSA
        data['label'] = 0
        data['text'] = image_description

        path = './data/'
        jsonname = 'katrin_test_seen'
        ext = '.json'
        filePathNameWExt = path + jsonname + ext

        with open(filePathNameWExt, "w+") as f:
            json.dump(data, f)

api.add_resource(Model, '/')

if __name__ == '__main__':
    app.run(debug=True)
