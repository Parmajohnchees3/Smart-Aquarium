from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import cv2
import psycopg2
import io
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model



app = Flask(__name__)
CORS(app, origins=["https://localhost:3000", "*"]) 

# load the model
model = load_model('fish_model.h5')

IMAGE_SIZE = [200, 200]


# names of all fish trained in model using scientific names
labels = [
 'Anthias anthias',
 'Atherinomorus lacunosus',
 'Belone belone',
 'Boops boops',
 'Chlorophthalmus agassizi',
 'Coris julis',
 'Dasyatis centroura',
 'Epinephelus caninus',
 'Gobius niger',
 'Mugil cephalus',
 'Phycis phycis',
 'Polyprion americanus',
 'Pseudocaranx dentex',
 'Rhinobatos cemiculus',
 'Scomber japonicus',
 'Solea solea',
 'Squalus acanthias',
 'Tetrapturus belone',
 'Trachinus draco',
 'Trigloporus lastoviza']


# dictionary of dictionaries for each fish and their respective pH, temperature, and common names (cn)
fish_ranges = {
    'Anthias anthias': {'pH' : [8.1, 8.4], 'temp' : [22,26], 'cn' : 'Swallowtail Seaperch'},
    'Atherinomorus lacunosus': {'pH' : [6, 7.5], 'temp' : [17.5,28], 'cn' : 'Hardyhead Silverside'},
    'Belone belone': {'pH' : [6.5, 7], 'temp' : [15.5,24], 'cn' : 'Garfish'},
    'Boops boops': {'pH' : [5, 7.5], 'temp' : [14,20], 'cn' : 'Bogue'},
    'Chlorophthalmus agassizi': {'pH' : [7, 8], 'temp' : [16,25], 'cn' : 'Shortnose Greeneye'},
    'Coris julis': {'pH' : [6.5, 7.5], 'temp' : [25,28], 'cn' : 'African Rainbow Wrasee'},
    'Dasyatis centroura': {'pH' : [5.5, 8.4], 'temp' : [13,18], 'cn' : 'Roughtail Stingray'},
    'Epinephelus caninus': {'pH' : [6.3, 8.5], 'temp' : [20,25], 'cn' : 'Dogtooth Grouper'},
    'Gobius niger': {'pH' : [6, 8], 'temp' : [23,26], 'cn' : 'Black Goby'},
    'Mugil cephalus': {'pH' : [7.5, 8.5], 'temp' : [21,25], 'cn' : 'Flathead Grey Mullet'},
    'Phycis phycis': {'pH' : [6.3, 8.4], 'temp' : [17,28], 'cn' : 'Lesser Forkbeard'},
    'Polyprion americanus': {'pH' : [7.2, 8.4], 'temp' : [13,15], 'cn' : 'Atlantic Wreckfish'},
    'Pseudocaranx dentex': {'pH' : [5.2, 7.5], 'temp' : [18,28], 'cn' : 'White Trevally'},
    'Rhinobatos cemiculus': {'pH' : [4, 5.5], 'temp' : [24.5,29], 'cn' : 'Blackchin Guitarfish'},
    'Scomber japonicus': {'pH' : [7.1, 8.4], 'temp' : [26,30], 'cn' : 'Chub Mackerel'},
    'Solea solea': {'pH' : [8.1, 8.4], 'temp' : [15.5,20.5], 'cn' : 'Common Sole'},
    'Squalus acanthias': {'pH' : [6.4, 8], 'temp' : [18.4,25.4], 'cn' : 'Spiny Dogfish'},
    'Tetrapturus belone': {'pH' : [7.1, 8], 'temp' : [21,27], 'cn' : 'Mediterranean Spearfish'},
    'Trachinus draco': {'pH' : [5.4, 7.8], 'temp' : [16.5,22.5], 'cn' : 'Greater Weever'},
    'Trigloporus lastoviza': {'pH' : [6.7, 7.9], 'temp' : [20.5,28.5], 'cn' : 'Streaked Gurnard'}
}

# function to receive fish image from frontend
@app.route('/', methods=['POST'])
def process_image():
    # Check if an image was uploaded
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files.get('file')
    if file.filename == '':
        return jsonify({"message": "No file selected for uploading"}), 400

    # call functions below to get prediction, check if fish can live in tank conditions, and get common name
    img_bytes = file.read()
    prediction = fish_determine(img_bytes)

    readings = pull_data()
    can_live = check_tank_conditions(prediction)
    common_name = get_fish_common_name(prediction)
    
    return jsonify({"prediction": prediction, "can_live" : can_live, "common_name" : common_name, "readings" : readings}), 200
    
# function to check whether fish is recognized and determines if fish species can survive in conditions
def fish_determine(image_bytes):
    try:
        pillow_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        cv_im = cv2.cvtColor(np.array(pillow_img), cv2.COLOR_RGB2BGR)
        internal_image = cv2.resize(cv_im, IMAGE_SIZE)
        internal_image = internal_image.reshape(1, IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
        p = model.predict(internal_image)
        p = np.argmax(p)
        return labels[p]
    except Exception as e:
        return str(e)

# pull data from flask server using GET request
def pull_data():   
    response = requests.get('http://18.221.200.217:5000/pull_data')
    if response.status_code == 200:
        data = response.json()  
        print(data)
    else:
        print("Failed to retrieve data")

# function to check if fish can survive in tank conditions
def check_tank_conditions(prediction):
    tank_readings = pull_data()
    temp, pH = tank_readings[0], tank_readings[1]
    for fish in fish_ranges:
        if prediction == fish:
            # check if pH and temperature are within the fish's range
            if fish_ranges[fish]['temp'][0] <= temp <= fish_ranges[fish]['temp'][1] and fish_ranges[fish]['pH'][0] <= pH <= fish_ranges[fish]['pH'][1]:
                return True
            else:
                return False
            
# function to get common name of fish based on their scientific name 
def get_fish_common_name(prediction):
    for fish in fish_ranges:
        if prediction == fish:
            name = fish_ranges[fish]['cn']

    return name




if __name__ == '__main__':
    app.run(debug=True)