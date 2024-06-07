from tkinter import *
from threading import Thread
import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr

# Initialize speech recognition
r = sr.Recognizer()
engine = pyttsx3.init()

# Function to detect lane
def detect_lane(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Define region of interest (ROI) mask
    height, width = edges.shape
    mask = np.zeros_like(edges)
    roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    cv2.fillPoly(mask, [np.array(roi_vertices)], 255)
    masked_edges = cv2.bitwise_and(edges, mask)

    # Apply Hough line transform to detect lanes
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=50)

    # Process detected lines and draw them on the frame
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

    return frame, lines

# Function to provide audio cues based on lane detection
def provide_audio_cues(lines):
    if lines is not None:
        # Calculate the average x-coordinate of the detected lane lines' midpoints
        midpoints = []
        for line in lines:
            x1, _, x2, _ = line[0]
            mid_x = (x1 + x2) // 2
            midpoints.append(mid_x)
        average_mid_x = int(np.mean(midpoints))

        # Determine the direction based on the average midpoint position
        if average_mid_x < width // 2:
            engine.say("Turn left")
        elif average_mid_x > width // 2:
            engine.say("Turn right")
    else:
        engine.say("Walk straight")

    engine.runAndWait()

# Function to process voice command
def process_voice():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("Command:", command)
        engine.say("You said: " + command)
        engine.runAndWait()

        # Process the voice command here and provide directions based on the command
        if "left" in command:
            engine.say("Turning left")
            engine.runAndWait()
            # Add your logic for left turn here
            perform_left_turn()

        elif "right" in command:
            engine.say("Turning right")
            engine.runAndWait()
            # Add your logic for right turn here
            perform_right_turn()

        else:
            engine.say("Unknown command")
            engine.runAndWait()

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service:", e)

    # Schedule the next voice processing
    cv2.waitKey(1000)
    process_voice()

# Function to perform left turn
def perform_left_turn():
    # Add your logic for left turn based on lane detection here
    # For example, you can analyze the detected lane lines to determine the left turn

    # Example logic:
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1)

            # If the slope of a line is negative, it suggests a left turn
            if slope < 0:
                print("Performing left turn")

# Function to perform right turn
def perform_right_turn():
    # Add your logic for right turn based on lane detection here
    # For example, you can analyze the detected lane lines to determine the right turn

    # Example logic:
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1)

            # If the slope of a line is positive, it suggests a right turn
            if slope > 0:
                print("Performing right turn")

# Function to start the pathway lane detection
def start_detection():
    thread = Thread(target=run_pathway_lane_detection)
    thread.start()

# Function to run the pathway lane detection with voice cues
def run_pathway_lane_detection():
    # Initialize the video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Perform lane detection on the frame
        processed_frame, lines = detect_lane(frame)

        # Get the width of the frame
        height, width, _ = frame.shape

        # Display the processed frame
        cv2.imshow("Pathway Lane Detection", processed_frame)

        # Provide audio cues based on lane detection
        provide_audio_cues(lines)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and destroy the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Create the GUI window
window = Tk()
window.title("Pathway Lane Detection")
window.geometry("400x200")
window.configure(bg="#e3f2fd")

# Create the title label
title_label = Label(window, text="Pathway Lane Detection", font=("Arial", 18), bg="#e3f2fd", fg="#01579b")
title_label.pack(pady=20)

# Create the start button
start_button = Button(window, text="Start Detection", font=("Arial", 14), bg="#2196f3", fg="#ffffff",
                      activebackground="#1976d2", activeforeground="#ffffff", relief=FLAT, command=start_detection)
start_button.pack(pady=10)

# Run the GUI event loop
window.mainloop()
