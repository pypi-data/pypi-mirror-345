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
    
def Segmentation():
    print("""import kagglehub
import os
# Download latest version
path = kagglehub.dataset_download("bulentsiyah/semantic-drone-dataset")

print("Path to dataset files:", path)

import cv2
os.environ["KERAS_BACKEND"] = "tensorflow"
import os
import warnings
# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import keras
import glob
import numpy as np
import skimage as ski
import tensorflow as tf
import matplotlib.pyplot as plt

image_path = os.path.join(path, 'dataset', 'semantic_drone_dataset', 'original_images')
mask_path = os.path.join(path, 'dataset', 'semantic_drone_dataset', 'label_images_semantic')

image_paths = sorted(glob.glob(os.path.join(image_path, "*.jpg")))
mask_paths = sorted(glob.glob(os.path.join(mask_path, "*.png")))

from sklearn.model_selection import train_test_split

# Split dataset into 90% train, 10% test
train_image_paths, test_image_paths, train_mask_paths, test_mask_paths = train_test_split(
    image_paths, mask_paths, test_size=0.1, random_state=42, shuffle=True)

print(f"Train size: {len(train_image_paths)}, Test size: {len(test_image_paths)}")

input_shape = (512, 512, 3)

num_classes = 24

batch_size = 8

def load_data(image_path, mask_path):
    # Loading image
    image = tf.io.read_file(image_path)
    # Decoding a JPEG-encoded image to a uint8 tensor
    image = tf.image.decode_jpeg(image, channels=3)
    # Resizing / Normalizing
    image = tf.image.resize(image, input_shape[:2]) / 255.0

    # Same for the mask (except normalizing)
    mask  = tf.io.read_file(mask_path)
    mask = tf.image.decode_png(mask, channels=1)
    mask = tf.image.resize(mask, input_shape[:2], method="nearest")

    return image, mask

def augment(image, mask):
    # Random horizontal flip
    if tf.random.uniform(()) > 0.5:
        image = tf.image.flip_left_right(image)
        mask = tf.image.flip_left_right(mask)

    # Random vertical flip
    if tf.random.uniform(()) > 0.5:
        image = tf.image.flip_up_down(image)
        mask = tf.image.flip_up_down(mask)

    # Random 90-degree rotation
    k = tf.random.uniform(shape=[], minval=0, maxval=4, dtype=tf.int32)
    image = tf.image.rot90(image, k)
    mask = tf.image.rot90(mask, k)

    return image, mask

train_dataset = tf.data.Dataset.zip((
    tf.data.Dataset.list_files(train_image_paths, shuffle=False),
    tf.data.Dataset.list_files(train_mask_paths, shuffle=False),
))

test_dataset = tf.data.Dataset.zip((
    tf.data.Dataset.list_files(test_image_paths, shuffle=False),
    tf.data.Dataset.list_files(test_mask_paths, shuffle=False),
))


# INPUT PIPELINE

train_dataset = (
    train_dataset
    .map(lambda x, y: load_data(x, y), num_parallel_calls=tf.data.AUTOTUNE)
    .map(augment, num_parallel_calls=tf.data.AUTOTUNE)
    .cache()      # Caches dataset in RAM if it fits (use small batch_size or comment out)
    .shuffle(buffer_size=1000)   # Ensures randomness
    .batch(batch_size)
    .prefetch(tf.data.AUTOTUNE)
)

test_dataset = (
    test_dataset
    .map(lambda x, y: load_data(x, y), num_parallel_calls=tf.data.AUTOTUNE)
    .cache()
    .batch(batch_size)
    .prefetch(tf.data.AUTOTUNE)
)



import matplotlib.pyplot as plt

def visualize_dataset(dataset, n=6):
    sample_images, sample_masks = next(iter(dataset.take(1)))  # Take only one batch

    fig, axes = plt.subplots(2, n, figsize=(4 * n, 10))

    for i in range(n):
        # Image
        axes[0, i].imshow(sample_images[i])
        axes[0, i].axis('off')

        # Mask
        axes[1, i].imshow(sample_masks[i])
        axes[1, i].axis('off')

    plt.tight_layout()
    plt.show()
visualize_dataset(train_dataset, n=6)

def create_unet_model():
    '''Smaller U-Net-like model with dropout'''

    inputs = keras.layers.Input(input_shape)

    # ENCODER
    c1 = keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(inputs)
    c1 = keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c1)
    p1 = keras.layers.MaxPooling2D((2, 2), strides=(2, 2))(c1)

    c2 = keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(p1)
    c2 = keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c2)
    p2 = keras.layers.MaxPooling2D((2, 2), strides=(2, 2))(c2)

    c3 = keras.layers.Conv2D(256, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(p2)
    c3 = keras.layers.Conv2D(256, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c3)
    p3 = keras.layers.MaxPooling2D((2, 2), strides=(2, 2))(c3)

    # BOTTLENECK
    c4 = keras.layers.Conv2D(512, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(p3)
    c4 = keras.layers.Conv2D(512, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c4)

    # DECODER
    u5 = keras.layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding="same")(c4)
    u5 = keras.layers.Concatenate()([u5, c3])
    u5 = keras.layers.Dropout(0.3)(u5)
    c5 = keras.layers.Conv2D(256, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(u5)
    c5 = keras.layers.Conv2D(256, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c5)

    u6 = keras.layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding="same")(c5)
    u6 = keras.layers.Concatenate()([u6, c2])
    u6 = keras.layers.Dropout(0.3)(u6)
    c6 = keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(u6)
    c6 = keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c6)

    u7 = keras.layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding="same")(c6)
    u7 = keras.layers.Concatenate()([u7, c1])
    u7 = keras.layers.Dropout(0.3)(u7)
    c7 = keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(u7)
    c7 = keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same", kernel_initializer="he_normal")(c7)

    # OUTPUT LAYER
    outputs = keras.layers.Conv2D(num_classes, (1, 1), activation="softmax")(c7)  # Multi-class segmentation

    return keras.Model(inputs, outputs, name="U-Net")

unet = create_unet_model()

unet.summary()

checkpoint_callback = keras.callbacks.ModelCheckpoint("best_unet.model.keras",
                                                      monitor="val_loss",
                                                      save_best_only=True)

# Reduces learning rate when validation loss stops improving
lr_scheduler = keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                                 factor=0.8,
                                                 patience=3,
                                                 min_lr=1e-6)

callbacks = [checkpoint_callback, lr_scheduler]



unet.compile(optimizer='adam',
             loss='sparse_categorical_crossentropy',
             metrics=["accuracy"])

unet_history = unet.fit(train_dataset,
                        validation_data=test_dataset,
                        epochs=5,
                        callbacks=callbacks)


# Loading the best weights after training has finished
unet.load_weights("best_unet.model.keras")

def plot_history(history):

    metrics = [m for m in history.history.keys() if not m.startswith("val_")]
    num_metrics = len(metrics)

    fig, axes = plt.subplots(nrows=1, ncols=num_metrics,
                             figsize=(min(5 * num_metrics, 20), 5))

    # Ensure axes is iterable, even if there's only one plot
    if num_metrics == 1:
        axes = [axes]

    for metric, ax in zip(metrics, axes):
        ax.plot(history.history[metric], label=f"Train {metric}")

        # Check if validation metric exists before plotting
        val_metric = f"val_{metric}"
        if val_metric in history.history:
            ax.plot(history.history[val_metric], label=f"Validation {metric}")

        ax.set_xlabel("Epochs")
        ax.set_ylabel(metric)
        ax.set_title(f"{metric.title()}")
        ax.legend()
        ax.grid()

    plt.tight_layout()
    plt.show()

plot_history(unet_history)

def show_predictions(model, dataset, num_samples=5):

    # Get a batch of images and masks
    sample_images, sample_masks = next(iter(dataset))
    pred_masks = model.predict(sample_images, verbose=0)

    fig, ax = plt.subplots(nrows=num_samples, ncols=3, figsize=(15, 4 * num_samples))

    for i in range(num_samples):
        single_channel_mask = np.argmax(pred_masks[i], axis=-1)  # Shape: (512, 512)

        ax[i, 0].imshow(sample_images[i])
        ax[i, 0].set_title('Original Image')

        ax[i, 1].imshow(sample_masks[i])
        ax[i, 1].set_title('Ground Truth Mask')

        ax[i, 2].imshow(single_channel_mask)
        ax[i, 2].set_title('Predicted Mask')

    plt.tight_layout()
    plt.show()

show_predictions(unet, test_dataset)

""")
    
