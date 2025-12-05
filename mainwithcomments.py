import cv2  # Import OpenCV for computer vision tasks
import mediapipe as mp  # Import MediaPipe for hand tracking
import pygame  # Import Pygame for game development
import random  # Import random for random number generation
import numpy as np  # Import NumPy for numerical operations

# Initialize Pygame
pygame.init()

# Screen dimensions and setup for game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Initialize the game window with specified dimensions
pygame.display.set_caption("Gesture Game")  # Set the title of the game window

# Define colors in RGB format
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
SELECTED_COLOR = (0, 200, 0)  # Color for selected camera button

# Load images for various game objects
player_img = pygame.image.load("assets/images/player_ship.png")  # Load player spaceship image
player_img = pygame.transform.scale(player_img, (50, 50))  # Scale image to fit the game

life_img = pygame.image.load("assets/images/life.png")  # Load life image
life_img = pygame.transform.scale(life_img, (30, 30))  # Scale life image

bullet_img = pygame.image.load("assets/images/bullet.png")  # Load bullet image
bullet_img = pygame.transform.scale(bullet_img, (10, 20))  # Scale bullet image

power_img = pygame.image.load("assets/images/power.png")  # Load power-up image
power_img = pygame.transform.scale(power_img, (10, 20))  # Scale power-up image

enemy_img = pygame.image.load("assets/images/enemy_ship.png")  # Load enemy spaceship image
enemy_img = pygame.transform.scale(enemy_img, (50, 50))  # Scale enemy image

beam_img = pygame.image.load("assets/images/beam.png")  # Load beam image
beam_img = pygame.transform.scale(beam_img, (30, 30))  # Scale beam image

background_img = pygame.image.load("assets/images/background.png")  # Load background image
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))  # Scale background image

# Game variables
player_x, player_y = WIDTH // 2, HEIGHT - 60  # Initial player position
player_speed = 10  # Player movement speed
bullets = []  # List to store bullets
enemy_ships = []  # List to store enemy ships
beams = []  # List to store power-up beams
score = 0  # Player score
lives = 3  # Player lives
cooldown = 200  # Bullet shooting cooldown in milliseconds
last_shot_time = 0  # Last time a bullet was shot
using_power_bullet = False  # Flag to check if a power-up bullet is in use
is_paused = False  # Flag to check if the game is paused
selected_camera = 0  # Index for the selected camera

# Hand gesture setup using MediaPipe
mp_hands = mp.solutions.hands  # Initialize MediaPipe hands module
hands = mp_hands.Hands(max_num_hands=1)  # Create hands object with a max of one hand to track

# Camera setup
cap = cv2.VideoCapture(0)  # Open the default camera (index 0)

# Set up clock for controlling frame rate
clock = pygame.time.Clock()

# Load sound effects
shoot_sound = pygame.mixer.Sound("assets/audio/shoot.wav")  # Load sound for shooting
explosion_sound = pygame.mixer.Sound("assets/audio/explosion.wav")  # Load explosion sound
beam_sound = pygame.mixer.Sound("assets/audio/beam.wav")  # Load beam sound
game_over_sound = pygame.mixer.Sound("assets/audio/game_over.wav")  # Load game over sound

# Background music
pygame.mixer.music.load("assets/audio/background_music.mp3")  # Load background music
pygame.mixer.music.play(-1, 0.0)  # Play the music indefinitely

def render_text(text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)  # Create a font object
    text_surface = font.render(text, True, color)  # Render text to an image
    screen.blit(text_surface, (x, y))  # Draw the text on the screen at specified position

def draw_buttons(buttons):
    for button in buttons:
        pygame.draw.rect(screen, button['color'], button['rect'])  # Draw the button rectangle
        render_text(button['text'], 28, WHITE, button['rect'].x + 10, button['rect'].y + 10)  # Draw text on the button

def button_click(buttons):
    for button in buttons:
        if button['rect'].collidepoint(pygame.mouse.get_pos()):  # Check if mouse is over button
            if button['action']:
                button['action']()  # Execute the action associated with the button

