from core.transformers.utils.debug_utils import save_debug_image, save_debug_text
from core.transformers.contour.contour import create_contour_from_roi, group_contours
from core.transformers.text.text_processing import get_text_rois_on_left_of_circle, put_text_in_circle_center, put_text_in_contour_center
import cv2
import numpy as np

def fill_circles(img, circles, index, output_dir):
    for circle in circles:
        print("circle", circle)
        index += 1
        put_text_in_circle_center(
            img,
            circle,
            str(index),
            font_scale=2.0,
            color=(0, 0, 255),
            thickness=2,
        )
    rois, img = get_text_rois_on_left_of_circle(circles, img)
    rois = [create_contour_from_roi(x[0], x[1], x[2], x[3]) for x in rois]
    
    # Save debug image
    save_debug_image(img, "concentric_rectangle_filtering.png", output_dir)
    
    return rois, img

def fill_and_find_missing_rectangles(img, contours, mean_area, output_dir):
    # Fill the rectangles
    index = -1
    search_radius = int(8 * np.sqrt(mean_area))

    # Merge similar rectangles
    contours = group_contours(contours, 8)
    
    rect_rois = []

    print(search_radius, mean_area, len(contours))

    # Save contours data
    contours_data = "index,x,y,w,h\n"
    for index, cnt in enumerate(contours):
        put_text_in_contour_center(
            img,
            cnt,
            str(index+1),
            font_scale=2.0,
            color=(0, 0, 255),
            thickness=2,
        )
        x, y, w, h = cv2.boundingRect(cnt)
        rect_rois.append({"x": x, "y": y, "w": w, "h": h, "index": index+1})
        contours_data += f"{index+1},{x},{y},{w},{h}\n"
    
    # Save debug files
    save_debug_text(contours_data, "contours.txt", output_dir)
    save_debug_image(img, "after_fill_and_find_missing_rectangles.png", output_dir)
    
    return img, index, rect_rois
