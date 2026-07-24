
import cv2
import time
import os
import mediapipe as mp
from mediapipe.tasks.python import vision

def main():
    model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options = BaseOptions(model_asset_path = model_path),
        running_mode = VisionRunningMode.VIDEO
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Webcam cannot be used for some reason")
        exit()

    with FaceLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't read the frame")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            timestamp_ms = int(time.time() * 1000) #1000 is a second 
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            if result.face_landmarks:
                for face_landmarks in result.face_landmarks:
                    for landmark in face_landmarks:
                        # landmark.x, landmark.y are normalized [0,1] — multiply by frame size for pixel coords
                        x_px = int(landmark.x * frame.shape[1])
                        y_px = int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x_px, y_px), 1, (0, 255, 0), -1)

            cv2.imshow('Face Landmarks', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()