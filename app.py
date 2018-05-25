from flask             import Flask, render_template, jsonify, request, Response
from PIL               import Image, ImageOps 
from io                import BytesIO
from sklearn.externals import joblib
import pickle
import json
import pickle
import numpy as np
import requests

namemap = [
    'axes',
    'boots',
    'carabiners',
    'crampons',
    'gloves',
    'hardshell_jackets',
    'harnesses',
    'helmets',
    'insulated_jackets',
    'pulleys',
    'rope',
    'tents'
]
app = Flask(__name__)

def resize(image):
    base = 128
    width, height = image.size

    if width > height:
        wpercent = base/float(width)
        hsize = int((float(height) * float(wpercent)))
        image = image.resize((base,hsize), Image.ANTIALIAS)
    else:
        hpercent = base/float(height)
        wsize = int((float(width) * float(hpercent)))
        image = image.resize((wsize, base), Image.ANTIALIAS)

    newImage = Image.new('RGB',
                     (base, base),     # A4 at 72dpi
                     (255, 255, 255))  # White

    position = (int( (base/2 - image.width/2) ), 0)
    newImage.paste(image, position)

    return newImage

def normalize(arr):
    """
    Linear normalization
    http://en.wikipedia.org/wiki/Normalization_%28image_processing%29
    """
    arr = arr.astype('float')
    
    # Do not touch the alpha channel
    for i in range(3):
        minval = arr[...,i].min()
        maxval = arr[...,i].max()
        if minval != maxval:
            arr[...,i] -= minval
            arr[...,i] *= (255.0/(maxval-minval))

    return arr

def processImage(image):
    """
    Resize and normalize the image
    """

    image   = resize(image)
    arr     = np.array(image)
    new_img = Image.fromarray(normalize(arr).astype('uint8'),'RGB')
    
    return new_img


@app.route('/classify', methods=['POST'])
def classify():
    """
    Make a POST to this endpint and pass in an URL to an image in the body of the request
    """
    try:
        body    = request.get_json()
        print(body)
        img_url = body["url"]

        # Get the image and show it
        response = requests.get(img_url)
        img      = Image.open(BytesIO(response.content))
        prcedImg = processImage(img)

        imgFeatures = np.array(prcedImg).ravel().reshape(1,-1)
        print(imgFeatures)

        model   = joblib.load('pickle_model.pkl')
        predict = model.predict(imgFeatures)
        print('The image is a ', namemap[int(predict[0])]),
        
        print('image: ', namemap[int(predict[0])], predict)

        response = json.dumps({"classification": namemap[int(predict[0])]})

        return(response)
        
    except Exception as e:
        print(e)
        raise 

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')




