from tflite_runtime.interpreter import Interpreter 
from PIL import Image
import numpy as np
import time
import os, sys 
import paho.mqtt.publish as publish

def load_labels(path): # Read the labels from the text file as a Python list.
  with open(path, 'r') as f:
    return [line.strip() for i, line in enumerate(f.readlines())]

def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  scale, zero_point = output_details['quantization']
  output = scale * (output - zero_point)
  ordered = np.argpartition(-output, 1)
  return [(i, output[i]) for i in ordered[:top_k]][0]


#data_folder = "/home/pi/TFLite_MobileNet/"
data_folder = "./Sample_TFLite_model/"

#  model_path = data_folder + "mobilenet_v1_1.0_224_quant.tflite"
# label_path = data_folder + "labels_mobilenet_quant_v1_224.txt"

# data_folder = "Sample_TFLite_model/"

model_path = data_folder + "good_bad_0622_mbn.tflite"
#"saved_model2.tflite"
label_path = data_folder + "labels.txt"

interpreter = Interpreter(model_path)
print("Model Loaded Successfully.")

interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
# print("Image Shape (", width, ",", height, ")")

# Load an image to be classified.
image = Image.open(data_folder + "photo/testtest2.jpg").convert('RGB').resize((width, height))
print('image load done')

# Classify the image.
time1 = time.time()
label_id, prob = classify_image(interpreter, image)
time2 = time.time()
classification_time = np.round(time2-time1, 3)
print("Classificaiton Time =", classification_time, "seconds.")

# Read class labels.
labels = load_labels(label_path)

# Return the classification label of the image.
classification_label = labels[label_id]
print("Image Label is :", classification_label)#, ", with Accuracy :", np.round(prob*100, 2), "%.")
print(classification_label)

# terminal_command = f"ps"
# os.system(terminal_command)

del interpreter
del Interpreter
del image

if classification_label=='good':
  exec(open('brand_detect.py').read())
else:
  print('bad')
  bad_sign = 'bad'
  publish.single("cup_result", bad_sign, hostname="35.78.109.81")
  print("="*100)
  exec(open('webcam2_copy.py').read())

