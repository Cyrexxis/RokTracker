import cv2
from PIL import Image
import re


def cropToRegion(image, roi):
    return image[int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])]


def cropToTextWithBorder(img, border_size):
    coords = cv2.findNonZero(cv2.bitwise_not(img))
    x, y, w, h = cv2.boundingRect(coords)

    roi = img[y : y + h, x : x + w]
    bordered = cv2.copyMakeBorder(
        roi,
        top=border_size,
        bottom=border_size,
        left=border_size,
        right=border_size,
        borderType=cv2.BORDER_CONSTANT,
        value=[255],
    )

    return bordered


def preprocessImage(image, scale_factor, threshold, border_size, invert=False):
    im_big = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    im_gray = cv2.cvtColor(im_big, cv2.COLOR_BGR2GRAY)
    if invert:
        im_gray = cv2.bitwise_not(im_gray)
    (thresh, im_bw) = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    im_bw = cropToTextWithBorder(im_bw, border_size)
    return im_bw


def ocr_number(api, image):
    api.SetImage(Image.fromarray(image))
    score = api.GetUTF8Text()
    score = re.sub("[^0-9]", "", score)
    return score


def ocr_text(api, image):
    api.SetImage(Image.fromarray(image))
    name = api.GetUTF8Text()
    return name.rstrip("\n")


def preprocess_and_ocr_number(api, image, region, invert=False):
    cropped_image = cropToRegion(image, region)
    cropped_bw_image = preprocessImage(cropped_image, 3, 150, 12, invert)

    return ocr_number(api, cropped_bw_image)
