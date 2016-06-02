"""
Face recognition (representation)
"""
import dlib
from skimage import io
import uuid
import json
import openface
import os

OBJECTS_PATH = "./dets/objects/"
RECOG_PATH = "./dets/recogobj/"
FRAME_IMAGE_PATH = "./frames/"
FRAME_MDATA_PATH = "./dets/"

Aligner = openface.AlignDlib("./shape_predictor_68_face_landmarks.dat")
net = openface.TorchNeuralNet("./openface/models/openface/nn4.small2.v1.t7",
                              imgDim=96)

def get_unrecognized_objects():
    all_objects = os.listdir(OBJECTS_PATH)
    rec_objects = os.listdir(RECOG_PATH)
    unrecog_objs = [item for item in all_objects if item not in rec_objects]
    return unrecog_objs

def read_obj_data(obj_file):
    json_data = open(OBJECTS_PATH + obj_file).read()
    data = json.loads(json_data)
    return data

def read_frame_data(frame):
    json_data = open(FRAME_MDATA_PATH + frame + ".json").read()
    data = json.loads(json_data)
    return data

def save_rep(obj_id, rep):
    jso = {}
    jso["id"] = obj_id
    jso["rep"] = []
    for i in rep:
        jso["rep"].append(i)

    with open(RECOG_PATH + obj_id + ".json", 'w') as f:
        json.dump(jso, f)

####
for objfile in get_unrecognized_objects():
    obj_data = read_obj_data(objfile)
    print "processing object {0}".format(obj_data["id"])
    start_frame = obj_data["start_frame"]
    print "reading frame {0}".format(start_frame)
    img = io.imread(FRAME_IMAGE_PATH + start_frame + ".jpg")
    frame_data = read_frame_data(start_frame)
    obj_pos = frame_data["objs"][obj_data["id"]]["pos"]
    bbox = dlib.rectangle(long(obj_pos["left"]), long(obj_pos["top"]),
                          long(obj_pos["right"]), long(obj_pos["bottom"]))

    print "finding face landmarks"
    landmarks = Aligner.findLandmarks(img, bbox)
    print "aligning to standart image"
    alignedFace = Aligner.align(96, img, bbox, landmarks=landmarks,
                                 landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        print "misalign!"

    print "calculating representation"
    rep = net.forward(alignedFace)

    print "saving representation"
    save_rep(obj_data["id"], rep)

    print "--------done--------"
