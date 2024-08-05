from video_upload import upload_video
from frt_processing import process_frt, live_frt, needs_frt

class Chatbot:
    def __init__(self, questions):
        self.questions = questions
        self.personal_details = []
        self.symptom_responses = []
        self.history_responses = []
        self.current_step = 'personal_details'
        self.current_question_index = 0
        self.initial_greeting_done = False
        self.waiting_for_days = False  # New state variable

    def handle_message(self, message):
        # Initial greeting handling
        if not self.initial_greeting_done:
            self.initial_greeting_done = True
            return {"question": "Welcome! Let's start with some questions. What is your name?", "options": []}

        # Debug information
        print(f"Current step: {self.current_step}")
        print(f"Current question index: {self.current_question_index}")
        print(f"Message: {message}")

        if self.current_step == 'personal_details':
            # Validation for personal details
            if self.current_question_index == 1:  # Age question
                if not message.isdigit() or int(message) < 0:
                    return {"question": "Invalid age. Please enter a valid age (e.g., 18):", "options": []}
            elif self.current_question_index == 3:  # Weight question
                try:
                    weight = float(message)
                    if weight <= 0:
                        raise ValueError
                except ValueError:
                    return {"question": "Invalid weight. Please enter a valid weight in kg (e.g., 70.5):", "options": []}

            self.personal_details.append(message)
            self.current_question_index += 1
            if self.current_question_index >= len(self.questions['personal_details']):
                self.current_step = 'symptoms'
                self.current_question_index = 0
                return {"question": self.questions['symptoms'][self.current_question_index]['question'], "options": []}
            else:
                return {"question": self.questions['personal_details'][self.current_question_index], "options": []}

        elif self.current_step == 'symptoms':
            if self.waiting_for_days:
                try:
                    days = int(message)
                    if days < 0:
                        raise ValueError
                    self.symptom_responses[-1]['days'] = days  # Save days input
                    self.waiting_for_days = False  # Reset state
                except ValueError:
                    return {"question": "Invalid input. Please enter the number of days (e.g., 3):", "options": []}

                self.current_question_index += 1
                if self.current_question_index >= len(self.questions['symptoms']):
                    self.current_step = 'history'
                    self.current_question_index = 0
                    return {"question": self.questions['history'][self.current_question_index], "options": []}
                else:
                    return {"question": self.questions['symptoms'][self.current_question_index]['question'], "options": []}
            else:
                if message.lower() == 'yes':
                    days_question = "How many days have you been experiencing this symptom?"
                    self.symptom_responses.append({'response': True, 'days': None, 'days_required': self.questions['symptoms'][self.current_question_index]['days_required']})
                    self.waiting_for_days = True  # Set state to wait for days input
                    return {"question": days_question, "options": []}
                elif message.lower() == 'no':
                    self.symptom_responses.append({'response': False, 'days': 0, 'days_required': self.questions['symptoms'][self.current_question_index]['days_required']})
                    self.current_question_index += 1
                    if self.current_question_index >= len(self.questions['symptoms']):
                        self.current_step = 'history'
                        self.current_question_index = 0
                        return {"question": self.questions['history'][self.current_question_index], "options": []}
                    else:
                        return {"question": self.questions['symptoms'][self.current_question_index]['question'], "options": []}
                else:
                    return {"question": "Invalid input. Please answer with 'yes' or 'no':", "options": []}

        elif self.current_step == 'history':
            # Assuming all history questions require free-form text, we skip validation
            self.history_responses.append(message)
            self.current_question_index += 1
            if self.current_question_index >= len(self.questions['history']):
                self.current_step = 'complete'
                if needs_frt(self.symptom_responses):
                    return {"question": "Based on your responses, a Functional Reach Test (FRT) is recommended. Do you prefer to upload a video file or use a live camera for the FRT?", "options": ["upload", "live"]}
                return {"question": "No Functional Reach Test (FRT) is needed based on your responses.", "options": []}
            else:
                return {"question": self.questions['history'][self.current_question_index], "options": []}

        elif self.current_step == 'complete':
            # This section should already be properly handled, as it doesn't rely on automatic question advancement.
            pass
