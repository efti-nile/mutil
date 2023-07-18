import os
import glob
import argparse

import cv2
import numpy as np


def main():
    args = get_args()

    tracklet_images = []
    for tracklet_folder in glob.glob(args['data']):
        tracklet_images.append([
            cv2.imread(img_filename) for img_filename in sorted(glob.glob(os.path.join(tracklet_folder, '*.jpg')))
        ])

    print(f'tracklets found: {len(tracklet_images)}')

    height = args['height'] // len(tracklet_images)
    width = height // 2
    thumbnail_size = (width, height)

    tracklet_images = [[cv2.resize(img, thumbnail_size) for img in tracklet[:10]] for tracklet in tracklet_images]

    out_image = np.zeros((args['height'], width * args['maxlen'], 3))

    for i, tracklet in enumerate(tracklet_images):
        for j, image in enumerate(tracklet):
            out_image[i * height:(i+1) * height, j * width:(j+1) * width, :] = image

    cv2.imwrite(args['out'], out_image)


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a glob to pick tracklet folders")
    ap.add_argument("--height", default=6000, help="output image height in pixels", type=int)
    ap.add_argument("--maxlen", default=10, help="truncate long tracklets to this length", type=int)
    ap.add_argument("--out", required=True, help="a glob to pick tracklet folders")
    return vars(ap.parse_args())


if __name__ == '__main__':
    main()