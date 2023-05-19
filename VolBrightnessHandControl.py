import cv2
import mediapipe as mp
import time
import numpy as np
import math

import HandTrackModule as htm


from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc


##############
wCam, hCam = 640, 480
##############

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

detector = htm.handDetector(detectionCon=0.8)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
selectMode = "Bright"

while True:

    ret, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    if(len(lmList)):

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,255,255),3)

        length = math.hypot(x2-x1,y2-y1)
        #print(length)
        if selectMode == "Vol":
            vol = np.interp(length,[35,100],[minVol,maxVol])
            print(vol)
            volume.SetMasterVolumeLevel(vol, None)
        elif selectMode == "Bright":
            bri = np.interp(length, [35, 100], [0, 100])
            print(bri)
            sbc.set_brightness(bri)
        else:
            print("Wrong Mode")



    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 0, 0), 2)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('v'):
        selectMode="Vol"

    if cv2.waitKey(1) & 0xFF == ord('b'):
        selectMode="Bright"

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
# Destroy all the windows
cv2.destroyAllWindows()