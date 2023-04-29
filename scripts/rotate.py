#!/usr/bin/env python3
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl import app, flags
import cv2
import glob
import os
import multiprocessing

flags.DEFINE_string("path", "", "Directory to process.")
flags.DEFINE_string("destination", "rotated", "Directory to write new files.")
flags.DEFINE_enum("angle", "90", enum_values=["90", "180", "270"], 
                  help="Angle to rotate the images in degrees counterclockwise.")

FLAGS = flags.FLAGS

def process_helper(files, angle, flagAngleVal, flagDestVal):
    for file in files:
        print(file, flagAngleVal)
        rotate(file, os.path.join(flagDestVal, os.path.split(file)[1]), angle)

def rotate(image, destination, angle):
    image = cv2.imread(image)
    rotated = cv2.rotate(image, angle)
    print(f"Writing {destination}")
    cv2.imwrite(destination, rotated)

# Rotates a directory of images by the given amount.
# Assumes all images are the same size.
def main(argv) -> None:
    del argv  # Unused.
    g = os.path.join(FLAGS.path, '*.jpg')
    files = glob.glob(g)

    if len(files) == 0:
        print(f"No files found in {g}")
        return  
    if FLAGS.angle == "90":
        angle = cv2.ROTATE_90_CLOCKWISE
    elif FLAGS.angle == "180":
        angle = cv2.ROTATE_180_CLOCKWISE
    elif FLAGS.angle == "270":
        angle = cv2.ROTATE_90_COUNTERCLOCKWISE
    else:
        return
    
    numProcesses = multiprocessing.cpu_count()
    fileSlices = [[] for i in range(0, numProcesses)]
    for i in range(0, len(files), numProcesses):
        for j in range(0, numProcesses):
            if i + j < len(files):
                fileSlices[j].append(files[i + j])
            else:
                break
    processes = []
    for i in range(0, numProcesses):
        p = multiprocessing.Process(target=process_helper, args=(fileSlices[i], angle, FLAGS.angle, FLAGS.destination))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

if __name__ == "__main__":
    app.run(main)
