import dlib
from skimage import io
import uuid
import json

INTERSECTION_EQ_RATIO = 0.80

detector = dlib.get_frontal_face_detector()

first_frame = 1 #1
last_frame = 175753 #175753

cur_objects = {}
cur_trackers = {}

def check_if_new(det, objs):
    for obj_id in objs:
        ob = objs[obj_id]
        pos_before = ob["tracker"].get_position()
        rect_before = dlib.rectangle(long(pos_before.left()), long(pos_before.top()), long(pos_before.right()), long(pos_before.bottom()))
        rect_det = dlib.rectangle(long(det.left()), long(det.top()), long(det.right()), long(det.bottom()))
        area_before = rect_before.area()
        print "!!! {0} {1}".format(rect_det, rect_before)
        intersection = rect_before.intersect(det)
        inters_area = intersection.area()
        print "area before {0} intersection {1}".format(area_before, inters_area)
        inters_ratio = float(inters_area) / float(area_before)
        print "intersection ratio: {0}".format(inters_ratio)
        if inters_ratio > INTERSECTION_EQ_RATIO:
            ob["confirmed"] = True
            return False
    return True

def finish_object(obj):
    print "finishing {0}".format(obj)
    #todo

def ser_obj(obj):
    ser = {}
    ser["id"] = obj["id"]
    ser["start_frame"] = obj["start_frame"]
    ser["last_frame"] = obj["last_frame"]
    return ser

last_frame_name = ""

for fr in range(first_frame, last_frame + 1):
    frame_name = "{:0>6d}".format(fr)
    last_frame_name = frame_name
    frame_data = {}
    frame_data["name"] = frame_name
    frame_data["objs"] = {}
    print "processing frame {0}".format(frame_name)
    image_file_name = frame_name + ".jpg"
    det_file_name = frame_name + ".json"

    img = io.imread("./frames/" + image_file_name)
    print "image was read from disk"

    print "tracking {0} current objects".format(len(cur_objects))
    # track & update prev objects
    ids_to_delete = []
    for obj_id in cur_objects:
        co = cur_objects[obj_id]
        ratio = co["tracker"].update(img)
        print "object {0} track ratio {1}".format(obj_id, ratio)
        if ratio < 10:
            co["last_frame"] = frame_name
            with open("./dets/objects/" + obj_id + ".json", 'w') as f:
                json.dump(ser_obj(co), f)
            ids_to_delete.append(obj_id)

    for oid in ids_to_delete:
        cur_objects.pop(oid)

    print "detecting faces"
    dets = detector(img, 2)

    print "faces detected: {0}".format(len(dets))
    for i, d in enumerate(dets):
        is_new = check_if_new(d, cur_objects)
        print "detection {0} is new? {1}".format(i, is_new)
        if is_new:
            new_ob = {}
            new_ob_id = str(uuid.uuid4())
            new_ob["id"] = new_ob_id
            print "starting tracking new object {0}".format(new_ob_id)
            new_ob["tracker"] = dlib.correlation_tracker()
            new_ob["tracker"].start_track(img, d)
            new_ob["start_frame"] = frame_name
            new_ob["confirmed"] = True
            #todo: face recognition
            cur_objects[new_ob_id] = new_ob

    for oid in cur_objects:
        pos = cur_objects[oid]["tracker"].get_position()
        obj_pos = {}
        obj_pos["top"] = pos.top()
        obj_pos["left"] = pos.left()
        obj_pos["right"] = pos.right()
        obj_pos["bottom"] = pos.bottom()
        frame_data["objs"][oid] = {}
        frame_data["objs"][oid]["pos"] = obj_pos
        frame_data["objs"][oid]["confirmed"] = cur_objects[oid]["confirmed"]
        cur_objects[oid]["confirmed"] = False

    with open("./dets/" + det_file_name, 'w') as f:
        json.dump(frame_data, f)

for oid in cur_objects:
    co = cur_objects[oid]
    co["last_frame"] = last_frame_name
    with open("./dets/objects/" + obj_id + ".json", 'w') as f:
        json.dump(ser_obj(co), f)
