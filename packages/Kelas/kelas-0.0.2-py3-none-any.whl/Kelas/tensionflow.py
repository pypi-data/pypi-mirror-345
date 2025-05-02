def HTML():
    print("!jupyter nbconvert --to html [path]")

def Classification():
    print("""import kagglehub

# Download latest version
path = kagglehub.dataset_download("kmkarakaya/logos-bk-kfc-mcdonald-starbucks-subway-none")

print("Path to dataset files:", path)

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import tensorflow as tf # Import TensorFlow
from tensorflow import keras # Import Keras from TensorFlow
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator # Import ImageDataGenerator from the correct path
#from tensorflow.keras.layers.normalization import BatchNormalization
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.applications.inception_v3 import decode_predictions
from sklearn.metrics import confusion_matrix
from sklearn.metrics import average_precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from tensorflow.keras.models import model_from_json # Import model_from_json from the correct path
import itertools
import matplotlib.pyplot as plt
import time
import pandas as pd
import os
# %matplotlib inline

print(os.listdir(path))

train_path = path + '/logos3/train'
test_path = path + '/logos3/test'

os.listdir(train_path)

train_datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        fill_mode='nearest',
    validation_split=0.2)

selectedClasses = os.listdir(train_path)

batchSize = 32
train_generator = train_datagen.flow_from_directory(
    train_path,
    target_size=(224, 224),
    batch_size=batchSize,
    classes=selectedClasses,
    subset='training') # set as training data

validation_generator = train_datagen.flow_from_directory(
    train_path, # same directory as training data
    target_size=(224, 224),
    batch_size=batchSize,
    classes=selectedClasses,
    subset='validation') # set as validation data

test_generator = ImageDataGenerator().flow_from_directory(
    test_path,
    target_size=(224,224),
    classes=selectedClasses,
    shuffle= False,
    batch_size = batchSize)

print ("In train_generator ")
for cls in range(len (train_generator.class_indices)):
    print(selectedClasses[cls],":\t",list(train_generator.classes).count(cls))
print ("")

def plots(ims, figsize = (22,22), rows=4, interp=False, titles=None, maxNum = 9):
    if type(ims[0] is np.ndarray):
        ims = np.array(ims).astype(np.uint8)
        if(ims.shape[-1] != 3):
            ims = ims.transpose((0,2,3,1))

    f = plt.figure(figsize=figsize)
    #cols = len(ims) //rows if len(ims) % 2 == 0 else len(ims)//rows + 1
    cols = maxNum // rows if maxNum % 2 == 0 else maxNum//rows + 1
    #for i in range(len(ims)):
    for i in range(maxNum):
        sp = f.add_subplot(rows, cols, i+1)
        sp.axis('Off')
        if titles is not None:
            sp.set_title(titles[i], fontsize=20)
        plt.imshow(ims[i], interpolation = None if interp else 'none')

train_generator.reset()
imgs, labels = next(train_generator)
labelNames=[]
labelIndices=[np.where(r==1)[0][0] for r in labels]
#print(labelIndices)

for ind in labelIndices:
    for labelName,labelIndex in train_generator.class_indices.items():
        if labelIndex == ind:
            #print (labelName)
            labelNames.append(labelName)
plots(imgs, rows=4, titles = labelNames, maxNum=8)

base_model = InceptionV3(weights='imagenet',
                                include_top=False,
                                input_shape=(224, 224,3))
base_model.trainable = False
x = base_model.output
x = keras.layers.GlobalAveragePooling2D()(x)
# let's add a fully-connected layer
x = Dropout(0.5)(x)
# and a sofymax/logistic layer -- we have 6 classes
predictions = Dense(len(selectedClasses), activation='softmax')(x)
# this is the model we will train
model = Model(base_model.input,predictions)
display(model.summary())

modelName= "Q1"
#save the best weights over the same file with the model name

#filepath="checkpoints/"+modelName+"_bestweights.hdf5"
filepath=modelName+"_bestweights.keras"
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint]

model.compile(Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

stepsPerEpoch= (train_generator.samples+ (batchSize-1)) // batchSize
print("stepsPerEpoch: ", stepsPerEpoch)

validationSteps=(validation_generator.samples+ (batchSize-1)) // batchSize
print("validationSteps: ", validationSteps)

train_generator.reset()
validation_generator.reset()

# Fit the model
history = model.fit(
    train_generator,
    validation_data = validation_generator,
    epochs = 10,
    steps_per_epoch = stepsPerEpoch,
    validation_steps= validationSteps,
    callbacks=callbacks_list,
    verbose=1)

print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'Validation'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

testStep = (test_generator.samples + (batchSize-1)) // batchSize
predictions = model.predict(test_generator, steps = testStep ,  verbose = 1)
len(predictions)

predicted_class_indices=np.argmax(predictions,axis=1)
print(predicted_class_indices)
len(predicted_class_indices)
labels = (test_generator.class_indices)
print(labels)

# prompt: map labels and predicted_class_indices

labels = dict((v,k) for k,v in test_generator.class_indices.items())
predictions = [labels[k] for k in predicted_class_indices]
len(predictions)

actualLables= [labels[k] for k in test_generator.classes]
print(actualLables)
len(actualLables)

accuracy_score(actualLables, predictions)

""")
    
def Yolo():
    print("""import kagglehub
import os
# Download latest version
path = kagglehub.dataset_download("taranmarley/sptire")

print("Path to dataset files:", path)
print(os.listdir(path))

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from matplotlib import pyplot as plt
import cv2 as cv

import torch
print(f"Setup complete. Using torch {torch.__version__} ({torch.cuda.get_device_properties(0).name if torch.cuda.is_available() else 'CPU'})")

fig,ax = plt.subplots(1,4,figsize=(10,5))
image = cv.imread(path+"/train/images/14_19_l_jpg.rf.8323d9f848377e32ca451017a3a80731.jpg")
ax[0].imshow(image)
image = cv.imread(path+"/train/images/IMG_0719_JPEG.rf.05f197445c4a42854e0b1f308fb4e636.jpg")
ax[1].imshow(image)
image = cv.imread(path+"/train/images/IMG_0680_JPEG.rf.560c49e01182db8356989ddc604557fb.jpg")
ax[2].imshow(image)
image = cv.imread(path+"/train/images/IMG_0701_JPEG.rf.d5ae66ab383142ef5d59b0454a19fdce.jpg")
ax[3].imshow(image)
fig.show()

!git clone https://github.com/WongKinYiu/yolov7 # clone repo

import yaml

data_yaml = dict(
    train = path+'/train',
    val = path+'/valid',
    nc = 1,
    names = ['Tire']
)

# Note that I am creating the file in the yolov5/data/ directory.
with open('data.yaml', 'w') as outfile:
    yaml.dump(data_yaml, outfile, default_flow_style=True)

from ultralytics import YOLO
model = YOLO('/content/yolo11s.pt')
model.train(data='/content/data.yaml',imgsz = 640,batch = 8, epochs = 5 , workers = 0)

img = cv.imread("/content/runs/detect/train2/train_batch0.jpg")
plt.figure(figsize=(15, 15))
plt.imshow(img)

model.predict(source= path +"/test/images/IMG_0672_JPEG.rf.c37833de9c2310cfba797a83f239d3c1.jpg",save=True)

img = cv.imread("/content/runs/detect/train4/results.png")
plt.figure(figsize=(15, 15))
plt.imshow(img)

""")