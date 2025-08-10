import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def is_closed_palm(landmarks):
    # Closed palm: all tips (except thumb) are below their PIP joints on Y
    finger_tips_ids = [8, 12, 16, 20]
    finger_pip_ids = [6, 10, 14, 18]
    closed = True
    for tip_id, pip_id in zip(finger_tips_ids, finger_pip_ids):
        if landmarks[tip_id][2] < landmarks[pip_id][2]:
            closed = False
            break
    return closed

def main():
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    # Initialize system volume interface
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Initialize smoothed volume
    smoothed_vol = minVol
    alpha = 0.15  # Smoothing factor: smaller = smoother and slower response

    prev_x, prev_time = None, time.time()
    swipe_cooldown = 1.0
    last_swipe_time = 0
    play_pause_cooldown = 1.0
    last_play_pause_time = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        swipe_detected = False

        if results.multi_hand_landmarks and results.multi_handedness:
            for handLms, handType in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handType.classification[0].label  # 'Left' or 'Right'

                h, w, _ = img.shape
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    lmList.append([id, int(lm.x * w), int(lm.y * h)])

                if not lmList:
                    continue

                if label == 'Right':
                    # Right hand: Volume control by distance between thumb tip (4) and index finger tip (8)
                    x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
                    x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip

                    # Draw visualization
                    cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    # Compute target volume
                    length = np.hypot(x2 - x1, y2 - y1)
                    target_vol = np.interp(length, [30, 200], [minVol, maxVol])

                    # Apply exponential smoothing for slow, smooth change
                    smoothed_vol = alpha * target_vol + (1 - alpha) * smoothed_vol
                    volume.SetMasterVolumeLevel(smoothed_vol, None)

                    # Volume bar visualization (shows smoothed volume)
                    volBar = np.interp(smoothed_vol, [minVol, maxVol], [400, 150])
                    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 2)
                    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
                    volPer = np.interp(smoothed_vol, [minVol, maxVol], [0, 100])
                    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 3)

                elif label == 'Left':
                    # Left hand: Media control (swipe for next/previous track and closed palm for play/pause)

                    # Draw landmarks
                    mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                    # Swipe detection with index finger tip (id 8)
                    x, y = lmList[8][1], lmList[8][2]
                    curr_time = time.time()
                    if prev_x is not None and (curr_time - last_swipe_time > swipe_cooldown):
                        dx = x - prev_x
                        if abs(dx) > 120:  # Tune this threshold as needed
                            if dx > 0:
                                # Left-to-right swipe: Previous track
                                pyautogui.press('prevtrack')
                                print("Swiped Left-to-Right: Previous Track")
                            else:
                                # Right-to-left swipe: Next track
                                pyautogui.press('nexttrack')
                                print("Swiped Right-to-Left: Next Track")
                            last_swipe_time = curr_time
                            swipe_detected = True
                    prev_x = x

                    # Closed palm for play/pause
                    if curr_time - last_play_pause_time > play_pause_cooldown and is_closed_palm(lmList):
                        pyautogui.press('space')
                        print("Closed palm: Play/Pause toggled")
                        last_play_pause_time = curr_time

                    # Skip drawing landmarks again for left hand (already drawn)

        cv2.imshow("Gesture Media Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
                   