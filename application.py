from flask import Flask
from flask import render_template,request, Response
import graphlab as gl
import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError
from scipy.misc import imread
import string
import random
from collections import OrderedDict

app = Flask(__name__)

cloth_classifier = gl.load_model("logit_classifier")
color_classifier = gl.load_model("logit_color_classifier")
pretrained_model = gl.load_model("deep_neural_network")

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def downloadImages(urls, path):
    size = 256,256
    if not os.path.exists(path):
        os.makedirs(path)
    for url in urls:
        try:
            image_r = requests.get(url)
            print "Downloaded %s" % url
        except ConnectionError, e:
            print 'could not download %s' % url
            continue
        file = open(os.path.join(path, '%s.jpg') % url[-12:].replace("/",""), 'w')
        try:
            img = Image.open(StringIO(image_r.content))
            img.thumbnail(size, Image.ANTIALIAS)
            Image.open(StringIO(image_r.content)).save(file, 'JPEG')
            imread(file.name)
        except IOError, e:
            os.remove(file.name)
            continue
        finally:
            file.close()

@app.route('/')
@app.route('/projects/tag-that-apparel/')
def hello():
    return render_template('home.html')


@app.route('/geturl', methods=['POST'])
def processImage():
    # url = request.args.get('url', '')
    url = request.form['url']
    path = id_generator()
    path = "data/" + path
    downloadImages([url], path)
    testImages = gl.image_analysis.load_images(path, random_order=False, with_path=False)
    images_resized_test = gl.SFrame()
    images_resized_test['image'] = gl.image_analysis.resize(testImages['image'], 256, 256, 3)
    images_resized_test['extracted_features'] = pretrained_model.extract_features(images_resized_test)
    pred1 = cloth_classifier.predict_topk(images_resized_test, k = 3)
    pred2 = color_classifier.predict_topk(images_resized_test, k = 3)

    cloth_type = {}
    for row in pred1.to_numpy():
        cloth_type[row[1]]= row[2]
    cloth_type = OrderedDict(sorted(cloth_type.items(), key=lambda x: x[1], reverse = True))

    color = {}
    for row in pred2.to_numpy():
        color[row[1]]= row[2]
    color = OrderedDict(sorted(color.items(), key=lambda x: x[1], reverse = True))
    # print color

    return json.dumps([cloth_type, color])

@app.route('/test')
def test():
    sample = '[{"skirt": "0.956359278837", "shorts": "0.0275911249023", "jeans-trousers": "0.0113845640521"}, {"teal": "0.665154639864", "blue": "0.308704102764", "green": "0.0147550139986"}]'
    return sample

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port = 8000)
