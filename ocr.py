import os
from googletrans import Translator
import cv2
import pytesseract

# Path to the tesseract executable if on Windows
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = (
            r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            )

next_tier = 'img/total_power_required.png'
template_path = 'img/max_total_power.png'

translator = Translator()


def match_template(image, template):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_loc, max_val


def extract_roi(image,
                image_to_extract,
                template,
                extra_width1=0,
                extra_width2=0):
    max_loc, max_val = match_template(image, template)
    # Get the bounding box for the detected region
    template_height, template_width = template.shape
    top_left = max_loc
    bottom_right = (top_left[0] + template_width,
                    top_left[1] + template_height)

    return image_to_extract[top_left[1]:bottom_right[1] + extra_width1,
                            top_left[0]:bottom_right[0] + extra_width2,
                            ], bottom_right, top_left


def check_sidebar(image_path):
    # Load the main image and the template image
    image = cv2.imread(image_path)
    sidebar_template = cv2.imread(next_tier, 0)

    # Convert the main image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    roi, bottom_right, top_left = extract_roi(
            gray_image, gray_image, sidebar_template)
    _, thresh_roi = cv2.threshold(roi, 0, 255,
                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    extracted_text = translator.translate(
            pytesseract.image_to_string(thresh_roi), src='auto', dest='en'
            ).text

    if "achievement reward" in extracted_text.lower():
        return True, bottom_right[0] - top_left[0]
    return False, None


def extract_numbers_with_template(image_path):
    # Load the main image and the template image
    image = cv2.imread(image_path)
    template = cv2.imread(template_path, 0)

    # Convert the main image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Template matching to find the region of interest
    _, thresh = cv2.threshold(gray_image, 190, 195, cv2.THRESH_BINARY)

    sidebar, sidebar_width = check_sidebar(image_path)
    if sidebar:
        # Crop the image to exclude the sidebar from the right
        gray_image = gray_image[:, :gray_image.shape[1] - (
            sidebar_width + 300)]
        thresh = thresh[:, :thresh.shape[1] - (sidebar_width + 300)]

    roi, _, _ = extract_roi(gray_image, thresh, template, extra_width2=150)

    # Use pytesseract to extract text from the thresholded ROI
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    extracted_text = pytesseract.image_to_string(roi, config=custom_config)
    if len(extracted_text.split(' ')) > 1:
        return extracted_text.split(' ')[1].strip()
    return extracted_text.strip()
