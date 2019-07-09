import argparse
import time

import numpy as np
import os
import datetime

import edgetpu.detection.engine
from PIL import Image

model = "road_signs_quantized_edgetpu.tflite"
label = 'road_sign_labels.txt'
image_path = "data/test/2019-04-16-095558.jpg"

engine = edgetpu.detection.engine.DetectionEngine(model)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


image = Image.open(image_path)
img_pil = Image.fromarray(image)
results = engine.DetectWithImage(img_pil, threshold=min_confidence, keep_aspect_ratio=True,
                                   relative_coord=False, top_k=5)
