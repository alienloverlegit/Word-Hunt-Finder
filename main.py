import cv2
import numpy as np

from ocr import get_ocr
from wordfind import get_possible_words


# How many possible words are printed per line. Feel free to change this to your preference.
PRINT_INTERVAL = 6

# Probably shouldn't mess with any of these, as they involve the measured size of the board and optimized sizes.
HEIGHT = 800
REAL_HEIGHT = 8.85
REAL_WIDTH = 5.85
GRID_WIDTH = 4.1
GRID_SIZE = 4
RATIO = REAL_HEIGHT/REAL_WIDTH


def get_straight(orig, cnt):
    screen_pts = cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    pt_sum = screen_pts.sum(axis=1)
    rect[0] = screen_pts[np.argmin(pt_sum)]
    rect[2] = screen_pts[np.argmax(pt_sum)]

    pt_dif = np.diff(screen_pts, axis=1)
    rect[1] = screen_pts[np.argmin(pt_dif)]
    rect[3] = screen_pts[np.argmax(pt_dif)]

    width_b = np.sqrt((rect[2, 0] - rect[3, 0]) ** 2 + (rect[2, 1] - rect[3, 1]) ** 2)
    width_t = np.sqrt((rect[1, 0] - rect[0, 0]) ** 2 + (rect[1, 1] - rect[0, 1]) ** 2)
    height_l = np.sqrt((rect[3, 0] - rect[0, 0]) ** 2 + (rect[3, 1] - rect[0, 1]) ** 2)
    height_r = np.sqrt((rect[2, 0] - rect[1, 0]) ** 2 + (rect[2, 1] - rect[1, 1]) ** 2)

    new_width = int(max(width_b, width_t))
    new_height = int(max(height_l, height_r))

    dst = np.array([[0, 0], [new_width-1, 0], [new_width-1, new_height-1], [0, new_height-1]], dtype="float32")
    trans_mat = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(orig, trans_mat, (new_width, new_height))


cap = cv2.VideoCapture(0)

straight = None

while 1:
    ret, fr = cap.read()
    copied = fr.copy()

    edges = cv2.Canny(fr, 64, 512)

    cnts, heir = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:9]

    screen = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, .0064 * peri, True)

        if len(approx) == 4:
            screen = approx
            break

    if screen is not None:
        cv2.drawContours(copied, [screen], 0, (200, 32, 255), 2)
        straight = get_straight(fr, screen)
        cv2.imshow("Straightened", straight)

    cv2.imshow("Camera Stream", copied)

    key_press = cv2.waitKey(1)
    if key_press == 13:

        # print(straight.shape)
        sec_key = cv2.waitKey(0)
        if sec_key == 13:
            img = straight
            break
        elif sec_key == 8:
            continue

cap.release()
cv2.destroyAllWindows()

img = cv2.resize(img, (int(HEIGHT/RATIO), HEIGHT))

# cv2.imshow("In-Between image sent to OCR", img)
# cv2.waitKey(0)
# cv2.imwrite("test_board3.png", img)

grid_letters = get_ocr(img, HEIGHT, GRID_SIZE)
print(grid_letters)

words = get_possible_words(grid_letters)

count = 0

for word in words:
    if count % PRINT_INTERVAL == 0:
        print()
    if len(word) < 9:
        print(word, end="\t")
        count += 1

