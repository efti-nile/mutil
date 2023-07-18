import json
import os
import shutil

import cv2
import numpy as np
import requests
from dateutil import tz


def create_empty_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    os.chmod(folder_path, 0o777)


def normalize(img):

    img = img.astype(np.float32)

    min_ = np.min(img)
    max_ = np.max(img)

    if max_ > min_:
        ret = np.clip((img - min_) / (max_ - min_), 0., 1.)
    else:
        ret = img * 0.

    return (255 * ret).astype(np.uint8)


def iou(box1, box2):

    xmin = max(box1[0], box2[0])
    ymin = max(box1[1], box2[1])
    xmax = min(box1[2], box2[2])
    ymax = min(box1[3], box2[3])

    if xmin > xmax or ymin > ymax:
        return 0.

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    intersection_area = (xmax - xmin) * (ymax - ymin)
    union_area = box1_area + box2_area - intersection_area
    iou = intersection_area / union_area

    assert 0. <= iou <= 1.

    return iou


def annotate(frame, boxes, classes, scores,
             colors, line_width=4, frame_idx=None,
             fclr=(255, 255, 255), font=cv2.FONT_HERSHEY_COMPLEX,
             rel_coord=True):
    frame = frame.copy()
    h, w, _ = frame.shape
    if frame_idx:
        frame = cv2.putText(frame, str(frame_idx), (20, 20),
                            font, .5, fclr, 1, cv2.LINE_AA)
    for b, c, s in zip(boxes, classes, scores):
        if rel_coord:
            x1 = int(b[0] * w)
            x2 = int(b[2] * w)
            y1 = int(b[1] * h)
            y2 = int(b[3] * h)
        else:
            x1 = int(b[0])
            x2 = int(b[2])
            y1 = int(b[1])
            y2 = int(b[3])
        p1 = (x1, y1)
        p2 = (x2, y2)
        frame = cv2.rectangle(frame, p1, p2, colors[c], line_width)
        txt = f'{c} {round(s * 100)}%'
        org = (x1 + 10, y1 + 20)
        frame = cv2.putText(frame, txt, org,
                            font, .5, fclr, 1, cv2.LINE_AA)
    return frame


def utc_to_local(dt,
                 tz_from='UTC',
                 tz_to='UTC+3'):
    tz_from = tz.gettz(tz_from)
    tz_to = tz.gettz(tz_to)
    utc_dt = dt.replace(tzinfo=tz_from)
    local_dt = utc_dt.astimezone(tz_to)
    return local_dt


def get_auth_token(cfg):
    # TODO: it's thread-unsafe
    headers = {'Content-Type': 'application/json'}
    data = {
        "username": os.environ.get('API_USERNAME'),
        "password": os.environ.get('API_PASSWORD')
    }
    endpoint = f'{cfg["be_protocol"]}://{cfg["be_server"]}:{cfg["be_port"]}/api/v1/token/'
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    print(f'auth: response {response.status_code}')
    token = f'Bearer {response.json()["access"]}'
    return token


def non_max_supression(detections, iou_thresh=.5):
    if not detections:
        return detections
    boxes = [d[0] for d in detections]
    classes = [d[1] for d in detections]
    scores = [d[2] for d in detections]
    out_detections = []
    n = len(detections)
    for i in range(n):
        discard = False
        for j in range(i + 1, n):
            if iou(boxes[j], boxes[i]) > iou_thresh:
                if scores[j] > scores[i]:
                    discard = True
        if not discard:
            out_detections.append(
                (boxes[i], classes[i], scores[i])
            )
    return out_detections
