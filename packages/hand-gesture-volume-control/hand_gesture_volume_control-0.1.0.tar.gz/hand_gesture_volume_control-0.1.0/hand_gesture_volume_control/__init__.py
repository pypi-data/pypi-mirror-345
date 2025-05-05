"""
Hand Gesture Volume Control Library
"""
# ضع الكود هنا من قبل المستخدم
import cv2
import mediapipe as mp
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe and video capture
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# Audio interface setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get system volume range
vol_min, vol_max = volume.GetVolumeRange()[:2]

# Volume change threshold and trigger zone
prev_distance = None
volume_trigger_zone = 150  # Only process volume if thumb-index distance < this

# Mute state tracker
is_muted = False
mute_trigger_cooldown = 0  # Avoid multiple toggles from same gesture

# Distance helper
def calculate_distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

while True:
    ret, image = cap.read()
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmarks
            index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            pinky = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

            # Convert to pixel coords
            h, w, _ = image.shape
            ix, iy = int(index.x * w), int(index.y * h)
            tx, ty = int(thumb.x * w), int(thumb.y * h)
            px, py = int(pinky.x * w), int(pinky.y * h)
            pmx, pmy = int(pinky_mcp.x * w), int(pinky_mcp.y * h)

            # Draw tips and line
            cv2.circle(image, (ix, iy), 10, (0, 255, 0), -1)
            cv2.circle(image, (tx, ty), 10, (255, 0, 0), -1)
            cv2.line(image, (ix, iy), (tx, ty), (255, 255, 255), 2)

            # Mute/unmute gesture - pinky tip much higher than MCP (extended)
            if (pmy - py) > 40 and mute_trigger_cooldown == 0:
                is_muted = not is_muted
                volume.SetMute(is_muted, None)
                mute_trigger_cooldown = 20  # Cooldown counter

            # Thumb-Index distance
            current_distance = calculate_distance(ix, iy, tx, ty)

            if current_distance < volume_trigger_zone:
                if prev_distance is not None:
                    change = current_distance - prev_distance

                    # Gesture sensitivity
                    small_thresh = 3
                    big_thresh = 10

                    if abs(change) > small_thresh:
                        volume_step = 0.12 if abs(change) > big_thresh else 0.03
                        current_vol = volume.GetMasterVolumeLevelScalar()

                        if change > 0:
                            new_vol = min(current_vol + volume_step, 1.0)
                        else:
                            new_vol = max(current_vol - volume_step, 0.0)

                        volume.SetMasterVolumeLevelScalar(new_vol, None)
                        cv2.putText(image, f'Volume: {int(new_vol * 100)}%', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                prev_distance = current_distance
            else:
                prev_distance = None  # Reset if outside volume zone

    if mute_trigger_cooldown > 0:
        mute_trigger_cooldown -= 1
        cv2.putText(image, f'Muted' if is_muted else 'Unmuted', (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Hand Gesture Volume Control", image)

    # Break the loop with 'a' key
    if cv2.waitKey(1) & 0xFF == ord('a'):
        break

cap.release()
cv2.destroyAllWindows()