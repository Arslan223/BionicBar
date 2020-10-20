import cv2
import face_recognition
import random
import subprocess
import time
import tkinter


def say_text(text):
    subprocess.call('say ' + text, shell=True)


def inputbox(title, message, button_text):
    root = tkinter.Tk()
    root.title(title)
    root.resizable(False, False)

    label = tkinter.Label(text=message)
    label.pack()

    text = ''

    def on_return(e=None):
        nonlocal text
        text = textbox.get()
        root.destroy()

    textbox = tkinter.Entry(width=40)
    textbox.bind('<Return>', on_return)
    textbox.pack()
    textbox.focus_set()

    button = tkinter.Button(text=button_text, command=on_return)
    button.pack()

    root.mainloop()

    return text


data = [{}]

video_capture = cv2.VideoCapture(0)

known_face_encodings = []
known_face_names = []
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                if data[0][name][1]:
                    if time.time() - data[0][name][1] > 10:
                        data[0][name][0] = None
                        data[0][name][1] = None
                        say_text("Bye, "+name)
                        time.sleep(5)
                else:
                    table = random.randint(1, 10)
                    data[0][name][0] = table
                    data[0][name][1] = time.time()
                    say_text("Hello! Your table is "+str(table))
                    continue
            elif len(face_encodings) == 1:
                time.sleep(1)
                cv2.imwrite("temp_frame.jpg", frame)
                temp_image = face_recognition.load_image_file("temp_frame.jpg")
                try:
                    temp_face_encoding = face_recognition.face_encodings(temp_image)[0]
                except:
                    continue
                say_text("Hello, I don't know who you are. Can you please write your name.")
                read = inputbox("Добавление пользователя", "Введите Имя", "Далее")
                if read in ("", "Unknown"):
                    continue
                else:
                    known_face_names.append(read)
                    known_face_encodings.append(temp_face_encoding)
                    data[0].update({read: [None, None]})
                    print(data)
                    continue
            else:
                continue
            face_names.append(name)

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if name != "Unknown":
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(
                frame,
                name+"; "+str(data[0][name][0]) + " tb",
                (left + 6, bottom - 6),
                font,
                1.0,
                (255, 255, 255),
                1
            )

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