def draw_bullets():
    bullet_image = power_img if using_power_bullet else bullet_img  # Choose bullet image based on power-up status
    for bullet in bullets:
        screen.blit(bullet_image, (bullet[0], bullet[1]))  # Draw each bullet on the screen

def draw_enemies():
    for enemy in enemy_ships:
        screen.blit(enemy_img, (enemy[0], enemy[1]))  # Draw each enemy ship on the screen

def draw_beams():
    for beam in beams:
        screen.blit(beam_img, (beam[0], beam[1]))  # Draw each power-up beam on the screen

def draw_lives():
    for i in range(lives):
        screen.blit(life_img, (WIDTH - 40 - (i * 40), 10))  # Draw each life remaining

def shoot_bullet():
    global bullets, last_shot_time
    current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
    if current_time - last_shot_time >= cooldown:  # Check cooldown
        bullets.append([player_x + 22, player_y])  # Add a new bullet based on player position
        last_shot_time = current_time  # Update the last shot time
        shoot_sound.play()  # Play shooting sound

def update_bullets():
    global score
    bullets_to_remove = []  # List to track bullets that need to be removed
    for bullet in bullets[:]:  # Create a copy to iterate over
        bullet[1] -= 10  # Move the bullet up
        if bullet[1] < 0:  # If the bullet goes off the screen
            bullets_to_remove.append(bullet)  # Mark bullet for removal
            continue
        for enemy in enemy_ships[:]:  # Check for collision with enemies
            if (bullet[0] > enemy[0] and bullet[0] < enemy[0] + 50 and
                    bullet[1] > enemy[1] and bullet[1] < enemy[1] + 50):
                bullets_to_remove.append(bullet)  # Mark bullet for removal
                enemy_ships.remove(enemy)  # Remove enemy ship
                score += 10  # Increment score
                explosion_sound.play()  # Play explosion sound
                break
    # Remove all marked bullets after the loop
    for bullet in bullets_to_remove:
        bullets.remove(bullet)

def update_enemies():
    global lives
    if random.random() < 0.02:  # Randomly spawn enemies
        enemy_x = random.randint(0, WIDTH - 50)  # Random x position
        enemy_y = -50  # Start above the screen
        enemy_ships.append([enemy_x, enemy_y])  # Add enemy to the list
    for enemy in enemy_ships[:]:
        enemy[1] += 5  # Move down
        enemy[0] += random.randint(-2, 2)  # Add horizontal movement
        if enemy[1] > HEIGHT:  # If enemy goes off the screen
            enemy_ships.remove(enemy)  # Remove enemy ship
        if (player_x < enemy[0] + 50 and player_x + 50 > enemy[0] and
                player_y < enemy[1] + 50 and player_y + 50 > enemy[1]):
            enemy_ships.remove(enemy)  # Remove enemy ship if it intersects with player
            lives -= 1  # Decrement player lives
            explosion_sound.play()  # Play explosion sound
            if lives <= 0:
                game_over()

def update_beams():
    global player_speed, cooldown, using_power_bullet
    if random.random() < 0.005:  # Random spawn
        beam_x = random.randint(0, WIDTH - 30)  # Random x position for beam
        beam_y = -30  # Start above the screen
        beams.append([beam_x, beam_y])  # Add beam to the list
    for beam in beams[:]:
        beam[1] += 5  # Move down
        if beam[1] > HEIGHT:  # If beam goes off the screen
            beams.remove(beam)  # Remove beam
        if (beam[0] < player_x + 50 and
                beam[0] + 30 > player_x and
                beam[1] < player_y + 50 and
                beam[1] + 30 > player_y):
            beams.remove(beam)  # Remove beam if it intersects with player
            activate_beam()  # Activate power-up

def activate_beam():
    global player_speed, cooldown, using_power_bullet
    player_speed += 5  # Increase player speed
    using_power_bullet = True  # Set to using power-up bullet
    cooldown = 20  # Reduce shooting cooldown when collecting a beam
    beam_sound.play()  # Play beam sound
    
    # Create an event to reset after 5 seconds
    pygame.time.set_timer(pygame.USEREVENT + 1, 5000)  # Reset after 5 seconds

