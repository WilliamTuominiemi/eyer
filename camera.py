import cv2

cam = cv2.VideoCapture(0)

frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

def detect_eyes(img_gray, frame_height):
    coords = eye_cascade.detectMultiScale(img_gray, 1.3, 5)
    valid_coords = []
    for (x, y, w, h) in coords:
        if y + h <= frame_height / 2:
            new_y = int(y + (h * 0.25))
            new_h = int(h * 0.75)
            valid_coords.append((x, new_y, w, new_h))
    return valid_coords

while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        face_roi = gray_frame[y:y+h, x:x+w]
        face = frame[y:y+h, x:x+w]
        
        eyes = detect_eyes(face_roi, h)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 0, 255), 2)


    out.write(frame) 

    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
out.release()
cv2.destroyAllWindows()