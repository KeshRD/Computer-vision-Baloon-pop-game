import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import math
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()
width, height = 1280, 720
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gesture Balloon Shooter")

# Load pop sound
pop_sound = pygame.mixer.Sound(pygame.mixer.Sound("pop.mp3"))  # Optional: use a .wav file

# Balloon colors
balloon_colors = [(255, 0, 0), (255, 105, 180), (0, 191, 255), (0, 255, 127), (255, 215, 0)]

# Font
font = pygame.font.SysFont("Arial", 36)

# Webcam
cap = cv2.VideoCapture(0)

# Game variables
score = 0
balloons = []
shoot_cooldown = 0

# Pointer variables
pointer_pos = (width // 2, height // 2)

# Balloon class
class Balloon:
    def __init__(self):
        self.x = random.randint(50, width - 50)
        self.y = height + random.randint(0, 300)
        self.radius = random.randint(30, 45)
        self.color = random.choice(balloon_colors)
        self.speed = random.uniform(1.5, 3.5)

    def move(self):
        self.y -= self.speed

    def draw(self):
        # Draw balloon body (oval)
        pygame.draw.ellipse(win, self.color, (self.x - self.radius, self.y - 1.5 * self.radius, 2 * self.radius, 2.5 * self.radius))
        # Draw string
        pygame.draw.line(win, (0, 0, 0), (self.x, self.y + self.radius), (self.x, self.y + self.radius + 30), 2)

# Detect pinch gesture
def is_pinch(landmarks):
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    distance = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
    return distance < 0.04

# Main loop
running = True
while running:
    win.fill((245, 245, 245))

    # Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_landmarks = results.multi_hand_landmarks
    pinch = False

    if hand_landmarks:
        for hand in hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            index_finger = hand.landmark[8]
            pointer_pos = (int(index_finger.x * width), int(index_finger.y * height))
            if is_pinch(hand):
                pinch = True

    # Draw pointer
    pygame.draw.circle(win, (0, 0, 0), pointer_pos, 8)

    # Add new balloons
    if len(balloons) < 7:
        balloons.append(Balloon())

    # Move and draw balloons
    for balloon in balloons[:]:
        balloon.move()
        balloon.draw()
        # Remove if off screen
        if balloon.y + balloon.radius < 0:
            balloons.remove(balloon)

    # Handle shooting
    if pinch and shoot_cooldown <= 0:
        shoot_cooldown = 20
        for balloon in balloons[:]:
            bx, by = balloon.x, balloon.y
            br = balloon.radius
            # Check if pointer hits balloon
            if math.hypot(pointer_pos[0] - bx, pointer_pos[1] - by) < br:
                balloons.remove(balloon)
                score += 1
                # pop_sound.play()  # Uncomment if you have a sound
                break
    else:
        shoot_cooldown -= 1

    # Show score
    score_text = font.render(f"Score: {score}", True, (50, 50, 50))
    win.blit(score_text, (30, 30))

    # Show Pygame window
    pygame.display.update()

    # Exit on 'q' key (OpenCV window for fallback)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
