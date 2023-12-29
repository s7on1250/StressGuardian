import cv2
import numpy as np
from scipy.signal import find_peaks

fps = 0

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Convert video of finger to signal. (Not used now)
def convert_to_signal(filename: str):
    global fps
    source = cv2.VideoCapture(filename)
    frame_width = int(source.get(3))
    frame_height = int(source.get(4))
    size = (frame_width, frame_height)
    signal = []
    fps = source.get(cv2.CAP_PROP_FPS)
    while True:
        ret, img = source.read()
        if not ret:
            break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        mean_color = np.mean(blurred, axis=(0, 1)).astype(int)
        signal.append(mean_color)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
    cv2.destroyAllWindows()
    source.release()
    return signal


# Convert video of face to signal
def convert_from_facial_video(filename: str):
    # Open the video file
    cap = cv2.VideoCapture(filename)
    # Initialize variables
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    heart_rates = []

    # Loop through each frame
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Convert frame to grayscale
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Extract region of interest (ROI) around the forehead
        face = face_classifier.detectMultiScale(
            img, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        for (x, y, w, h) in face:
            # Calculate forehead region based on face coordinates
            forehead_top = y
            forehead_bottom = int(y + 0.25 * h)
            forehead_left = x + w // 4
            forehead_right = x + 2 * w // 3
        roi = img[forehead_top:forehead_bottom, forehead_left:forehead_right]

        # Calculate average pixel intensity in the ROI
        average_intensity = np.mean(roi)

        # Append average intensity to the heart rate list
        heart_rates.append(average_intensity)


        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()

    # Perform signal processing to find peaks (heartbeats)
    peaks, _ = find_peaks(heart_rates, distance=int(fps * 0.25))

    # Calculate heart rate in beats per minute (BPM)
    # heart_rate_bpm = 60 / np.mean(np.diff(peaks) / fps)

    return np.array(peaks)


# Converting signal to hrv characteristics
def get_metrics(peaks: list):
    rr_intervals = []
    for i in range(1, len(peaks)):
        rr_intervals.append((peaks[i] - peaks[i - 1]) / fps * 1000)
    rr_intervals = sorted(rr_intervals)
    mean_rr = np.mean(rr_intervals)
    median_rr = np.median(rr_intervals)
    sdrr = np.std(rr_intervals)
    rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    sdsd = np.std(np.diff(rr_intervals))
    sdrr_rmssd = sdrr / rmssd
    return [mean_rr, median_rr, sdrr, rmssd, sdsd, sdrr_rmssd]