def TransferLearning():
    print("""
    

!wget --quiet https://upload.wikimedia.org/wikipedia/commons/d/d7/Green_Sea_Turtle_grazing_seagrass.jpg
!wget --quiet https://upload.wikimedia.org/wikipedia/commons/0/0a/The_Great_Wave_off_Kanagawa.jpg

import matplotlib.pyplot as plt
import tensorflow.keras as kr
import tensorflow as tf
import numpy as np
from IPython import display
from PIL import Image

CONTENT = 'Green_Sea_Turtle_grazing_seagrass.jpg'
STYLE = 'The_Great_Wave_off_Kanagawa.jpg'

IMAGE_HEIGHT = 300
IMAGE_WIDTH = 400

content = Image.open(CONTENT)
style = Image.open(STYLE)

plt.figure(figsize=(10, 10))

plt.subplot(1, 2, 1)
plt.imshow(content)
plt.title('Content Image')

plt.subplot(1, 2, 2)
plt.imshow(style)
plt.title('Style Image')

plt.tight_layout()
plt.show()

def img_parser(filename):
    img_string = tf.io.read_file(filename)
    img = tf.image.decode_jpeg(img_string, channels=3)
    img = tf.cast(img, dtype=tf.float32)

    # Resize the image using tf.image.resize instead of tf.image.resize_images
    img = tf.image.resize(img, size=(IMAGE_HEIGHT, IMAGE_WIDTH))
    img = tf.expand_dims(img, axis=0)   # Add batch dimension
    return img

def load_image(filename):
    img = img_parser(filename)
    img = kr.applications.vgg19.preprocess_input(img)
    return img

def deprocess_img(processed_img):
    x = processed_img.copy()
    if len(x.shape) == 4:
        x = np.squeeze(x, 0)
    assert len(x.shape) == 3, ("Input to deprocess image must be an image of "
                             "dimension [1, height, width, channel] or [height, width, channel]")
    if len(x.shape) != 3:
        raise ValueError("Invalid input to deprocessing image")

    # perform the inverse of the preprocessing step
    x[:, :, 0] += 103.939
    x[:, :, 1] += 116.779
    x[:, :, 2] += 123.68
    x = x[:, :, ::-1]  # Convert back to RGB from BGR

    x = np.clip(x, 0, 255).astype('uint8')
    return x

_vgg = kr.applications.vgg19.VGG19(include_top=False,
                                   weights=None,
                                   input_shape=(IMAGE_HEIGHT, IMAGE_WIDTH, 3))
_vgg.summary()

# Content layer where will pull our feature maps
content_layers = ['block5_conv2']

# Style layers
style_layers = ['block1_conv1',
                'block2_conv1',
                'block3_conv1',
                'block4_conv1',
                'block5_conv1']

def get_model(styles, contents):

    vgg = kr.applications.vgg19.VGG19(include_top=False,
                                      weights='imagenet',
                                      input_shape=(IMAGE_HEIGHT, IMAGE_WIDTH, 3))
    vgg.trainable = False

    # Get output layers corresponding to style and content layers
    style_outputs = [vgg.get_layer(layer_name).output for layer_name in styles]
    content_outputs = [vgg.get_layer(layer_name).output for layer_name in contents]
    model_outputs = style_outputs + content_outputs

    return kr.Model(vgg.input, model_outputs)

def get_content_loss(content, generated):
    return tf.reduce_mean(tf.square(content - generated))

def get_layer_style_loss(style, generated):
    def gram_matrix(tensor):
        channels = int(tensor.shape[-1])
        a = tf.reshape(tensor, [-1, channels])
        gram = tf.matmul(a, a, transpose_a=True)
        return gram / tf.cast(tf.shape(a)[0], tf.float32)

    gram_style = gram_matrix(style)
    gram_generated = gram_matrix(generated)
    return tf.reduce_mean(tf.square(gram_style - gram_generated))


def get_style_loss(style, generated):
    loss = 0
    coeffs = [0.2, 0.2, 0.2, 0.2, 0.2]
    for s, g, coeff in zip(style, generated, coeffs):
        loss += coeff * get_layer_style_loss(s, g)

    return loss

def compute_loss(model, image, style_features, content_features, alpha=0.1, beta=0.002):

    # Feed our init image through our model.
    model_outputs = model(image)

    content_generated = [content_layer[0] for content_layer in model_outputs[len(style_layers):]][0]
    style_generated = [style_layer for style_layer in model_outputs[:len(style_layers)]]

    content_loss = alpha * get_content_loss(content_features, content_generated)
    style_loss = beta * get_style_loss(style_features, style_generated)

    # Get total loss
    loss = style_loss + content_loss
    return loss

def compute_grads(cfg):
    with tf.GradientTape() as tape:
        loss = compute_loss(**cfg)
    # Compute gradients with respect to input image
    return tape.gradient(loss, cfg['image']), loss

def transfer_style(content_img, style_img, epochs=1000):
    def generate_noisy_image(content_image, noise_ratio):

        noise_image = tf.random.uniform([1, IMAGE_HEIGHT, IMAGE_WIDTH, 3], minval=-20, maxval=20)
        input_image = noise_image * noise_ratio + content_image * (1 - noise_ratio)
        return input_image

    # We don't want to train any layers of our model
    model = get_model(style_layers, content_layers)
    for layer in model.layers:
        layer.trainable = False

    S = load_image(style_img)
    C = load_image(content_img)

    style_outputs = model(S)
    content_outputs = model(C)

    # Get the style and content feature representations (from our specified intermediate layers)
    _content = [content_layer[0] for content_layer in content_outputs[len(style_layers):]][0]
    _style = [style_layer[0] for style_layer in style_outputs[:len(style_layers)]]

    # Set initial image
    G = generate_noisy_image(C, 0.6)
    # Replace tf.contrib.eager.Variable with tf.Variable
    G = tf.Variable(G, dtype=tf.float32)

    best_loss, best_img = float('inf'), None

    # Create a nice config
    cfg = {
        'model': model,
        'image': G,
        'style_features': _style,
        'content_features': _content
    }

    # Create our optimizer
    opt = tf.compat.v1.train.AdamOptimizer(learning_rate=2, beta1=0.99, epsilon=1e-1) # Use tf.compat.v1.train.AdamOptimizer

    # For displaying
    display_interval = epochs/(2*5)

    norm_means = np.array([103.939, 116.779, 123.68])
    min_vals = -norm_means
    max_vals = 255 - norm_means

    imgs = []
    for i in range(epochs):
        grads, cost = compute_grads(cfg)
        opt.apply_gradients([(grads, G)])
        clipped = tf.clip_by_value(G, min_vals, max_vals)
        G.assign(clipped)

        if cost < best_loss:
            best_loss = cost
            best_img = deprocess_img(G.numpy())

        if i % display_interval== 0:
            plot_img = G.numpy()
            plot_img = deprocess_img(plot_img)
            imgs.append(plot_img)
            display.clear_output(wait=True)
            display.display_png(Image.fromarray(plot_img))
            print('Epoch: {}, LOSS: {:.4e}'.format(i, cost))


    display.clear_output(wait=True)
    plt.figure(figsize=(14,4))
    for i,img in enumerate(imgs):
        plt.subplot(2, 5, i+1)
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])

    return best_img, best_loss

best, best_loss = transfer_style(CONTENT, STYLE, epochs=50)

plt.figure(figsize=(10, 10))
content = Image.open(CONTENT)
style = Image.open(STYLE)

plt.subplot(1, 2, 1)
plt.imshow(content)
plt.title('Content Image')

plt.subplot(1, 2, 2)
plt.imshow(style)
plt.title('Style Image')

plt.figure(figsize=(10, 10))

plt.imshow(best)
plt.title('Output Image')
plt.show()

""")
    
