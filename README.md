This project enables intuitive media and volume control using hand gestures captured from your webcam, leveraging OpenCV, MediaPipe, PyAutoGUI, and Pycaw.

Features
Right Hand (Volume Control):

Adjust system volume by changing the distance between your thumb tip and index finger tip.

Real-time visual feedback via an on-screen volume bar.

Volume changes are smoothed for a more natural, lag-free experience.

Left Hand (Media Control):

Swipe with index finger:

Swipe left-to-right to switch to the previous track.

Swipe right-to-left to skip to the next track.

Cooldowns prevent accidental repeats.

Closed palm gesture:

Play/pause the media player by making a fist (all fingers folded except the thumb).

Cooldown prevents rapid toggling.

How It Works
Utilizes MediaPipe to detect and track hand landmarks in real-time.

Assigns gesture-based controls depending on detected hand:

The right hand manipulates the system volume using physical finger distance.

The left hand triggers media commands (play/pause or skip) using gestural detection.

PyAutoGUI sends keyboard commands for media control (track navigation, play/pause).

Pycaw manages system audio volume changes directly.

Visualizes controls on the webcam feed with overlays and bars for clarity.

Requirements
Python 3.x

opencv-python

mediapipe

pyautogui

pycaw

comtypes

numpy

Usage
Run the script. Your webcam should activate.

Show your right hand: Adjust volume by moving your thumb and index finger together or apart.

Show your left hand: Swipe horizontally for track navigation, or close your palm to toggle play/pause.

Press Q in the OpenCV window to exit.

This project is ideal for hands-free control of your media and system audio, providing both functionality and a visual demonstration of gesture recognition technology using open-source Python libraries.
