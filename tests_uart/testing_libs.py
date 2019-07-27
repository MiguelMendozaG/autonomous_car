#!/home/mendel/.virtualenvs/cv/bin/python


from periphery import Serial
import numpy as np
import cv2 as cv
import time
import re
import svgwrite
import imp
import os
from edgetpu.detection.engine import DetectionEngine
import gstreamer
