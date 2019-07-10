import argparse
import time
import re
import numpy as np
import os
import datetime

import edgetpu.detection.engine
from PIL import Image

model = "road_signs_quantized_edgetpu.tflite"
label = 'road_sign_labels.txt'
image_path = "data/test/2019-04-16-100317.jpg"

with open(label, 'r') as f:
	pairs = (l.strip().split(maxsplit=1) for l in f.readlines())
	labels = dict((int(k), v) for k, v in pairs) 

engine = edgetpu.detection.engine.DetectionEngine(model)

image = Image.open(image_path)
results = engine.DetectWithImage(image, threshold = 0.20, top_k = 6)

for result in results:
	print(labels[result.label_id], result.score*100)

