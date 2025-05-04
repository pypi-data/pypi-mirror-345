from ultralytics import YOLO
import cv2
import base64
import numpy as np
from ultralytics.utils.plotting import Annotator
import os
import torch
import gc
import time

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
if(torch.cuda.is_available()):
    torch.cuda.set_per_process_memory_fraction(0.7, 0)


current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'weights/best.pt')


def getYoloModel():
    model = YOLO(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model.fuse()
    model.to(device)
    return model


def extract_digits(test_model, bigfile, conf, imgflg=False, cropped=False):
    start = time.time()
    img = cv2.imread(bigfile)
    annotator = Annotator(img)

    y_adjustment = 20.0

    test_model.conf = conf
    try:
        result = test_model.predict(source=img, show_conf=True, save=False,
                                    save_crop=False, exist_ok=True, verbose=False, iou=.4,
                                    agnostic_nms=True)
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return '', '', ''

    digit = {}
    cb64 = ''
    base64_image = ''

    for r in result:

        boxes = r.boxes.cpu()
        if len(boxes) == 0:
            print("[WARNING] No boxes found.")
            return '', '', ''

        avg_y = np.mean([box.xywh.tolist()[0][1] for box in boxes])

        high_box = np.array([[int(box.xywh.tolist()[0][0]), box.conf.item()] for box in boxes])
        high_conf_box = np.array([high_box[high_box[:, 0] == key].max(axis=0) for key in np.unique(high_box[:, 0])])
        lookup_dict = {int(key): value for key, value in high_conf_box}
        # print(lookup_dict)

        for box in boxes:

            # print(box.xywh.tolist()[0][0] , ':' , box.conf)
            y = box.xywh.tolist()[0][1]
            box_conf = lookup_dict.get(int(box.xywh.tolist()[0][0]), None)
            # print(box_conf)
            if box.conf >= box_conf and avg_y + y_adjustment >= y >= avg_y - y_adjustment:
                c = box.cls
                b = box.xyxy[0]
                digit.update({box.xywh.tolist()[0][0]: test_model.names[int(c)]})
                annotator.box_label(b, test_model.names[int(c)])

    digits_str = ''
    for x, y in sorted(digit.items()):
        digits_str += str(y)

    # print(imgflg)

    if imgflg:
        # Get the annotated image
        img = annotator.result()
        # Convert the image to base64
        _, buffer = cv2.imencode('.jpg', img)
        base64_image = base64.b64encode(buffer).decode()

    if cropped:
        # Create a new image that only contains the annotated area
        x_min = int(min([box.xyxy[0][0] for box in boxes]))
        y_min = int(min([box.xyxy[0][1] for box in boxes]))
        x_max = int(max([box.xyxy[0][2] for box in boxes]))
        y_max = int(max([box.xyxy[0][3] for box in boxes]))

        if (y_min < 20):
            y_min = 0
        else:
            y_min = y_min - 20

        try:
            annotated_area_img = img[y_min:y_max, x_min:x_max]
            # Save the new image
            _, abuffer = cv2.imencode('.jpg', annotated_area_img)
            cb64 = base64.b64encode(abuffer).decode()
            del annotated_area_img
        except Exception as e:
            print("[ERROR] Cropping failed:", e)
            cb64 = ''

    del annotator
    del img
    gc.collect()
    torch.cuda.empty_cache()
    print('Extraction in: ' + str(round((time.time() - start) * 1000, 2)) + ' ms \n')
    return digits_str, base64_image, cb64
