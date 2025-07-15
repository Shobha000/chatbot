import tkinter as tk
from tkinter import scrolledtext
import re
import datetime
import random
import pyttsx3
import speech_recognition as sr

# --- Voice Engine Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Speech Recognition Setup ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

# --- Memory ---
conversation_history = []

# --- Jokes ---
jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the computer go to therapy? It had too many bytes of trauma.",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the math book sad? Because it had too many problems."
]

# --- Pattern Matching ---
def match_pattern(text, patterns):
    return any(re.search(p, text) for p in patterns)

# --- Analyze Preferences ---
def analyze_preferences():
    prefs = {"joke": 0, "math": 0, "time": 0}
    for sender, msg in conversation_history:
        if sender == "You":
            if "joke" in msg.lower():
                prefs["joke"] += 1
            if re.search(r"[\d\+\-\*/\(\)]", msg):
                prefs["math"] += 1
            if "time" in msg.lower() or "date" in msg.lower():
                prefs["time"] += 1
    return prefs

# --- Math Evaluation ---
def extract_expression(text):
    try:
        expr = re.findall(r"[\d\.\+\-\*/\(\)\s]+", text)
        result = eval("".join(expr))
        return f"The result is {result}"
    except:
        return "Sorry, I couldn't calculate that."

# --- Bot Response Logic ---
def get_response(user_input):
    user_input = user_input.lower()
    prefs = analyze_preferences()

    user_name = None
    for sender, message in conversation_history:
        match = re.search(r"my name is (\w+)", message.lower())
        if match:
            user_name = match.group(1).capitalize()
            break

    match = re.search(r"my name is (\w+)", user_input)
    if match:
        name = match.group(1).capitalize()
        conversation_history.append(("Bot", f"Nice to meet you, {name}!"))
        return f"Nice to meet you, {name}!"

    if "what about" in user_input or "that" in user_input:
        last_user = next((msg for sender, msg in reversed(conversation_history) if sender == "You"), "")
        return f"Are you asking something related to: '{last_user}'?"

    if "previous chat" in user_input or "history" in user_input:
        return "Here’s what we’ve talked about:\n" + "\n".join([f"{s}: {m}" for s, m in conversation_history[-5:]])

    if match_pattern(user_input, [r"\bhi\b", r"\bhello\b", r"\bhey\b"]):
        if user_name:
            return f"Hello again, {user_name}! How can I help today?"
        else:
            return "Hello! What’s your name?"

    elif match_pattern(user_input, [r"how are you", r"how's it going"]):
        return "I'm doing great, thank you!"

    elif match_pattern(user_input, [r"your name", r"who are you"]):
        return "I'm your chatbot assistant!"

    elif match_pattern(user_input, [r"\btime\b", r"what.*time"]):
        now = datetime.datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}."

    elif match_pattern(user_input, [r"\bdate\b", r"what.*date"]):
        today = datetime.date.today()
        return f"Today is {today.strftime('%A, %B %d, %Y')}."

    elif match_pattern(user_input, [r"joke", r"make me laugh", r"tell.*joke"]):
        reply = random.choice(jokes)
        if prefs["joke"] > 2:
            reply += " 😄 You really love jokes!"
        return reply

    elif match_pattern(user_input, [r"[\d\s\+\-\*/\(\)]+", r"calculate", r"solve", r"what.*\d"]):
        return extract_expression(user_input)

    elif match_pattern(user_input, [r"help", r"what can you do"]):
        msg = "I can chat, tell jokes, do math, and tell you the time or date."
        if prefs["joke"] > 0:
            msg += " You seem to enjoy jokes, so try saying 'Tell me a joke'!"
        if prefs["math"] > 0:
            msg += " I can solve math like '12 + 45 * 3'."
        return msg

    elif match_pattern(user_input, [r"bye", r"exit", r"quit", r"see you"]):
        farewell = "Goodbye!"
        if prefs["math"] > 1:
            farewell += " Don't forget to practice your math!"
        elif prefs["joke"] > 1:
            farewell += " Hope you keep laughing!"
        return farewell

    else:
        return "Hmm, I’m not sure what you mean. Can you clarify?"

# --- GUI Class ---
class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(" CHATBOT")

        # Layout frames
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10, padx=10)

        self.chat_frame = tk.Frame(main_frame)
        self.chat_frame.pack(side=tk.LEFT)

        self.memory_frame = tk.Frame(main_frame)

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, width=60, height=20, font=("Arial", 12))
        self.chat_area.pack()
        self.chat_area.config(state=tk.DISABLED)

        # Memory area (initially hidden)
        tk.Label(self.memory_frame, text="Memory", font=("Arial", 12, "bold")).pack()
        self.memory_area = scrolledtext.ScrolledText(self.memory_frame, wrap=tk.WORD, width=30, height=20, font=("Arial", 11), bg="#f0f0f0")
        self.memory_area.pack()
        self.memory_area.config(state=tk.DISABLED)
        self.memory_visible = False  # Initially hidden

        # Entry
        self.entry = tk.Entry(root, font=("Arial", 14))
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.send_message)

        # Buttons
        actions_frame = tk.Frame(root)
        actions_frame.pack(pady=5)

        tk.Button(actions_frame, text="Send", command=self.send_message, width=10).grid(row=0, column=0, padx=5)
        tk.Button(actions_frame, text="🎤 Speak", command=self.voice_input, width=10).grid(row=0, column=1, padx=5)
        tk.Button(actions_frame, text="🧠 Memory", command=self.toggle_memory, width=10).grid(row=0, column=2, padx=5)
        tk.Button(actions_frame, text="Exit", command=root.quit, width=10).grid(row=0, column=3, padx=5)

    def display_message(self, sender, message):
        conversation_history.append((sender, message))
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def send_message(self, event=None):
        user_msg = self.entry.get()
        if user_msg.strip() == "":
            return
        self.entry.delete(0, tk.END)
        self.display_message("You", user_msg)
        response = get_response(user_msg)
        self.display_message("Bot", response)
        speak(response)

    def voice_input(self):
        with mic as source:
            self.display_message("Bot", "Listening...")
            audio = recognizer.listen(source)
        try:
            user_msg = recognizer.recognize_google(audio)
            self.display_message("You", user_msg)
            response = get_response(user_msg)
            self.display_message("Bot", response)
            speak(response)
        except sr.UnknownValueError:
            self.display_message("Bot", "Sorry, I didn’t catch that.")
        except sr.RequestError:
            self.display_message("Bot", "Speech service is unavailable.")

    def toggle_memory(self):
        if self.memory_visible:
            self.memory_frame.pack_forget()
            self.memory_visible = False
        else:
            self.update_memory()
            self.memory_frame.pack(side=tk.RIGHT, padx=10)
            self.memory_visible = True

    def update_memory(self):
        self.memory_area.config(state=tk.NORMAL)
        self.memory_area.delete(1.0, tk.END)
        if not conversation_history:
            self.memory_area.insert(tk.END, "No memory yet.")
        else:
            for sender, message in conversation_history[-10:]:
                self.memory_area.insert(tk.END, f"{sender}: {message}\n")
        self.memory_area.config(state=tk.DISABLED)

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()
