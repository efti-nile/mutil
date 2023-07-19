import logging

import cv2
import numpy as np

from files import *


def create_thumbnails(
    input_folder,
    output_folder,
    video_format='mp4',
    thumbnail_format='jpg',
    skip_frames=10,
    report_every=10
):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    videos = list(input_folder.rglob(f'*.{video_format}'))
    create_empty_folder(output_folder)
    for video_path in videos:
        video_name = get_only_filename(video_path)
        create_empty_folder(output_folder / video_name)
        num_frames = get_num_frames(video_path)
        logging.debug(f'reading {video_path}')
        logging.debug(f'total frames: {num_frames}')
        for idx, frame in get_frames(video_path, skip=skip_frames):
            if idx % (report_every + 1) == 0:
                progress = round((idx + 1) * 100 / num_frames, 1)
                logging.debug(f'frame {idx + 1}/{num_frames} {progress}%')
            path = output_folder / video_name / f'{idx}.{thumbnail_format}'
            cv2.imwrite(path.as_posix(), frame)


def get_num_frames(video_path):
    video_path = Path(video_path)
    cap = cv2.VideoCapture(video_path.as_posix())
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return num_frames


def get_frames(video_path, skip=0):
    video_path = Path(video_path)
    cap = cv2.VideoCapture(video_path.as_posix())
    idx = 0
    while True:
        for _ in range(skip):
            ok = cap.grab()
            if not ok:
                break
            idx += 1
        ok, frame = cap.read()
        if not ok:
            break
        idx += 1
        yield idx, frame


def color2pixel(color):
    return np.array(color[::-1]).reshape([1, 1, 3])


def get_rgb_delta(image, color):
    image = np.array(image, dtype=np.double)
    pixel = np.array(color2pixel(color), dtype=np.double)
    rgb_delta = np.linalg.norm(image - pixel, axis=2)
    return rgb_delta


def get_mask(image, color, tolerance=20, fill_value=255):
    delta = get_rgb_delta(image, color)
    _, mask_f = cv2.threshold(delta, tolerance, fill_value, cv2.THRESH_BINARY)
    mask_u8 = np.array(mask_f, dtype=np.uint8)
    return fill_value - mask_u8  # inverse the image
  

def count_pixels(image, color):
    delta = get_rgb_delta(image, color)
    delta_flatten = delta.flatten()
    num_matches = (np.abs(delta_flatten) == 0).sum()
    return num_matches


def morph_dilate(image, kernel_size=5, iterations=1):
    kernel = np.ones((kernel_size, kernel_size))
    dilated = cv2.dilate(image, kernel, iterations=iterations)
    return dilated
    

def morph_open(image, kernel_size=5):
    kernel = np.ones((kernel_size, kernel_size),
                     dtype=np.uint8)
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return opened


def play(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()    


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