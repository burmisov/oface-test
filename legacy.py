from mc import MC
import sys
import json
import os
import re

OBJECTS_PATH = "./dets/objects/"
RECOG_PATH = "./dets/recogobj/"
FRAME_MDATA_PATH = "./dets/"

if len(sys.argv) < 6:
    print "no db arg"
    print "legacy.py <db server url> <db server port> <username> <password>"
    exit(1)

mc = MC({'serverUrl': sys.argv[1],
         'port': int(sys.argv[2]),
         'userName': sys.argv[3],
         'password': sys.argv[4],
         'dbName': sys.argv[5]})

# upload objects (facetraces)
print "uploading objects (facetraces)"
object_files = os.listdir(OBJECTS_PATH)
total_obj_files = len(object_files)
processed_obj_files = 0
for obj_file in object_files:
    print "processing file {0}".format(obj_file)
    obj_json = open(OBJECTS_PATH + obj_file).read()
    obj_data = json.loads(obj_json)
    mc.addFaceTrace(obj_data)
    processed_obj_files = processed_obj_files + 1
    print "uploaded facetrace {0} of {1}".format(processed_obj_files, total_obj_files)


# update objects (facetraces) with recognitions
print "uploading recognitions"
recog_files = os.listdir(RECOG_PATH)
total_rec_files = len(recog_files)
processed_rec_files = 0
for rec_file in recog_files:
    print "processing file {0}".format(rec_file)
    rec_json = open(RECOG_PATH + rec_file).read()
    rec_data = json.loads(rec_json)
    ft = mc.getFaceTraceByTraceId(rec_data['id'])
    ft['rep'] = rec_data['rep']
    mc.updateFaceTrace(ft)
    processed_rec_files = processed_rec_files + 1
    print "updated facetrace {0} of {1}".format(processed_rec_files, total_rec_files)

# upload frame metadata
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

print "uploading frames"
frame_dir_files = os.listdir(FRAME_MDATA_PATH)
frame_re = re.compile('\d{6}\.json')
frame_files = [f for f in frame_dir_files if frame_re.match(f) is not None]
total_frame_files = len(frame_files)
processed_frame_files = 0

for chunk in chunks(frame_files, 200):
    docs = []
    chunk_length = len(chunk)
    for frame_file in chunk:
        print "processing file {0}".format(frame_file)
        frame_json = open(FRAME_MDATA_PATH + frame_file).read()
        frame_data = json.loads(frame_json)
        docs.append(frame_data)
    print "inserting to db"
    mc.addMultipleFrames(docs)
    processed_frame_files = processed_frame_files + chunk_length
    print "uploaded frames {0} of {1}".format(processed_frame_files,
                                             total_frame_files)