def reset_game():
    global player_x, player_y, score, bullets, enemy_ships, beams, lives, player_speed, cooldown, using_power_bullet
    player_x, player_y = WIDTH // 2, HEIGHT - 60  # Reset player position
    player_speed = 10  # Reset player speed
    cooldown = 200  # Reset cooldown
    bullets.clear()  # Clear bullets
    enemy_ships.clear()  # Clear enemies
    beams.clear()  # Clear beams
    score = 0  # Reset score
    lives = 3  # Reset lives
    using_power_bullet = False  # Reset power-up status

def fade_out_effect():
    for alpha in range(0, 300, 5):  # Create fade-out effect
        screen.blit(background_img, (0, 0))  # Use background image
        render_text("GAME OVER", 72, RED, WIDTH // 2.8, HEIGHT // 3)  # Display "GAME OVER" text
        render_text(f"Score: {score}", 36, WHITE, WIDTH // 2.5, HEIGHT // 2)  # Display score
        pygame.display.flip()  # Update display
        pygame.time.delay(30)  # Delay for effect

def game_over():
    global score, lives
    game_over_sound.play()  # Play game over sound
    fade_out_effect()  # Execute fade-out effect
    
    # Show end screen after fade out
    screen.blit(background_img, (0, 0))  # Use background image
    pygame.draw.rect(screen, GREEN, pygame.Rect(WIDTH // 2.5, HEIGHT // 1.5, 200, 50))  # Draw play again button
    render_text("Play Again", 36, WHITE, WIDTH // 2.5 + 50, HEIGHT // 1.5 + 10)  # Render button text
    pygame.display.flip()  # Update display
    
    waiting_for_click = True
    
    while waiting_for_click:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for quit event
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click
                mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
                if (WIDTH // 2.5 <= mouse_x <= WIDTH // 2.5 + 200 and 
                    HEIGHT // 1.5 <= mouse_y <= HEIGHT // 1.5 + 50):
                    reset_game()  # Reset game variables
                    game_loop()  # Start the game loop

def draw_hand_landmarks(image, hand_landmarks):
    for landmark in hand_landmarks.landmark:
        h, w, _ = image.shape  # Get the dimensions of the image
        cx, cy = int(landmark.x * w), int(landmark.y * h)  # Calculate landmark position
        cv2.circle(image, (cx, cy), 5, (255, 255, 0), -1)  # Draw circle at landmark position

    connections = mp_hands.HAND_CONNECTIONS  # Get connections for hand landmarks
    for connection in connections:
        cv2.line(image,
                 (int(hand_landmarks.landmark[connection[0]].x * w), int(hand_landmarks.landmark[connection[0]].y * h)),
                 (int(hand_landmarks.landmark[connection[1]].x * w), int(hand_landmarks.landmark[connection[1]].y * h)),
                 (0, 255, 0), 2)  # Draw lines between connected landmarks

def start_screen():
    global cap
    
    running = True
    
    buttons = [
        {'text': 'Start Game', 'rect': pygame.Rect(WIDTH // 3, HEIGHT // 2, WIDTH // 3, 50), 'color': GREEN, 'action': start_game},
        {'text': 'Camera 0', 'rect': pygame.Rect(WIDTH // 3, HEIGHT // 2 + 70, WIDTH // 3, 50), 'color': BLUE, 'action': lambda: select_camera(0)},
        {'text': 'Camera 1', 'rect': pygame.Rect(WIDTH // 3, HEIGHT // 2 + 140, WIDTH // 3, 50), 'color': BLUE, 'action': lambda: select_camera(1)},
    ]
    
    while running:
        screen.blit(background_img, (0, 0))  # Use background image
        render_text("Gesture Game", 54, WHITE, WIDTH // 4, HEIGHT // 3)  # Display title
        
        # Change button color if selected camera
        for button in buttons:
            if button['text'] == 'Camera 0' and selected_camera == 0:
                button['color'] = SELECTED_COLOR  # Highlight selected camera
            elif button['text'] == 'Camera 1' and selected_camera == 1:
                button['color'] = SELECTED_COLOR  # Highlight selected camera
            else:
                button['color'] = BLUE  # Reset to original color
        
        draw_buttons(buttons)  # Draw buttons
        
        pygame.display.flip()  # Update the display
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for quit event
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:  # Check for key pressed
                if event.key == pygame.K_ESCAPE:  # Exit if ESC is pressed
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
                button_click(buttons)  # Check if any button was clicked

def start_game():
    game_loop()  # Start the main game loop

def select_camera(camera_index):
    global cap, selected_camera
    selected_camera = camera_index  # Update the selected camera variable
    cap.release()  # Release the current camera
    cap = cv2.VideoCapture(camera_index)  # Capture from the selected camera

def game_loop():
    global player_x, player_y, score, bullets, enemy_ships, beams, lives, is_paused
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for quit event
                running = False
            
            if event.type == pygame.USEREVENT + 1:  # Check for custom event to deactivate beam
                deactivate_beam()
        
        keys = pygame.key.get_pressed()  # Get the current state of all keyboard keys
        
        if keys[pygame.K_ESCAPE]:  # Exit the game
            pygame.quit()
            exit()
        
        if keys[pygame.K_SPACE]:  # Pause or continue the game
            is_paused = not is_paused
        
        if is_paused:
            screen.blit(background_img, (0, 0))  # Use background image
            render_text("Paused", 70, RED, WIDTH // 2.7, HEIGHT // 3)  # Display paused text
            render_text("Press SPACE to Continue", 36, WHITE, WIDTH // 4, HEIGHT // 2)  # Instructions to continue
            render_text("Press ESC to Exit", 36, WHITE, WIDTH // 4, HEIGHT // 1.5)  # Instructions to exit
            pygame.display.flip()  # Update the display
            continue  # Skip the game update loop
        
        screen.blit(background_img, (0, 0))  # Draw background
        ret, frame = cap.read()  # Capture frame from camera
        
        if not ret:  # Check if the frame was captured successfully
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame to RGB for MediaPipe
        results = hands.process(frame_rgb)  # Process the frame for hand landmarks
        
        if results.multi_hand_landmarks:  # If hand landmarks are detected
            for hand_landmarks in results.multi_hand_landmarks:
                draw_hand_landmarks(frame, hand_landmarks)  # Draw hand landmarks
        
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        cv2.imshow("Hand Tracking", frame)  # Display the frame in a window
        
        if results.multi_hand_landmarks:  # If hand landmarks are detected
            landmarks = results.multi_hand_landmarks[0]  # Get the first hand's landmarks
            x = int(landmarks.landmark[mp_hands.HandLandmark.WRIST].x * WIDTH)  # Get wrist x position
            y = int(landmarks.landmark[mp_hands.HandLandmark.WRIST].y * HEIGHT)  # Get wrist y position
            player_x = min(max(WIDTH - x - 25, 0), WIDTH - 50)  # Update player x position
            player_y = min(max(y - 25, 0), HEIGHT - 50)  # Update player y position
            
            index_finger = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]  # Index finger tip landmark
            middle_finger = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]  # Middle finger tip landmark
            
            if abs(index_finger.x - middle_finger.x) < 0.03:  # Check if fingers are close together
                shoot_bullet()  # Shoot bullet
        
        update_bullets()  # Update bullet positions and check collisions
        update_enemies()  # Update enemy positions and check collisions
        update_beams()  # Update power-up beam positions
        
        screen.blit(player_img, (int(player_x), int(player_y)))  # Draw player image
        draw_bullets()  # Draw bullets
        draw_enemies()  # Draw enemies
        draw_beams()  # Draw power-up beams
        draw_lives()  # Draw the number of lives remaining
        
        render_text(f"Score: {score}", 36, WHITE, 10, 10)  # Display score
        
        pygame.display.flip()  # Update the display
        clock.tick(60)  # Cap the frame rate at 60 FPS
    
    pygame.quit()  # Quit Pygame
    cap.release()  # Release camera
    cv2.destroyAllWindows()  # Close all OpenCV windows

def deactivate_beam():
    global using_power_bullet, cooldown
    using_power_bullet = False  # Deactivate power-up bullet
    cooldown = 200  # Reset cooldown to default value

start_screen()  # Start the game with the start screen