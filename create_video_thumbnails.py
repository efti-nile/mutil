import cv2, re, os, math, numpy

# The script creates a thumbnails for videos in a specified folder. Videos must have the same size.

# Parameters
FOLDER = '../../video_trim/trimmed'
RE = re.compile(r'.+.mp4$', re.IGNORECASE)  # RE to check if file is a video by its filename
OUT = './thumbnails.png'

# Find and count videos. Create list of caps
caps = []
for filename in os.listdir(FOLDER):
    if RE.match(filename):
        video_path = os.path.join(FOLDER, filename)
        caps.append(cv2.VideoCapture(video_path))

ts = math.ceil(math.sqrt(len(caps)))  # table size

# Compose a pallet
pallet = None
row, col = 0, 0
for cap in caps:
    _, frame = cap.read()
    cap.release()
    h, w, _ = frame.shape
    if pallet is None:
        pallet = numpy.zeros((h * ts, w * ts, 3))
    pallet[(row * h):((row + 1) * h), (col * w):((col + 1) * w)] = frame
    col += 1
    if col >= ts:
        col = 0
        row += 1

cv2.imwrite(OUT, pallet)
