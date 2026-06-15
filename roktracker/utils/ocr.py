"""OCR preprocessing and text extraction utilities.

Provides image preprocessing functions (preprocessImage,
advancedProcessing, cropToRegion, cropToTextWithBorder) and
OCR extraction helpers (ocr_number, ocr_text,
preprocess_and_ocr_number). All work with cv2/MatLike images."""

import re
from typing import Literal, Tuple

import cv2
import numpy as np
import tesserocr
from cv2.typing import MatLike
from PIL import Image


def cropToRegion(image: MatLike, roi: Tuple[int, int, int, int]) -> MatLike:
    """Crops an image to a region.

    Args:
        image (MatLike): The image to crop
        roi (Tuple[int, int, int, int]): The region to crop to in (x, y, w, h)

    Returns:
        MatLike: The cropped image
    """
    return image[int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])]


def cropToTextWithBorder(img: MatLike, border_size: int) -> MatLike:
    """Crops a black and white picture to the smallest size containing non white pixels.

    Args:
        img (MatLike): The image to crop
        border_size (int): The border to add around the detected pixels

    Returns:
        MatLike: The cropped image
    """
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


def preprocessImage(
    image: MatLike,
    scale_factor: int,
    threshold: int,
    border_size: int,
    invert: bool = False,
) -> MatLike:
    """Preprocesses an image to improve OCR quality.

    First a scaling factor gets applied, then the image is converted to
    grey scale. After that it is inverted if needed and then gets cropped
    to the smallest region containing black pixels with a border around them.

    Args:
        image (MatLike): The image to preprocess
        scale_factor (int): The factor the image is scaled
        threshold (int): The threshold to use for black and white conversion
        border_size (int): The border to add around the black pixels
        invert (bool): Whether to invert the image or not (Default value = False)

    Returns:
        MatLike: The preprocessed image
    """
    im_big = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    im_gray = cv2.cvtColor(im_big, cv2.COLOR_BGR2GRAY)
    if invert:
        im_gray = cv2.bitwise_not(im_gray)
    (_, im_bw) = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
    im_bw = cropToTextWithBorder(im_bw, border_size)
    return im_bw


def advancedProcessing(
    image: MatLike, scale_factor: int, mode: Literal["white", "dimmed white", "black"]
) -> MatLike:
    """Preprocesses an image to improve OCR quality.

    First a scaling factor gets applied, then the image is converted to
    HSV scale. After that a mask depending on the expected color gets
    applied. The final processing is to dilute that mask and invert it
    to get black text.

    Args:
        image (MatLike): The image to preprocess
        scale_factor (int): The factor the image is scaled
        mode (Literal['white', 'dimmed white', 'black']): The color of the text to detect

    Returns:
        MatLike: The preprocessed image
    """
    kernel = np.ones((2, 2), np.uint8)
    im_big = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    hsv = cv2.cvtColor(im_big, cv2.COLOR_BGR2HSV)

    match mode:
        case "black":
            lower = np.array([0, 0, 0])  # Acclaim and ID
            upper = np.array([255, 255, 30])  # Acclaim and ID
        case "dimmed white":
            lower = np.array([0, 0, 210])  # Acclaim and ID
            upper = np.array([255, 255, 255])  # Acclaim and ID
        case "white":
            lower = np.array([0, 0, 220])  # Acclaim and ID
            upper = np.array([255, 255, 255])  # Acclaim and ID

    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.dilate(mask, kernel, iterations=1)
    result = cv2.bitwise_not(result)  # Need to invert to make text black
    return result


def ocr_number(
    api: tesserocr.PyTessBaseAPI, image: MatLike, empty_retry: bool = True
) -> str:
    """Extracts a integer from an image.

    This function extract the text from the given image, then strips it
    with regex to only contain digits. If the first try produces an
    empty text a second try with a scaled down version of the image gets
    attempted.

    Args:
        api (tesserocr.PyTessBaseAPI): The ocr api to use
        image (MatLike): The image to analyze
        empty_retry (bool): Whether to try a second time if first fails (Default value = True)

    Returns:
        str: The digits that got detected
    """
    api.SetImage(Image.fromarray(image))  # type: ignore
    score_raw = api.GetUTF8Text()
    score = re.sub("[^0-9]", "", score_raw)

    if score == "" and empty_retry:
        img_try_2 = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        api.SetImage(Image.fromarray(img_try_2))  # type: ignore
        score_raw = api.GetUTF8Text()
        score = re.sub("[^0-9]", "", score_raw)

    return score


def ocr_text(api: tesserocr.PyTessBaseAPI, image: MatLike) -> str:
    """Extracts a string from the image.

    Args:
        api (tesserocr.PyTessBaseAPI): The ocr api to use
        image (MatLike): The image to analyze

    Returns:
        str: The detected string
    """
    api.SetImage(Image.fromarray(image))  # type: ignore
    name = api.GetUTF8Text()
    return name.rstrip("\n")


def preprocess_and_ocr_number(
    api: tesserocr.PyTessBaseAPI,
    image: MatLike,
    region: Tuple[int, int, int, int],
    invert: bool = False,
) -> str:
    """Combines the preprocessing and ocr into a single method.

    Args:
        api (tesserocr.PyTessBaseAPI): The ocr api to use
        image (MatLike): The image to analyze
        region (Tuple[int, int, int, int]): The region to analyze in (x, y, w, h) format
        invert (bool): Whether to invert the image before OCR (Default value = False)

    Returns:
        str: The detected digits
    """
    cropped_image = cropToRegion(image, region)
    cropped_bw_image = preprocessImage(cropped_image, 3, 150, 12, invert)

    return ocr_number(api, cropped_bw_image)


def get_supported_langs(path: str) -> str:
    """Gets the supported languages from the ocr engine.

    Args:
        path (str): Path to the trained data

    Returns:
        str: All supported languages
    """
    return str(tesserocr.get_languages(path))  # type: ignore
