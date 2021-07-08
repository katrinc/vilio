from flask import Flask
from flask import request
from flask import jsonify
import flask
from flask_restful import Resource, Api, reqparse
import requests  # to get image from the web
import shutil  # to save it locally
import os
import urllib
import urllib.request
import json
import subprocess  # to use subprocess
import glob
from waitress import serve
from functools import wraps

app = Flask(__name__)
api = Api(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = './data/img'


class Model(Resource):

    def post(self):
        print("post start")
        src_dir = os.getcwd()
        dest_dir = src_dir + "/img"
        image_url = request.form['image']
        print(image_url)
        image_description = request.form['image_description']
        if not image_url:
            raise APIImageError('No matching image file found (.jpg .jpeg. png .gif)')
        else:
            filename = image_url.split("/")[-1]
            fullfilename = os.path.join(UPLOAD_FOLDER, filename)
            file_ending = image_url.split(".")[-1]
            only_filename = filename.split(".")[0]
            if self.validate_file(filename):
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'none',
                           'Accept-Language': 'en-US,en;q=0.8',
                           'Connection': 'keep-alive'}
                request_ = urllib.request.Request(
                    image_url, None, headers)  # The assembled request
                response = urllib.request.urlopen(
                    request_)  # store the response

                # save image for inference
                new_filename = "10002" + "." + file_ending
                f = open('data/img/' + new_filename, 'wb')
                rep = response.read()
                f.write(rep)
                f.close()

                #  save image for feature extraction
                new_filename2 = "10002" + "." + file_ending
                f = open('py-bottom-up-attention/data/img/' +
                         new_filename2, 'wb')
                f.write(rep)
                f.close()

            json_file = self.create_json(
                file_ending, only_filename, image_description)
            self.extract_features()
            score = self.calculate_score()
            score_float = float(score)
            print(score_float)
            hate_value = self.calculate_hate(score_float)
            data = {'result': hate_value}
            self.clean_up()
            return data

    def validate_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def calculate_score(self):
        p1 = subprocess.Popen(['python', 'model_inference.py', '--seed', '129', '--model', 'U', '--test', 'testset',
                             '--lr', '1e-5', '--batchSize', '8', '--tr', 'bert-large-cased', '--epochs', '5',
                                     '--tsv', '--num_features', '36', '--num_pos', '6', '--loadfin', './kaggle/input/viliou36/LASTtraindev.pth', '--exp', 'U36'], stdout=subprocess.PIPE)
        p_status = p1.wait()
        result = p1.communicate()[0]
        string_result = result.split()
        return string_result[-1].decode('UTF-8')

    def create_json(self, file_ending, only_filename, image_description):
        data = {}
        data['id'] = 10002
        data['img'] = "img/" + "10002" + "." + file_ending
        data['label'] = 1 # means hateful
        data['text'] = image_description

        path = 'data/'
        jsonname = 'testset'
        ext = '.json'
        filePathNameWExt = path + jsonname + ext

        with open(filePathNameWExt, "w") as f:
            f.seek(0)
            json.dump(data, f)

    def extract_features(self):
        p = subprocess.Popen(['python', 'detectron2_mscoco_proposal_maxnms.py', '--batchsize', '1', '--split', 'img', '--weight', 'vgattr', '--minboxes', '36', '--maxboxes', '36'],cwd="/home/3caragiu/infhome/projekt_2021/vilio/py-bottom-up-attention/")
        #This makes the wait possible
        p_status = p.wait()
        shutil.move("/home/3caragiu/infhome/projekt_2021/vilio/py-bottom-up-attention/data/hm_vgattr3636.tsv","/home/3caragiu/infhome/projekt_2021/vilio/data/HM_img.tsv")
    def calculate_hate(self, prob):
        if(prob <= -0.75):
            return 1
        else:
            return 0

    def clean_up(self):
        files = glob.glob('data/img/*')
        for f in files:
            os.remove(f)
        files0 = glob.glob('data/HM_img.tsv')
        for f0 in files0:
            os.remove(f0)
        files2 = glob.glob('/home/3caragiu/infhome/projekt_2021/vilio/py-bottom-up-attention/data/img/*')
        for f2 in files2:
            os.remove(f2)

class APIImageError(Exception):
    code = 403
    description = "Image Handling Error"

api.add_resource(Model, '/')

if __name__ == '__main__':
   # serve(app)#, host='0.0.0.0', port=12200, url_scheme='http')
    app.run()#(host='0.0.0.0', port=8000)


