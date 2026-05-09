import cv2
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import math
from pycaw.pycaw import AudioUtilities # Change audio level (lab)

# model
cap = cv2.VideoCapture(0)

# video size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
pTime = 0

detector = HandDetector(detectionCon=0.8, maxHands=2)

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume
print(f"Audio output: {device.FriendlyName}")
print(f"- Muted: {bool(volume.GetMute())}")
print(f"- Volume level: {volume.GetMasterVolumeLevel()} dB")
print(f"- Volume range: {volume.GetVolumeRange()[0]} dB - {volume.GetVolumeRange()[1]} dB")
volRange = volume.GetVolumeRange() # Gets the audio range
minVol = volRange[0] # min audio
maxVol = volRange[1] # max auido
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()

    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)

    if hands:
        lmList = hands[0]["lmList"]
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][0], lmList[4][1]
        x2, y2 = lmList[8][0], lmList[8][1]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0))
        cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)
        
        
        # hand range: 50 - 300
        # volume range: -65 - 0
        
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None) # Change audio level
        
    
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    
    if volPer < 20:
        color = (0, 255, 0)
    elif volPer < 80:
        color = (0, 255, 255)
    else:
        color = (0, 0, 255)
    
    cv2.rectangle(img, (50, int(volBar)), (85, 400), color, cv2.FILLED)
        
    cv2.putText(
        img,                        # image to be written on it
        f"{int(volPer)} %",         # fbs
        (40, 450),                  # position
        cv2.FONT_HERSHEY_COMPLEX,   # font
        1,                          # size
        (0, 0, 255),                # color
        3                           # thickness
    )     

    cTime = time.time()             # current time
    fps = 1/(cTime - pTime)         # fps
    pTime = cTime
    
    cv2.putText(
        img,                        # image to be written on it
        f"FPS: {int(fps)}",         # fbs
        (40, 70),                   # position
        cv2.FONT_HERSHEY_COMPLEX,   # font
        1,                          # size
        (255, 0, 0),                # color
        3                           # thickness
    )
    
    cv2.imshow("Img", img)
    cv2.waitKey(1)
