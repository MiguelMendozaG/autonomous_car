# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from periphery import SPI
import numpy as np
import cv2 as cv
import time
import re
import svgwrite
import imp
import os
from edgetpu.detection.engine import DetectionEngine
import gstreamer
from lane_detection import input_output

angles = 0
traffic_sign = 0


def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def shadow_text(dwg, x, y, text, font_size=20):
    dwg.add(dwg.text(text, insert=(x+1, y+1), fill='black', font_size=font_size))
    dwg.add(dwg.text(text, insert=(x, y), fill='white', font_size=font_size))

def generate_svg(dwg, objs, labels, text_lines):
    width, height = dwg.attribs['width'], dwg.attribs['height']
    for y, line in enumerate(text_lines):
        shadow_text(dwg, 10, y*20, line)
    for obj in objs:
        x0, y0, x1, y1 = obj.bounding_box.flatten().tolist()
        x, y, w, h = x0, y0, x1 - x0, y1 - y0
        x, y, w, h = int(x * width), int(y * height), int(w * width), int(h * height)
        percent = int(100 * obj.score)
        label = '%d%% %s' % (percent, labels[obj.label_id])
        traffic_sign = obj.label_id
        #print (obj.label_id)
        shadow_text(dwg, x, y - 5, label)
        dwg.add(dwg.rect(insert=(x,y), size=(w, h),
                        fill='red', fill_opacity=0.3, stroke='white'))

def main():
    model = '../traffic_sign_detection/road_signs_quantized_v2_edgetpu.tflite'
    labels = '../traffic_sign_detection/road_sign_labels.txt'

    print("Loading %s with %s labels."%(model, labels))
    engine = DetectionEngine(model)
    labels = load_labels(labels)

    last_time = time.monotonic()
    def user_callback(image, svg_canvas):
      nonlocal last_time
      start_time = time.monotonic()
      objs = engine.DetectWithImage(image, threshold=0.1, keep_aspect_ratio=True, relative_coord=True, top_k=5)
      end_time = time.monotonic()
      text_lines = [
          'Inference: %.2f ms' %((end_time - start_time) * 1000),
          'FPS: %.2f fps' %(1.0/(end_time - last_time)),
      ]
      #print(' '.join(text_lines))
      last_time = end_time
      generate_svg(svg_canvas, objs, labels, text_lines)
      #status = cv.imwrite('output_image.png', np.array(image))
      angles = input_output(image)
      if (angles == False):
          print ("no angles found")
      else:
          #continue
          print (angles, traffic_sign)
    
    result = gstreamer.run_pipeline(user_callback)
    

if __name__ == '__main__':
    main()

