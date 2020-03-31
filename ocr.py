import pytesseract
import numpy as np
import cv2


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CONFIG = ("--oem 1 --psm 10")
# -c tessedit_char_whitelist=ABCDEFGHI|1lJKLMNOPQRSTUVWXYZ

KERNEL = np.ones((3, 3), dtype=np.uint8)
RAD = 0.039
PADDING = 0.32
I_CHARS = "1|"
O_CHARS = "0"


def process_str(return_char):
    return_char = return_char.lower()
    for c in return_char:
        if c in I_CHARS:
            return "i"
        if c in O_CHARS:
            return "o"
        if c.isalpha():
            return c
    return "i"


def process_result(text_grid):
    shape = text_grid.shape
    for i in range(shape[0]):
        for j in range(shape[1]):
            text_grid[i, j] = process_str(text_grid[i, j])


def get_ocr(img, height, grid_size):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = cv2.GaussianBlur(img, (9, 9), 0)
    img = cv2.medianBlur(img, 7)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 2)

    cnts, heir = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:3]

    grid_cnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, .012 * peri, True)
        if len(approx) == 4:
            grid_cnt = approx
            break

    x, y, w, h = cv2.boundingRect(grid_cnt)

    avg_y = y + int(h/2)
    avg_x = x + int(w/2)
    tile_size = int((w + h)/2/grid_size)
    pad_dist = int(tile_size * PADDING / 2)

    crop = img[avg_y - 2 * tile_size:avg_y + 2 * tile_size, avg_x - 2 * tile_size:avg_x + 2 * tile_size]
    crop = 255 - crop

    circle_mask = np.zeros((tile_size, tile_size), dtype=np.uint8)
    cv2.circle(circle_mask, (int(tile_size/2), int(tile_size/2)), int(RAD * height), 255, -1)
    inv_circle = cv2.bitwise_not(circle_mask)

    text_grid = np.empty((grid_size, grid_size), dtype=object)
    # tiles = np.empty((4, 4, tile_size - 2 * pad_dist, tile_size - 2 * pad_dist), dtype=np.uint8)

    for i in range(grid_size):
        for j in range(grid_size):
            curr_tile = crop[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size]
            curr_tile = cv2.bitwise_and(curr_tile, curr_tile, mask=circle_mask)
            curr_tile += inv_circle
            curr_tile = cv2.morphologyEx(curr_tile, cv2.MORPH_OPEN, KERNEL, iterations=2)
            curr_tile = cv2.morphologyEx(curr_tile, cv2.MORPH_CLOSE, KERNEL, iterations=2)
            curr_tile = cv2.blur(curr_tile, (2, 2))
            curr_tile = cv2.bilateralFilter(curr_tile, 5, 180, 164)
            curr_tile = curr_tile[pad_dist:tile_size - pad_dist, pad_dist:tile_size - pad_dist]

            text_grid[i, j] = pytesseract.image_to_string(curr_tile, config=CONFIG)
            # tiles[i, j] = curr_tile

    process_result(text_grid)

    return text_grid

