import matplotlib.pyplot as plt
import cv2
import numpy as np

def zebra_line(W=1000, H=500, width=20, displacement=.4, step=100):
    img = np.zeros((H, W, 3))
    y_cntr = H // 2
    for i in range(W // step):
        x_offset = i * step
        rect = np.array([
            0,
            y_cntr - round(width / 2) + (1 if i % 2 == 0 else -1) * round(width * displacement),
            step,
            y_cntr + round(width / 2) + (1 if i % 2 == 0 else -1) * round(width * displacement),
        ], dtype=int)
        rect += np.array([x_offset, 0, x_offset, 0], dtype=int)
        cv2.rectangle(img, tuple(rect[:2]), tuple(rect[2:]), (255, 255, 255), -1)
    return img
 
plt.figure(figsize=(15, 25))
plt.imshow(zebra_line())