def GAN():
    print("""import kagglehub

# Download latest version
path = kagglehub.dataset_download("jessicali9530/celeba-dataset")

print("Path to dataset files:", path)

import numpy as np
import matplotlib.pyplot as plt
import os
import time
import imageio
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers import Flatten
from keras.layers import Conv2D
from keras.layers import Conv2DTranspose
from keras.layers import LeakyReLU
from keras.layers import Dropout
from keras.preprocessing.image import array_to_img, img_to_array, load_img
from numpy.random import randn
from numpy.random import randint
import tensorflow as tf

n_images = 12000
batch_size = 128
latent_dim = 100
n_epoch = 5
img_shape = (128, 128, 3)

data_dir = path+'/img_align_celeba/img_align_celeba/'
images = os.listdir(data_dir)
images = images[:n_images]

plt.figure(figsize=(10,10))
for i, name in enumerate(images[:16]):
    plt.subplot(4, 4, i + 1)
    img = plt.imread(data_dir + '/' + name)
    plt.imshow(img)
    plt.title(name)
    plt.axis('off')

def get_data(data_path) :
    X = []
    for filename in data_path :
        img = img_to_array(load_img(data_dir + "/" + filename, target_size = img_shape[:2]))
        X.append(img)
    X = np.array(X).astype('float32')
    #X = (X - 127.5) / 127.5
    X = X / 255
    return X

dataset = get_data(images)

def define_discriminator(in_shape=(128,128,3)):
    model = Sequential()
    # normal
    model.add(Conv2D(128, (5,5), padding='same', input_shape=in_shape))
    model.add(LeakyReLU(alpha=0.2))
    # downsample to 64x64
    model.add(Conv2D(128, (5,5), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # downsample to 32x32
    model.add(Conv2D(128, (5,5), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # downsample to 16x16
    model.add(Conv2D(128, (5,5), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # downsample to 8x8
    model.add(Conv2D(128, (5,5), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # classifier
    model.add(Flatten())
    model.add(Dropout(0.4))
    model.add(Dense(1, activation='sigmoid'))
    # compile model
    # Change 'lr' to 'learning_rate'
    opt = Adam(learning_rate=0.0002, beta_1=0.5)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model

def define_generator(latent_dim):
    model = Sequential()
    # foundation for 8x8 feature maps
    n_nodes = 128 * 8 * 8
    model.add(Dense(n_nodes, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Reshape((8, 8, 128)))
    # upsample to 16x16
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # upsample to 32x32
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # upsample to 64x64
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # upsample to 128x128
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    # output layer 128x128x3
    model.add(Conv2D(3, (5,5), activation='tanh', padding='same'))
    return model

#input of G
def generate_latent_points(latent_dim, n_samples):
    # generate points in the latent space
    x_input = randn(latent_dim * n_samples)
    # reshape into a batch of inputs for the network
    x_input = x_input.reshape(n_samples, latent_dim)
    return x_input

# use the generator to generate n fake examples, with class labels
def generate_fake_samples(g_model, latent_dim, n_samples):
    # generate points in latent space
    x_input = generate_latent_points(latent_dim, n_samples)
    # predict outputs
    X = g_model.predict(x_input)
    # create 'fake' class labels (0)
    y = np.zeros((n_samples, 1))
    return X, y

def define_gan(g_model, d_model):
    # make weights in the discriminator not trainable
    d_model.trainable = False
    # connect them
    model = Sequential()
    # add generator
    model.add(g_model)
    # add the discriminator
    model.add(d_model)
    # compile model
    # Changed 'lr' to 'learning_rate'
    opt = Adam(learning_rate=0.0002, beta_1=0.5)
    model.compile(loss='binary_crossentropy', optimizer=opt)
    return model

# retrive real samples
def get_real_samples(dataset, n_samples):
    # choose random instances
    ix = randint(0, dataset.shape[0], n_samples)
    # retrieve selected images
    X = dataset[ix]
    # set 'real' class labels (1)
    y = np.ones((n_samples, 1))
    return X, y

# create and save a plot of generated images
def show_generated(generated,epoch, n=5):
    #[-1,1] -> [0,1]
    #generated = (generated + 1)/ 2
    #generated = (generated[:n*n] * 127.5) + 127.5
    #generated = generated * 255
    plt.figure(figsize=(10,10))
    for i in range(n * n):
        plt.subplot(n, n, i + 1)
        #img = plt.imread(data_dir + '/' + name)
        plt.imshow(generated[i])
        #plt.title(name)
        plt.axis('off')
    plt.savefig('image_at_epoch_{:04d}.png'.format(epoch+1))
    plt.show()

# evaluate the discriminator and plot generated images
def summarize_performance(epoch, g_model, d_model, dataset, latent_dim, n_samples=100):
    # prepare real samples
    X_real, y_real = get_real_samples(dataset, n_samples)
    # evaluate discriminator on real examples
    _, acc_real = d_model.evaluate(X_real, y_real, verbose=0)
    # prepare fake examples
    x_fake, y_fake = generate_fake_samples(g_model, latent_dim, n_samples)
    # evaluate discriminator on fake examples
    _, acc_fake = d_model.evaluate(x_fake, y_fake, verbose=0)
    # summarize discriminator performance
    print('>Accuracy [real: %.0f%%, fake: %.0f%%]' % (acc_real*100, acc_fake*100))
    # show plot
    show_generated(x_fake, epoch)

def train(g_model, d_model, gan_model, dataset, latent_dim=100, n_epochs=100, n_batch=128):
    bat_per_epo = int(dataset.shape[0] / n_batch)
    half_batch = int(n_batch / 2)
    # manually enumerate epochs
    start = time.time()
    for i in range(n_epochs):

        # enumerate batches over the training set
        for j in range(bat_per_epo):
            # get randomly selected 'real' samples
            X_real, y_real = get_real_samples(dataset, half_batch)
            # update discriminator model weights
            d_loss1, _ = d_model.train_on_batch(X_real, y_real)
            # generate 'fake' examples
            X_fake, y_fake = generate_fake_samples(g_model, latent_dim, half_batch)
            # update discriminator model weights
            d_loss2, _ = d_model.train_on_batch(X_fake, y_fake)
            # prepare points in latent space as input for the generator
            X_gan = generate_latent_points(latent_dim, n_batch)
            # create inverted labels for the fake samples
            y_gan = np.ones((n_batch, 1))
            # update the generator via the discriminator's error
            g_loss = gan_model.train_on_batch(X_gan, y_gan)
            # summarize loss on this batch
        print('Epoch: %d,  Loss: D_real = %.3f, D_fake = %.3f,  G = %.3f' %   (i+1, d_loss1, d_loss2, g_loss))
        # evaluate the model performance and show generated images every epoch
        # Show generated images every epoch
        summarize_performance(i, g_model, d_model, dataset, latent_dim)
    print ('Total time for training {} epochs is {} sec'.format(n_epochs, (time.time()-start)))

discriminator = define_discriminator()
generator = define_generator(latent_dim)

# create the gan
gan = define_gan(generator, discriminator)

# train model
train(generator, discriminator, gan, dataset, latent_dim, n_epoch, batch_size)

n_iter = int(n_epoch / 10) # change from -1 to  to avoid n_iter to be 0, otherwise it won't execute the loop
# or
n_iter = int(n_epoch) # if you want to generate gif for each epoch
# or any number greater than 0
for e in range(n_iter):
    img_name = '/content/image_at_epoch_{:04d}.png'.format((e+1)*1)
    print(img_name)
    #check if the file exists before reading it.
    if os.path.exists(img_name):
        files.append(imageio.imread(img_name))
    else:
        print(f"Warning: Image file not found: {img_name}")
imageio.mimsave('dcgan_celebA_generation_animation.gif', files, fps=5)

""")