import fitz  # PyMuPDF
import numpy as np
import cv2
import os
import shutil
import ntpath
from tqdm import tqdm
from thefuzz import fuzz, process
from paddleocr import PaddleOCR


def page_to_image(page, dpi=300, clip=None):
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=clip)  # Scale image
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format
    return img


def fitz_to_cv2_rect(rect, dpi=300):
    scale = dpi / 72  # Convert from points to pixels
    x1, y1 = int(rect[0] * scale), int(rect[1] * scale)
    x2, y2 = int(rect[2] * scale), int(rect[3] * scale)
    return (x1, y1), (x2, y2)


def crop_cv2_bbox(image, bbox):
    """Crop a region from an image using OpenCV-style bounding box."""
    (x1, y1), (x2, y2) = bbox
    return image[y1:y2, x1:x2]


def draw_cv2_bbox(image, bbox, color=(0, 255, 0), thickness=2):
    """Draw a rectangle on the image using OpenCV-style bounding box."""
    (x1, y1), (x2, y2) = bbox
    img_copy = image.copy()
    cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)
    return img_copy


def enlarge_fitz_bbox(bbox, w1, h1, w2, h2):
    x0, y0, x1, y1 = bbox
    width = x1 - x0
    height = y1 - y0

    new_x0 = x0 - w1 * width
    new_y0 = y0 - h1 * height
    new_x1 = x1 + w2 * width
    new_y1 = y1 + h2 * height
    return new_x0, new_y0, new_x1, new_y1


def enlarge_opencv_bbox(bbox, w1, h1, w2, h2):
    """
    Enlarge an OpenCV-style bounding box with 4 multipliers (left, top, right, bottom).

    :param bbox: ((x0, y0), (x1, y1))
    :param w1: multiplier for left side
    :param h1: multiplier for top side
    :param w2: multiplier for right side
    :param h2: multiplier for bottom side
    :return: Enlarged bbox in OpenCV format: ((new_x0, new_y0), (new_x1, new_y1))
    """
    (x0, y0), (x1, y1) = bbox
    width = x1 - x0
    height = y1 - y0

    new_x0 = int(x0 - w1 * width)
    new_y0 = int(y0 - h1 * height)
    new_x1 = int(x1 + w2 * width)
    new_y1 = int(y1 + h2 * height)

    return (new_x0, new_y0), (new_x1, new_y1)



def find_cartouche(page, output_png_path=None, output_pdf_path=None, threshold=90):
    # Extract all text from the page
    text = page.get_text("text")
    words = text.split()  # Split into individual words

    # Use fuzzy matching to find the closest match to "MATERIAL"
    pattern = "MATIERE/MATERIAL"
    best_match = process.extractOne(pattern, words, scorer=fuzz.token_sort_ratio)

    if best_match and best_match[1] >= threshold:  # Check if score meets threshold
        matched_word = best_match[0]
        #print(f"Found best match: '{matched_word}' with score: {best_match[1]}")

        # Search for the matched word in the page
        text_instances = page.search_for(matched_word)
        bbox = text_instances[0]
        if len(text_instances) > 1:
            print(f"CAREFUL !! {len(text_instances)} boxes containing '{pattern}' have been found !")

        # Modify bbox coordinates as per the original request
        bbox = enlarge_fitz_bbox(bbox, 0.5, 10, 5.5, 23)

        # Extract the selected bbox area and save it as a PNG
        page_cv2 = page_to_image(page, dpi=300, clip=bbox)

        # Draw a rectangle around the bbox in the PDF
        page.draw_rect(bbox, color=(1, 0, 0), width=2)  # Red rectangle

        # Save the crop as an image
        if output_png_path:
            cv2.imwrite(output_png_path, page_cv2)

        # Save the PDF with annotations
        if output_pdf_path:
            doc = fitz.open()
            doc.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
            doc.save(output_pdf_path)
            doc.close()

        return page_cv2, bbox
    return None, None


def find_cell(page, pattern="MATIERE/MATERIAL", output_png_path=None, output_pdf_path=None, threshold=90):
    # Extract all text from the page
    text = page.get_text("text")
    words = text.split()  # Split into individual words

    # Use fuzzy matching to find the closest match to "MATERIAL"
    best_match = process.extractOne(pattern, words, scorer=fuzz.token_sort_ratio)

    if best_match and best_match[1] >= threshold:  # Check if score meets threshold
        matched_word = best_match[0]
        #print(f"Found best match: '{matched_word}' with score: {best_match[1]}")

        # Search for the matched word in the page
        text_instances = page.search_for(matched_word)
        bbox = text_instances[0]
        if len(text_instances) > 1:
            print(f"CAREFUL !! {len(text_instances)} boxes containing '{pattern}' have been found !")

        # Modify bbox coordinates to get the entire cell
        bbox = enlarge_fitz_bbox(bbox, 0.1, 0.5, 3, 0.4)

        # Extract the selected bbox area and save it as a PNG
        page_cv2 = page_to_image(page, dpi=300, clip=bbox)

        # Draw a rectangle around the bbox in the PDF
        page.draw_rect(bbox, color=(1, 0, 0), width=2)  # Red rectangle

        # Save the crop as an image
        if output_png_path:
            cv2.imwrite(output_png_path, page_cv2)

        # Save the PDF with annotations
        if output_pdf_path:
            doc = fitz.open()
            doc.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
            doc.save(output_pdf_path)
            doc.close()

        return page_cv2
    return None


