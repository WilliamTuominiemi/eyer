import cv2

cam = cv2.VideoCapture(0)

frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

detector = cv2.SimpleBlobDetector_create()

def detect_eyes(img_gray, frame_height):
    coords = eye_cascade.detectMultiScale(img_gray, 1.3, 5)
    valid_coords = []
    for (x, y, w, h) in coords:
        if y + h <= frame_height / 2:
            new_y = int(y + (h * 0.25))
            new_h = int(h * 0.5)
            valid_coords.append((x, new_y, w, new_h))
    return valid_coords

def calculate_view_point(eye_rect, pupil_pos):
    ex, ey, ew, eh = eye_rect
    px, py = pupil_pos

    x_ratio = px - (ew / 2)
    y_ratio = py - (eh / 2)

    screen_x = int((frame_width / 2)+x_ratio *100)
    screen_y = int((frame_height / 2)+y_ratio *100)
    
    return (screen_x, screen_y)

while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

    threshold = 25
    gaze_point=(0,0)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        face_roi = gray_frame[y:y+h, x:x+w]
        face = frame[y:y+h, x:x+w]
        
        eyes = detect_eyes(face_roi, h)

        for (ex, ey, ew, eh) in eyes:
            eye_roi = cv2.equalizeHist(face_roi[ey:ey+eh, ex:ex+ew])
            _, eye_roi_bw = cv2.threshold(eye_roi, threshold, 255, cv2.THRESH_BINARY)
           
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 0, 255), 1)

            eye_roi_bw = cv2.erode(eye_roi_bw, None, iterations=2)
            eye_roi_bw = cv2.dilate(eye_roi_bw, None, iterations=4)
            eye_roi_bw = cv2.medianBlur(eye_roi_bw, 5)
           
            detector = cv2.SimpleBlobDetector_create()
            keypoints = detector.detect(eye_roi_bw)
           
            for keypoint in keypoints:
                center = (int(keypoint.pt[0]), int(keypoint.pt[1]))

                gaze_point = calculate_view_point((ex, ey, ew, eh), center)

                radius = int(keypoint.size / 2)
                cv2.circle(frame[y+ey:y+ey+eh, x+ex:x+ex+ew], center, radius, (0, 0, 255), 2)
   
    
    cv2.circle(frame, gaze_point, 10, (255, 0, 0), -1)

    out.write(frame) 

    flipped_frame = cv2.flip(frame, 1)

    cv2.imshow('Camera', flipped_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
out.release()
cv2.destroyAllWindows()