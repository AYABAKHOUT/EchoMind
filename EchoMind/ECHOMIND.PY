import pygame
import random
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Emotion definitions: color and sound file
EMOTIONS = {
    "joy": [(255, 223, 0), "joy.wav"],         # yellow
    "sadness": [(70, 130, 180), "sadness.wav"],  # steel blue
    "fear": [(138, 43, 226), "fear.wav"],      # blue violet
    "anger": [(220, 20, 60), "anger.wav"]      # crimson
}

SEQUENCE_LENGTH = 3
WINDOW_SIZE = (600, 500)
FPS = 30
FONT_NAME = "Segoe UI"

# Load sounds
def load_sounds():
    sounds = {}
    for emotion, (_, filename) in EMOTIONS.items():
        try:
            sounds[emotion] = pygame.mixer.Sound(filename)
        except:
            sounds[emotion] = pygame.mixer.Sound(buffer=b'\x00' * 100)
    return sounds

SOUNDS = load_sounds()

# Setup Pygame window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("EchoMind")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont(FONT_NAME, 36)
font_medium = pygame.font.SysFont(FONT_NAME, 26)
font_small = pygame.font.SysFont(FONT_NAME, 20)

# Generate a random emotion sequence
def generate_sequence(length=SEQUENCE_LENGTH):
    return random.choices(list(EMOTIONS.keys()), k=length)

# Play the emotion sequence
def play_sequence(sequence):
    for emotion in sequence:
        color, _ = EMOTIONS[emotion]
        screen.fill(color)
        pygame.display.flip()
        sound = SOUNDS[emotion]
        sound.play()
        time.sleep(0.9)
        sound.stop()
        screen.fill((30, 30, 30))
        pygame.display.flip()
        time.sleep(0.3)

# Create a custom input dialog
class EmotionInputDialog:
    def __init__(self, root, sequence_length):
        self.root = root
        self.top = tk.Toplevel(self.root)
        self.top.title("🎧 Repeat the Sequence")
        self.top.geometry("350x300")
        self.top.configure(bg="#f0f0f0")

        ttk.Label(self.top, text="Enter emotions in order: (joy, sadness, fear, anger)", font=("Segoe UI", 11, "bold")).pack(pady=10)

        self.entries = []
        for i in range(sequence_length):
            entry = ttk.Entry(self.top, font=("Segoe UI", 10))
            entry.pack(pady=3)
            self.entries.append(entry)

        ttk.Label(self.top, text="What was the overall emotion?", font=("Segoe UI", 11, "bold")).pack(pady=10)
        self.emotion_entry = ttk.Entry(self.top, font=("Segoe UI", 10))
        self.emotion_entry.pack(pady=5)

        ttk.Button(self.top, text="Submit", command=self.submit).pack(pady=10)
        self.result = None

    def submit(self):
        emotions = [entry.get().strip().lower() for entry in self.entries]
        overall = self.emotion_entry.get().strip().lower()
        self.result = (emotions, overall)
        self.top.destroy()

# Evaluate user response
def evaluate(player_seq, true_seq, guessed_emotion, correct_emotion):
    correct = player_seq == true_seq
    emotion_correct = guessed_emotion == correct_emotion
    return correct, emotion_correct

# Render centered text on screen helper
def draw_centered_text(surface, text, font, color, y_pos):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(WINDOW_SIZE[0]//2, y_pos))
    surface.blit(text_obj, text_rect)

# Show results inside the Pygame window
def show_result_screen(correct_seq, seq, correct_emotion, emotion_correct, score):
    screen.fill((20, 20, 40))

    draw_centered_text(screen, "\U0001F3AE Round Result", font_large, (255, 255, 255), 60)

    if correct_seq:
        seq_text = "Sequence: Correct \u2705"
        seq_color = (0, 255, 100)
    else:
        seq_text = f"Sequence: Incorrect \u274C (Correct was: {' - '.join(seq)})"
        seq_color = (255, 80, 80)
    draw_centered_text(screen, seq_text, font_medium, seq_color, 150)

    if emotion_correct:
        emotion_text = "Emotion Guess: Correct \U0001F60A"
        emotion_color = (0, 255, 100)
    else:
        emotion_text = f"Emotion Guess: Incorrect \U0001F615 (Was: {correct_emotion.capitalize()})"
        emotion_color = (255, 80, 80)
    draw_centered_text(screen, emotion_text, font_medium, emotion_color, 200)

    draw_centered_text(screen, f"Your Score: {score} / 6 \U0001F31F", font_medium, (255, 255, 150), 280)
    draw_centered_text(screen, "Press SPACE to continue...", font_small, (200, 200, 200), 420)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(FPS)

# Show welcome screen with rules
def show_welcome_screen():
    screen.fill((10, 10, 30))
    draw_centered_text(screen, "\U0001F44B Welcome to EchoMind!", font_large, (255, 255, 255), 100)
    draw_centered_text(screen, "Remember the sequence of colors and sounds", font_small, (200, 200, 200), 160)
    draw_centered_text(screen, "Then repeat the sequence and guess the emotion", font_small, (200, 200, 200), 190)
    draw_centered_text(screen, "Press SPACE to start!", font_medium, (255, 255, 100), 300)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        clock.tick(FPS)

# Main game function
def main():
    root = tk.Tk()
    root.withdraw()

    show_welcome_screen()

    score = 0

    for _ in range(3):
        sequence = generate_sequence()
        dominant_emotion = random.choice(sequence)
        play_sequence(sequence)

        dialog = EmotionInputDialog(root, SEQUENCE_LENGTH)
        root.wait_window(dialog.top)
        if dialog.result is None:
            break

        user_sequence, user_emotion = dialog.result
        correct_seq, emotion_correct = evaluate(user_sequence, sequence, user_emotion, dominant_emotion)

        if correct_seq:
            score += 1
        if emotion_correct:
            score += 1

        show_result_screen(correct_seq, sequence, dominant_emotion, emotion_correct, score)

    screen.fill((10, 10, 20))
    draw_centered_text(screen, "\U0001F3C1 Game Over! \U0001F3C1", font_large, (255, 255, 255), 150)
    draw_centered_text(screen, f"Your final score: {score} / 6 \U0001F31F", font_medium, (255, 255, 150), 220)
    draw_centered_text(screen, "Thanks for playing EchoMind!", font_medium, (180, 180, 180), 280)
    draw_centered_text(screen, "Close window to exit.", font_small, (150, 150, 150), 420)
    pygame.display.flip()

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
