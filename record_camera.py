import cv2
import datetime as dt
import sys


MAX_PARTS = 100
PART_DURATION = dt.timedelta(minutes=5)
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
FPS = 20


def main(uri, label):
    cap = cv2.VideoCapture(sys.argv[1])
    writer = None
    begin = None
    parts = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            cap.release()
            if writer:
                writer.release()
            raise Exception(f'no frame returned: {uri}')
        if not writer:
            h, w, _ = frame.shape
            begin = dt.datetime.now()
            video = f'{label}_{begin.strftime("%Y-%m-%dT%H-%M-%S")}.mp4'
            writer = cv2.VideoWriter(video, FOURCC, FPS, (w, h))
        if dt.datetime.now() - begin > PART_DURATION:
            if writer:
                writer.release()
                writer = None
                parts += 1
        if parts > MAX_PARTS:
            cap.release()
            quit()


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
