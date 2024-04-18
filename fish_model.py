from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model

# for TPU
# from tensorflow.distribute.cluster_resolver import TPUClusterResolver
# from tensorflow.distribute.experimental import TPUStrategy

from sklearn.metrics import confusion_matrix
import numpy as np
import matplotlib.pyplot as plt

import random
import os

import requests, io, cv2
import numpy as np
from PIL import Image


from shutil import copyfile, rmtree
from pathlib import Path


from glob import glob
import itertools
import warnings
warnings.filterwarnings("ignore")

# Test/train sizes parameters
# Takes not more than TRAIN_SAMPLE_SIZE and TEST_SAMPLE_SIZE from a given GROPPED_CLASSES_DIR

INPUT_CLASSES_DIR = r'C:\Users\johny\OneDrive\Desktop\School\Spring 2024\ECE 590\Species\Training_Set'

TRAIN_SAMPLE_SIZE = 100
TEST_SAMPLE_SIZE = 20

# list of all classes available

folders = glob(os.path.join(INPUT_CLASSES_DIR, '*'))

print([os.path.split(x)[-1] for x in folders])
print(len(folders))

# generates samples of gives sized and copies files to train/test folders

test_root = './test'
train_root = './train'

for dirname in folders:
    if len(os.listdir(dirname)) < TRAIN_SAMPLE_SIZE + TEST_SAMPLE_SIZE:
        print(f'{dirname} contains less files than needed')
        break
    else:
        # Use os.path to get the last part of the path in a cross-platform way
        current_subfolder = os.path.basename(dirname)
        
        # Correctly forming the sample glob pattern
        folder_sample = random.sample(glob(os.path.join(dirname, '*')), TRAIN_SAMPLE_SIZE + TEST_SAMPLE_SIZE)
        
        # Create directories using pathlib.Path, which handles paths correctly across OSes
        test_subfolder_path = Path(test_root) / current_subfolder
        train_subfolder_path = Path(train_root) / current_subfolder
        
        test_subfolder_path.mkdir(parents=True, exist_ok=True)
        train_subfolder_path.mkdir(parents=True, exist_ok=True)
        
        # Partition the sample into training and testing
        train_filenames = folder_sample[:TRAIN_SAMPLE_SIZE]
        test_filenames = folder_sample[TRAIN_SAMPLE_SIZE:]
        
        # Copy files
        for f in train_filenames:
            copyfile(f, train_subfolder_path / Path(f).name)
        for f in test_filenames:
            copyfile(f, test_subfolder_path / Path(f).name)


# re-size all the images to this
IMAGE_SIZE = [200, 200]

# training config:
epochs = 10
batch_size = 128

# resnet base
res = ResNet50(
input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

# don't train existing weights
for layer in res.layers:
  layer.trainable = False

# our layers - you can add more if you want
x = Flatten()(res.output)
# x = Dense(1000, activation='relu')(x) # example
prediction = Dense(len(folders), activation='softmax')(x)

# create a model object
model = Model(inputs=res.input, outputs=prediction)
# tell the model what cost and optimization method to use
model.compile(
loss='sparse_categorical_crossentropy',
optimizer='adam',
metrics=['accuracy'])

# create an instance of ImageDataGenerator
train_gen = ImageDataGenerator(
  rotation_range=20,
  width_shift_range=0.1,
  height_shift_range=0.1,
  shear_range=0.1,
  zoom_range=0.2,
  horizontal_flip=True,
  vertical_flip=True,
  preprocessing_function=preprocess_input
)

val_gen = ImageDataGenerator(
  preprocessing_function=preprocess_input
)

# get label mapping for confusion matrix plot
test_gen = val_gen.flow_from_directory(test_root, target_size=IMAGE_SIZE)
print(test_gen.class_indices)
labels = [None] * len(test_gen.class_indices)
for k, v in test_gen.class_indices.items():
  labels[v] = k


# should be a strangely colored image (due to VGG weights being BGR)
for x, y in test_gen:
  print("min:", x[0].min(), "max:", x[0].max())
  plt.title(labels[np.argmax(y[0])])
  plt.imshow(x[0])
  plt.show()
  break


# create generators
train_generator = train_gen.flow_from_directory(
  train_root,
  target_size=IMAGE_SIZE,
  shuffle=True,
  batch_size=batch_size,
  class_mode='sparse',
)
valid_generator = val_gen.flow_from_directory(
  test_root,
  target_size=IMAGE_SIZE,
  shuffle=False,
  batch_size=batch_size,
  class_mode='sparse',
)


# fit the model
r = model.fit(
  train_generator,
  validation_data=valid_generator,
  epochs=epochs,
  steps_per_epoch=len(train_files) // batch_size,
  validation_steps=len(test_files) // batch_size,
)

# You can use joblib or just use 
model.save('fish_model.h5')

labels = list(val_gen.flow_from_directory(test_root).class_indices.keys())
labels

URL = 'https://upload.wikimedia.org/wikipedia/commons/1/12/Spiny_dogfish.jpg'
response = requests.get(URL)
bytes_im = io.BytesIO(response.content)
cv_im = cv2.cvtColor(np.array(Image.open(bytes_im)), cv2.COLOR_RGB2BGR)

internal_image = cv2.resize(cv_im,IMAGE_SIZE)
internal_image = internal_image.reshape(1,IMAGE_SIZE[0], IMAGE_SIZE[1],3) 


plt.imshow(internal_image[0])

p = model.predict(internal_image)
p = np.argmax(p)
labels[p]