def find_best_match(crop, pictograms, labels, threshold=0.1, scales=None):
    import cv2

    if scales is None:
        scales = np.arange(0.1, 1.31, 0.1)

    crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    pictograms_gray = [cv2.cvtColor(p, cv2.COLOR_BGR2GRAY) for p in pictograms]

    highest_confidence = threshold
    best_index = -1

    for i, pictogram in enumerate(pictograms_gray):
        for scale in scales:
            # Resize template
            resized = cv2.resize(pictogram, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

            # Skip if resized template is larger than the crop
            if resized.shape[0] > crop_gray.shape[0] or resized.shape[1] > crop_gray.shape[1]:
                print("skip")
                continue

            result = cv2.matchTemplate(crop_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > highest_confidence:
                highest_confidence = max_val
                best_index = i

    if best_index != -1:
        return pictograms[best_index], highest_confidence, labels[best_index]
    else:
        return None, highest_confidence, None


def find_pictogram_in_image(image, pictogram, threshold=0.7, max_scale=2.0, output_png_path=None):
    """
    Searches for the pictogram in the part image using template matching at multiple scales.

    :param image: Path to the part image where we search the pictogram.
    :param pictogram: Path to the pictogram image.
    :param threshold: Minimum match score for a valid match (0 to 1).
    :param max_scale: Maximum scale factor to stop resizing at.

    :return: A list of rectangles around the found pictograms along with their confidence scores.
    """
    # Convert images to grayscale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pictogram_gray = cv2.cvtColor(pictogram, cv2.COLOR_BGR2GRAY)

    rectangles = []
    confidences = []
    # Try different scales
    step = 0.1
    scale_values = np.arange(step, max_scale + step, step)
    for scale in tqdm(scale_values, desc="🔍 Scanning scales"):
        # Resize the pictogram at the current scale
        resized_pictogram = cv2.resize(pictogram_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Perform template matching
        result = cv2.matchTemplate(image_gray, resized_pictogram, cv2.TM_CCOEFF_NORMED)
        # Find locations where the match score is above the threshold
        match_locations = np.where(result >= threshold)
        for pt in zip(*match_locations[::-1]):  # Reverse the coordinates for x, y
            top_left = pt
            bottom_right = (top_left[0] + resized_pictogram.shape[1], top_left[1] + resized_pictogram.shape[0])
            confidence = result[top_left[1], top_left[0]]  # Get the confidence score for the match

            rectangles.append((top_left, bottom_right))
            confidences.append(confidence)

            # Draw rectangles on the part image (optional)
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    # Save the image with rectangles drawn around the found pictograms
    if output_png_path:
        cv2.imwrite(output_png_path, image)
    return rectangles, confidences


def merge_rectangles(rectangles, confidences, threshold=10):
    """
    Merges rectangles that are very close to each other based on a given threshold,
    while keeping the highest confidence rectangle.

    :param rectangles: List of tuples containing the coordinates of rectangles.
    :param confidences: List of confidence values corresponding to each rectangle.
    :param threshold: Distance threshold for merging (in pixels).
    :return: List of merged rectangles along with their associated confidence scores.
    """
    merged = []
    merged_confidences = []  # List to store the confidence scores of merged rectangles

    # Sort rectangles by top-left corner (to make it easier to compare)
    rectangles = sorted(zip(rectangles, confidences), key=lambda r: (r[0][0][1], r[0][0][0]))
    rectangles, confidences = zip(*rectangles)  # Unzip the sorted rectangles and confidences

    for rect, confidence in zip(rectangles, confidences):
        # If no merged rectangles or the current rectangle is far from the last merged one
        if not merged:
            merged.append(rect)
            merged_confidences.append(confidence)
        else:
            last_rect = merged[-1]
            last_confidence = merged_confidences[-1]

            # Check if the current rectangle is close enough to the last merged one
            x_distance = abs(rect[0][0] - last_rect[0][0])  # Check x distance
            y_distance = abs(rect[0][1] - last_rect[0][1])  # Check y distance

            if (x_distance <= threshold and y_distance <= threshold and
                    rect[1][0] >= last_rect[0][0] and rect[1][1] >= last_rect[0][1]):
                # Merge the rectangles (expand the bounding box) and keep the higher confidence
                new_rect = (
                    (min(last_rect[0][0], rect[0][0]), min(last_rect[0][1], rect[0][1])),
                    (max(last_rect[1][0], rect[1][0]), max(last_rect[1][1], rect[1][1]))
                )

                # Keep the rectangle with the higher confidence
                if confidence > last_confidence:
                    merged[-1] = new_rect
                    merged_confidences[-1] = confidence
            else:
                merged.append(rect)  # Add current rectangle to merged list if it's not close enough
                merged_confidences.append(confidence)

    return merged, merged_confidences


def exclude_inner_rectangles(big_rect, small_rects):
    """
    Removes rectangles that are fully inside the big_rect.

    :param big_rect: A tuple (x0, y0, x1, y1) for the reference rectangle.
    :param small_rects: A list of rectangles in format [((x0, y0), (x1, y1)), ...]
    :return: Filtered list of rectangles not fully inside big_rect.
    """
    bx0, by0, bx1, by1 = big_rect
    filtered = []
    for (sx0, sy0), (sx1, sy1) in small_rects:
        if not (bx0 <= sx0 <= sx1 <= bx1 and by0 <= sy0 <= sy1 <= by1):
            filtered.append(((sx0, sy0), (sx1, sy1)))
    return filtered


def apply_OCR(img, model_path):
    # Initialize the OCR model
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="fr",
        det_model_dir=os.path.join(model_path, "det"),
        rec_model_dir=os.path.join(model_path, "rec"),
        cls_model_dir=os.path.join(model_path, "cls"),
        show_log=False,
    )
    # Run OCR on the RGB image
    result = ocr.ocr(img, cls=True)
    return result



