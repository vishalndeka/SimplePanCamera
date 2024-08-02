# SimplePanCamera
This is a simple closed loop control system that does two things:
- Object detection on webcam feed
- Panning webcam to center the detected object in frame

<b>Object detection:</b>
Used Yolov8 (medium) from Ultralytics to detect objects in frame. Decided to detect only person classes (class_id = 0). To account for multiple people in frame, the object with highest confidence score is taken as the object to target. Bounding boxes and annotators are created using the `supervision` package, a very convenient package that houses reusable computer vision tools. Works real well.

<b>Panning Camera:</b>
The Webcam used here is Lenovo 300 FHD with 95 degree FOV. Camera panning movement is achieved by attempting to center the detected object's bounding box in the frame for every frame in which displacement of center of bounding box to center of frame is non-zero.
<img src = C:\Users\neerz\OneDrive\Documents\MindPlace\Images\panCamera_frame.excalidraw.png>
Moving to the right of the center line of the frame is considered +ve displacement, and -ve for the opposite side. This displacement value is added to the current angle that the servo is at, to move the camera into the desired position.
```Python
# considering the servo motor was at base_angle initially:
angle = -(disp*47.5/(frame_width//2))
base_angle += angle
```
The servo motor, an SG-90 is controlled using an Arduino Uno. For ease of use, I found `pyfirmata` a better choice for input from the python program than `pyserial`. Remember to install `pyfirmata` package in Arduino IDE and upload the `Servo Firmata` example onto the board for it to be ready to take in angle value inputs from python program.

_Note_: Only horizontal displacement from center is considered as only one servo in hand now, and panning would be easier to perform owing to the form of the webcam, compared to tilting.

Control Flow Diagram:
<img src = C:\Users\neerz\OneDrive\Documents\MindPlace\Images\PanCamera_ControlFlow.png>


# Further Work
- Making this work on the Jetson Nano - yolov8n has 9 times less FLOPs than yolov9m used here, need to check accuracy
- Code can be written cleaner, in a class preferably. Doing so will make it easier to add more components or scale it up
- Project could be more end to end, creating an UI would be nice, which would display all info in a better way, maybe the ability to select object to track
- Adding Tilt (another motor) and Zoom (using opencv?)
- Firmer base for the camera to handle rotations better (used tapes and clips for now, not very sound structurally)
