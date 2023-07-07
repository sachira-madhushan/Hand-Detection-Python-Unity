import cv2
import mediapipe as mp
import math
import socket
import time
import pyautogui

UDP_IP = "127.0.0.1"
UDP_PORT = 5065

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#send commands to udp connection
def sendCommand(sock, UDP_IP, UDP_PORT, hands):
    command =str(hands)
    sock.sendto((command).encode(), (UDP_IP, UDP_PORT) )
    
    if(True): print("_"*10, command, " sent!", "_"*10)

#Calculate screen coordinates    
screen_width, screen_height = pyautogui.size()
frame_width, frame_height = 640, 480
frame_x = screen_width - frame_width
frame_y = screen_height - frame_height

#cv2 window settings
cap = cv2.VideoCapture(0)
cv2.namedWindow("Pong Input System - Developed By Sachira Madhushan", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Pong Input System - Developed By Sachira Madhushan", cv2.WND_PROP_TOPMOST, 1)
cv2.moveWindow("Pong Input System - Developed By Sachira Madhushan", frame_x, frame_y)


with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count fingers
            hand = results.multi_hand_landmarks[0]
            index_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_tip = hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand.landmark[mp_hands.HandLandmark.PINKY_TIP]

            fingers_up = 0
            if index_tip.y < middle_tip.y:
                fingers_up += 1
            if middle_tip.y < ring_tip.y:
                fingers_up += 1
            if ring_tip.y < pinky_tip.y:
                fingers_up += 1
            if thumb_tip.x < index_tip.x:
                fingers_up += 1
            if thumb_tip.x > index_tip.x:
                fingers_up += 2
            # Display finger count
            cv2.putText(image, str(fingers_up), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            sendCommand(sock, UDP_IP, UDP_PORT, fingers_up)
        else:
            sendCommand(sock, UDP_IP, UDP_PORT, 0)
        cv2.imshow('Pong Input System - Developed By Sachira Madhushan', image)
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()