import cv2
import argparse
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
from pyfirmata import Arduino, SERVO

port = 'COM7'
pin = 9
board = Arduino(port)
board.digital[pin].mode = SERVO

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='YOLOv8 Live')
    parser.add_argument('--webcam-resolution', default=[1280, 800], nargs=2, type=int)
    args = parser.parse_args()
    return args

def servo_signal(base_angle, disp, frame_width):
    angle = -(disp*47.5/(frame_width//2))
    base_angle += angle
    if base_angle>180 or base_angle<0:
        base_angle = 90
    # with open('moves.txt', 'a') as f:
    #     f.write("moving by angle: " + str(angle) + " for disp " + str(disp) + "\n")
    board.digital[pin].write(base_angle)
    time.sleep(0.015)
    return base_angle

def main(base_angle):
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    cap = cv2.VideoCapture(1) # 1 for external web cam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO('yolov8m.pt')
    # using annotator from supervision module, will create BBs on the frame from detections
    box_annotator = sv.BoundingBoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator()
    IMAGE_CENTER = (frame_width//2, frame_height//2)
    frame_count = 0
    while True:
        frame_count += 1
        ret, frame = cap.read()
        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_ultralytics(result)
        detections = detections[detections.class_id==0]

        labels = [f"{confidence:0.2f}"
                  for _, mask, confidence, class_id, _, data in detections]
        frame = box_annotator.annotate(scene=frame, detections=detections)
        frame = label_annotator.annotate(scene=frame, detections=detections, labels=labels)

        if len(detections)>0:
            max_conf = 0
            max_obj = None
            for detection in detections:
                if detection[2]>max_conf:
                    max_conf = detection[2]
                    max_obj = detection
            end_point = ((np.int32(max_obj[0][2])+np.int32(max_obj[0][0]))//2, frame_height//2)
            frame = cv2.line(frame, IMAGE_CENTER, end_point,
                            color=(0,0,255), thickness=2)
            text = f'{end_point[0]-IMAGE_CENTER[0]}, {end_point[1]}'
            frame = cv2.putText(frame, text, (end_point[0], end_point[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if frame_count%10==0:
                base_angle = servo_signal(base_angle, end_point[0]-IMAGE_CENTER[0], frame_width)

        
        cv2.imshow('window', frame)
        if cv2.waitKey(30)==27:
            break

if __name__=="__main__":
    base_angle = 90
    board.digital[pin].write(base_angle)
    main(base_angle)
        