import cv2
import mediapipe as mp
import numpy as np
import json
import time

def validate_posture(landmarks):
    issues = []
    mp_pose = mp.solutions.pose
    
    # Define the landmark indices for the body parts
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

    # Calculate midpoints for shoulders and hips
    shoulder_midpoint = [(left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2]
    hip_midpoint = [(left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2]

    # Check for posture issues
    if not np.isclose(left_ankle[1], right_ankle[1], atol=0.05):
        issues.append("Feet should be flat on the floor and aligned.")
        
    if shoulder_midpoint[0] < hip_midpoint[0] - 0.05 or shoulder_midpoint[0] > hip_midpoint[0] + 0.05:
        issues.append("Shoulders should be aligned with the hips.")

    return issues

def process_frt(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(video_path)
    pose_correct = False
    pose_start_time = None
    initial_position = None
    initial_hip_position = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_height, image_width, _ = frame.shape
        frame = cv2.resize(frame, (520, 750))
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            if not pose_correct:
                issues = validate_posture(results.pose_landmarks.landmark)
                if issues:
                    pose_start_time = None
                    for i, issue in enumerate(issues):
                        cv2.putText(image, issue, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, "Posture: Incorrect", (10, 50 + len(issues) * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    if pose_start_time is None:
                        pose_start_time = time.time()
                    elif time.time() - pose_start_time >= 1.5:
                        pose_correct = True
                        initial_position = [results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                            results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                        initial_hip_position = [(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value].x + 
                                                results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2, 
                                                (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value].y + 
                                                results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2]

    cap.release()
    cv2.destroyAllWindows()
    return "FRT processing completed. Please review the results."

def live_frt():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)  # Use camera index 0 for the default camera
    pose_correct = False
    pose_start_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            if not pose_correct:
                issues = validate_posture(results.pose_landmarks.landmark)
                if issues:
                    pose_start_time = None
                    for i, issue in enumerate(issues):
                        cv2.putText(image, issue, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, "Posture: Incorrect", (10, 50 + len(issues) * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    if pose_start_time is None:
                        pose_start_time = time.time()
                    elif time.time() - pose_start_time >= 1.5:
                        pose_correct = True

        cv2.imshow('Functional Reach Test - Live Feed', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return "FRT processing completed. Please review the results."

def needs_frt(symptom_responses):
    # Load questions and criteria from JSON file
    with open('questions.json', 'r') as file:
        data = json.load(file)

    questions = {
        'symptoms': data['symptoms']
    }
    
    for symptom in questions['symptoms']:
        question = symptom['question']
        days_required = symptom['days_required']
        
        for response in symptom_responses:
            if response['response']:
                if response['days'] >= days_required:
                    return True
    return False

