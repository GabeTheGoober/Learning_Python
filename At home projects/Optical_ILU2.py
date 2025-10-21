import pygame
import math
import sys

pygame.init()

# Get available display modes and screen info
try:
    display_info = pygame.display.Info()
    # Get desktop resolution
    DESKTOP_WIDTH = display_info.current_w
    DESKTOP_HEIGHT = display_info.current_h
    
    # Set window size to 80% of desktop size by default
    SCREEN_WIDTH = int(DESKTOP_WIDTH * 0.8)
    SCREEN_HEIGHT = int(DESKTOP_HEIGHT * 0.8)
    
    # Ensure minimum size
    SCREEN_WIDTH = max(SCREEN_WIDTH, 800)
    SCREEN_HEIGHT = max(SCREEN_HEIGHT, 600)
    
except pygame.error:
    # Fallback resolution if cannot get display info
    SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768

# Modified display initialization
try:
    # Start in windowed mode first
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Enhanced Optical Illusions - Concentric Patterns")
    
    # Add toggle fullscreen function
    def toggle_fullscreen():
        global screen, SCREEN_WIDTH, SCREEN_HEIGHT
        is_fullscreen = bool(screen.get_flags() & pygame.FULLSCREEN)
        if is_fullscreen:
            # Switch to windowed
            screen = pygame.display.set_mode((int(DESKTOP_WIDTH * 0.8), 
                                           int(DESKTOP_HEIGHT * 0.8)), 
                                           pygame.RESIZABLE)
            SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        else:
            # Switch to fullscreen
            screen = pygame.display.set_mode((DESKTOP_WIDTH, DESKTOP_HEIGHT), 
                                           pygame.FULLSCREEN)
            SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        return not is_fullscreen

except pygame.error as e:
    print(f"Error initializing display: {e}")
    pygame.quit()
    sys.exit(1)

# Global constants
FPS = 60
STROBE_INTERVAL = 3  # Frames between flips (~20Hz at 60 FPS)
BUTTON_WIDTH, BUTTON_HEIGHT = 300, 50
BUTTON_COLOR = (128, 128, 128)  # Gray
BUTTON_HOVER_COLOR = (160, 160, 160)
TEXT_COLOR = (255, 255, 255)  # White
WARNING_COLOR = (255, 0, 0)  # Red
INSTR_COLOR = (255, 255, 0)  # Yellow for instructions

# Initialize clock after display
clock = pygame.time.Clock()

# FIXED FONT SIZES - No scaling, just reasonable sizes
font_large = pygame.font.SysFont("consolas", 36)   # Fixed size
font_medium = pygame.font.SysFont("consolas", 20)  # Fixed size  
font_small = pygame.font.SysFont("consolas", 12)   # Fixed size

# Global strobe control
strobe_state = False
strobe_counter = 0

def update_strobe():
    global strobe_state, strobe_counter
    strobe_counter += 1
    if strobe_counter >= STROBE_INTERVAL:
        strobe_state = not strobe_state
        strobe_counter = 0
    bg_color = (255, 255, 255) if strobe_state else (0, 0, 0)  # White or black
    fg_color = (0, 0, 0) if strobe_state else (255, 255, 255)  # Opposite
    return bg_color, fg_color

# SIMPLIFIED SCALING - Much less aggressive
def scale_size(base_size):
    # Only scale for very large screens, otherwise use base size
    if SCREEN_HEIGHT > 1200:
        return int(base_size * SCREEN_HEIGHT / 1080)
    else:
        return base_size

# ENHANCED ILLUSION DRAWING FUNCTIONS WITH CONCENTRIC PATTERNS

def draw_vertical_motion(screen, fg_color, offset):
    stripe_width = 30
    for x in range(-SCREEN_WIDTH, SCREEN_WIDTH * 2, stripe_width * 2):
        pygame.draw.rect(screen, fg_color, (x + offset, 0, stripe_width, SCREEN_HEIGHT))
    return (offset + 4) % (stripe_width * 2)

def draw_spiral(screen, fg_color, angle):
    """Enhanced spiral with multiple layers and smoother animation"""
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45
    
    # Draw 3 intertwined spirals for richer effect
    for spiral_num in range(3):
        points = []
        spiral_offset = spiral_num * 120  # 120 degree offset between spirals
        
        # Logarithmic spiral for more natural curve
        a = 8  # Starting radius
        k = 0.08  # Growth factor
        
        for i in range(400):
            current_angle = angle + spiral_offset + i * 0.9
            rad_angle = math.radians(current_angle)
            # Logarithmic spiral: r = a * e^(k*angle)
            radius = a * math.exp(k * i * 0.05)
            
            if radius > max_radius:
                break
                
            x = center_x + radius * math.cos(rad_angle)
            y = center_y + radius * math.sin(rad_angle)
            points.append((x, y))
        
        if len(points) > 1:
            # Vary thickness for depth
            thickness = max(1, 3 - spiral_num)
            pygame.draw.lines(screen, fg_color, False, points, thickness)
    
    return angle + 3

def draw_radial(screen, fg_color, frame):
    """Enhanced radial with multiple frequency pulsing"""
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45
    
    for i, angle in enumerate(range(0, 360, 10)):
        rad = math.radians(angle)
        # Multi-frequency pulsing for stronger effect
        pulse1 = max_radius * 0.6 + max_radius * 0.2 * math.sin(frame * 0.03)
        pulse2 = max_radius * 0.3 + max_radius * 0.1 * math.sin(frame * 0.07 + i)
        pulse = (pulse1 + pulse2) / 2
        
        end_x = center_x + pulse * math.cos(rad)
        end_y = center_y + pulse * math.sin(rad)
        
        # Varying line thickness for enhanced effect
        thickness = 2 + math.sin(frame * 0.1 + i * 0.5)
        pygame.draw.line(screen, fg_color, (center_x, center_y), 
                        (end_x, end_y), max(1, int(thickness)))
    
    return frame + 1

def draw_checkerboard(screen, fg_color, offset_x, offset_y):
    square_size = 40
    alt_color = (0, 0, 0) if fg_color == (255, 255, 255) else (255, 255, 255)
    
    # Calculate grid dimensions based on screen size
    cols = int(SCREEN_WIDTH / square_size) + 4
    rows = int(SCREEN_HEIGHT / square_size) + 4
    
    start_x = -square_size * 2 + offset_x
    start_y = -square_size * 2 + offset_y
    
    for row in range(-rows//2, rows//2):
        for col in range(-cols//2, cols//2):
            color = fg_color if (row + col) % 2 == 0 else alt_color
            x = start_x + (col * square_size)
            y = start_y + (row * square_size)
            pygame.draw.rect(screen, color, (x, y, square_size, square_size))
    
    return (offset_x + 3) % square_size, (offset_y + 3) % square_size

def draw_breathing_square(screen, fg_color, size, growing):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_size = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.8
    min_size = 50
    
    rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
    pygame.draw.rect(screen, fg_color, rect)
    
    if growing:
        size += 3
        if size > max_size:
            growing = False
    else:
        size -= 3
        if size < min_size:
            growing = True
    return size, growing

def draw_tunnel(screen, fg_color, frame):
    """Enhanced tunnel with more circles and pulsing effect"""
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2
    
    # Draw more circles for stronger tunnel effect
    for i, radius in enumerate(range(15, max_radius, 20)):
        # Add pulsing that varies with circle and time
        pulse = radius + 12 * math.sin(frame * 0.06 + i * 0.1)
        
        # Alternate colors for adjacent circles
        current_color = fg_color
        if i % 2 == 1:
            # Create a mid-tone gray for alternating circles
            current_color = (128, 128, 128) if fg_color == (255, 255, 255) else (128, 128, 128)
        
        pygame.draw.circle(screen, current_color, (center_x, center_y), int(pulse), 2)
    
    return frame + 1

def draw_hering(screen, fg_color):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_length = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4
    
    # Draw radiating lines
    for angle in range(0, 180, 8):
        rad = math.radians(angle)
        end_x = center_x + max_length * 1.5 * math.cos(rad)
        end_y = center_y + max_length * 1.5 * math.sin(rad)
        pygame.draw.line(screen, fg_color, (center_x, center_y), (end_x, end_y), 1)
    
    # Draw vertical lines that should appear curved
    line_spacing = 150
    for x_offset in [-line_spacing, line_spacing]:
        start_pos = (center_x + x_offset, center_y - max_length)
        end_pos = (center_x + x_offset, center_y + max_length)
        pygame.draw.line(screen, fg_color, start_pos, end_pos, 3)

def draw_ebbinghaus(screen, fg_color):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    # Left group - central circle with large surrounding circles
    left_x = center_x - 200
    pygame.draw.circle(screen, fg_color, (left_x, center_y), 60)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        surr_x = left_x + 180 * math.cos(rad)
        surr_y = center_y + 180 * math.sin(rad)
        pygame.draw.circle(screen, fg_color, (int(surr_x), int(surr_y)), 40)
    
    # Right group - same central circle with small surrounding circles
    right_x = center_x + 200
    pygame.draw.circle(screen, fg_color, (right_x, center_y), 60)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        surr_x = right_x + 180 * math.cos(rad)
        surr_y = center_y + 180 * math.sin(rad)
        pygame.draw.circle(screen, fg_color, (int(surr_x), int(surr_y)), 20)

# NEW ENHANCED ILLUSIONS WITH CONCENTRIC PATTERNS

def draw_concentric_circles(screen, fg_color, frame):
    """Multiple concentric circles with pulsing effect"""
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45
    
    # Draw 12 concentric circles
    num_circles = 12
    for i in range(num_circles):
        # Space circles evenly
        base_radius = (i + 1) * (max_radius / num_circles)
        
        # Add pulsing effect that varies by circle
        pulse = base_radius + 8 * math.sin(frame * 0.05 + i * 0.5)
        
        # Alternate colors for adjacent circles
        current_color = fg_color
        if i % 2 == 1:
            # Use mid-gray for alternating circles
            current_color = (128, 128, 128) if fg_color == (255, 255, 255) else (128, 128, 128)
        
        pygame.draw.circle(screen, current_color, (center_x, center_y), 
                          int(pulse), 2)
    
    return frame + 1

def draw_peripheral_drift(screen, fg_color, frame):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4
    
    for radius in range(20, int(max_radius), 30):
        for angle in range(0, 360, 45):
            rad = math.radians(angle + frame * 2)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            # Create asymmetric patterns for drift illusion
            for i in range(4):
                segment_angle = rad + i * math.pi/2
                start_x = x + 10 * math.cos(segment_angle)
                start_y = y + 10 * math.sin(segment_angle)
                end_x = x + 25 * math.cos(segment_angle)
                end_y = y + 25 * math.sin(segment_angle)
                
                pygame.draw.line(screen, fg_color, (start_x, start_y), 
                               (end_x, end_y), 3)
    
    return frame + 1

def draw_hermann_grid(screen, fg_color, frame):
    grid_size = 80
    offset_x = (frame // 2) % grid_size
    offset_y = (frame // 2) % grid_size
    
    # Draw grid lines
    for x in range(-grid_size, SCREEN_WIDTH + grid_size, grid_size):
        pygame.draw.line(screen, fg_color, (x + offset_x, 0), 
                        (x + offset_x, SCREEN_HEIGHT), 4)
    
    for y in range(-grid_size, SCREEN_HEIGHT + grid_size, grid_size):
        pygame.draw.line(screen, fg_color, (0, y + offset_y), 
                        (SCREEN_WIDTH, y + offset_y), 4)
    
    return frame + 1

def draw_ambiguous_figure(screen, fg_color, frame):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    size = 150 + 20 * math.sin(frame * 0.05)
    
    # Draw ambiguous figure that can be seen as two different things
    pygame.draw.ellipse(screen, fg_color, 
                       (center_x - size, center_y - size//3, size*2, size//2))
    
    # Add elements that create ambiguity
    for i in range(3):
        angle = frame * 0.02 + i * math.pi/3
        x1 = center_x + size * 0.7 * math.cos(angle)
        y1 = center_y + size * 0.7 * math.sin(angle)
        x2 = center_x + size * 0.3 * math.cos(angle + math.pi/6)
        y2 = center_y + size * 0.3 * math.sin(angle + math.pi/6)
        
        pygame.draw.line(screen, fg_color, (x1, y1), (x2, y2), 4)
    
    return frame + 1

def draw_enhanced_radial(screen, fg_color, frame):
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45
    
    for i, angle in enumerate(range(0, 360, 8)):
        rad = math.radians(angle)
        # Multi-frequency pulsing for stronger effect
        pulse1 = max_radius * 0.6 + max_radius * 0.2 * math.sin(frame * 0.03)
        pulse2 = max_radius * 0.3 + max_radius * 0.1 * math.sin(frame * 0.07 + i)
        pulse = (pulse1 + pulse2) / 2
        
        end_x = center_x + pulse * math.cos(rad)
        end_y = center_y + pulse * math.sin(rad)
        
        # Varying line thickness for enhanced effect
        thickness = 2 + math.sin(frame * 0.1 + i * 0.5)
        pygame.draw.line(screen, fg_color, (center_x, center_y), 
                        (end_x, end_y), max(1, int(thickness)))
    
    return frame + 1

# ENHANCED HYPNOTIC SPIRAL ILLUSIONS
def draw_hypnotic_spiral(screen, fg_color, state):
    """
    Advanced hypnotic spiral with multiple layers and direction reversal
    """
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.45
    
    # Unpack state
    current_angle, direction, start_time, spiral_type = state
    current_time = pygame.time.get_ticks()
    elapsed_seconds = (current_time - start_time) / 1000.0
    
    # Reverse direction every 20 seconds
    if elapsed_seconds >= 20:
        direction *= -1
        start_time = current_time
        elapsed_seconds = 0
    
    # Calculate rotation speed
    rotation_speed = 2 * direction
    current_angle += rotation_speed
    
    # Clear previous frame
    screen.fill((0, 0, 0) if fg_color == (255, 255, 255) else (255, 255, 255))
    
    # Draw multiple layered spirals for hypnotic effect
    spiral_offsets = [0, 120, 240]  # Three spirals offset by 120 degrees
    
    for offset in spiral_offsets:
        points = []
        # Logarithmic spiral parameters for smooth, expanding curve
        a = 10  # Starting radius
        k = 0.1  # Growth factor
        
        # Generate spiral points
        for i in range(800):
            angle_rad = math.radians(current_angle + offset + i * 0.5)
            # Logarithmic spiral equation: r = a * e^(k * θ)
            radius = a * math.exp(k * i * 0.05)
            
            if radius > max_radius:
                break
                
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            points.append((x, y))
        
        # Draw the spiral with varying thickness for depth effect
        if len(points) > 1:
            for i in range(len(points) - 1):
                # Vary line thickness - thicker at center, thinner at edges
                progress = i / len(points)
                thickness = int(5 * (1 - progress * 0.7))
                thickness = max(1, thickness)
                
                # Draw segment
                pygame.draw.line(screen, fg_color, points[i], points[i + 1], thickness)
    
    # Add pulsing effect to central area
    pulse = 0.8 + 0.2 * math.sin(elapsed_seconds * 2)
    center_radius = 15 * pulse
    pygame.draw.circle(screen, fg_color, (center_x, center_y), int(center_radius))
    
    # Update state
    state[0] = current_angle
    state[1] = direction
    state[2] = start_time
    
    return state

def draw_alternating_spirals(screen, fg_color, state):
    """
    Dual spirals that create stronger motion aftereffects
    """
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4
    
    current_angle, direction, start_time, spiral_count = state
    current_time = pygame.time.get_ticks()
    elapsed_seconds = (current_time - start_time) / 1000.0
    
    # Reverse direction every 20 seconds
    if elapsed_seconds >= 20:
        direction *= -1
        start_time = current_time
        elapsed_seconds = 0
    
    current_angle += 3 * direction
    
    # Draw multiple intertwined spirals
    spiral_offsets = [0, 120, 240]  # Three spirals offset by 120 degrees
    
    for offset in spiral_offsets:
        points = []
        a = 8
        k = 0.08
        
        for i in range(600):
            angle_rad = math.radians(current_angle + offset + i * 0.6)
            radius = a * math.exp(k * i * 0.05)
            
            if radius > max_radius:
                break
                
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, fg_color, False, points, 2)
    
    state[0] = current_angle
    state[1] = direction
    state[2] = start_time
    
    return state

def draw_multi_concentric(screen, fg_color, frame):
    """
    Multiple sets of concentric circles for complex tunnel effect
    """
    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4
    
    # Draw 3 sets of concentric circles at different positions
    positions = [
        (center_x, center_y),  # Center
        (center_x - 150, center_y - 100),  # Top-left
        (center_x + 150, center_y + 100)   # Bottom-right
    ]
    
    for pos_x, pos_y in positions:
        # Draw 8 concentric circles at each position
        for i in range(8):
            radius = 20 + i * 25
            # Add pulsing that varies by position and circle
            pulse = radius + 10 * math.sin(frame * 0.04 + i * 0.3 + pos_x * 0.001)
            
            pygame.draw.circle(screen, fg_color, (int(pos_x), int(pos_y)), 
                              int(pulse), 2)
    
    return frame + 1

# Simple strobes
def bw_strobe():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        bg_color, _ = update_strobe()
        screen.fill(bg_color)
        pygame.display.flip()
        clock.tick(FPS)
    return True

def rainbow_strobe():
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue
    color_index = 0
    frame_count = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        # Change color every 10 frames for smooth transition
        if frame_count % 10 == 0:
            color_index = (color_index + 1) % len(colors)
        
        screen.fill(colors[color_index])
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1
    
    return True

# Generic illusion runner
def run_illusion(draw_func, instruction, init_state=None):
    state = init_state if init_state is not None else [0]
    running = True
    
    # Create instruction surface
    instr_surface = font_medium.render(instruction, True, INSTR_COLOR)
    instr_rect = instr_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        # Update strobe and get colors
        bg_color, fg_color = update_strobe()
        screen.fill(bg_color)
        
        # Draw the illusion
        if draw_func == draw_vertical_motion:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_spiral:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_radial:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_checkerboard:
            state[0], state[1] = draw_func(screen, fg_color, state[0], state[1])
        elif draw_func == draw_breathing_square:
            state[0], state[1] = draw_func(screen, fg_color, state[0], state[1])
        elif draw_func == draw_tunnel:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func in [draw_hering, draw_ebbinghaus]:
            draw_func(screen, fg_color)
        elif draw_func == draw_peripheral_drift:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_hermann_grid:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_ambiguous_figure:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_enhanced_radial:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func in [draw_hypnotic_spiral, draw_alternating_spirals]:
            state = draw_func(screen, fg_color, state)
        elif draw_func == draw_concentric_circles:
            state[0] = draw_func(screen, fg_color, state[0])
        elif draw_func == draw_multi_concentric:
            state[0] = draw_func(screen, fg_color, state[0])
        
        # Draw instruction
        screen.blit(instr_surface, instr_rect)
        pygame.display.flip()
        clock.tick(FPS)
    
    return True

# Illusion wrappers
def vertical_motion(): 
    return run_illusion(draw_vertical_motion, "Stare at center for 30s, then look at wall to see it melt!", [0])

def spiral_motion(): 
    return run_illusion(draw_spiral, "Enhanced spiral - multiple layers for stronger effect!", [0])

def radial_motion(): 
    return run_illusion(draw_radial, "Stare at center, then look at surface to see it breathe!", [0])

def checkerboard_motion(): 
    return run_illusion(draw_checkerboard, "Stare at pattern, then look away to see ghostly motion!", [0, 0])

def breathing_square(): 
    return run_illusion(draw_breathing_square, "Stare at square, then look away to see size aftereffects!", [100, True])

def tunnel_effect(): 
    return run_illusion(draw_tunnel, "Enhanced tunnel - more circles with pulsing effect!", [0])

def hering_illusion(): 
    return run_illusion(draw_hering, "Stare at the illusion - the straight lines will appear curved!")

def ebbinghaus_illusion(): 
    return run_illusion(draw_ebbinghaus, "Stare at the circles - they appear different sizes!")

# NEW ENHANCED ILLUSION WRAPPERS
def peripheral_drift(): 
    return run_illusion(draw_peripheral_drift, "Look at center, notice motion in periphery!", [0])

def hermann_grid(): 
    return run_illusion(draw_hermann_grid, "See ghostly dots at intersections? Look away!", [0])

def ambiguous_figure(): 
    return run_illusion(draw_ambiguous_figure, "Does the shape flip between interpretations?", [0])

def enhanced_radial(): 
    return run_illusion(draw_enhanced_radial, "Enhanced radial - stronger breathing effect!", [0])

def concentric_circles():
    return run_illusion(draw_concentric_circles, "Multiple concentric circles with pulsing effect!", [0])

def multi_concentric():
    return run_illusion(draw_multi_concentric, "Multiple sets of concentric circles - complex tunnel!", [0])

# ENHANCED HYPNOTIC SPIRAL WRAPPERS
def hypnotic_spiral():
    initial_state = [
        0,      # current_angle
        1,      # direction (1 for clockwise, -1 for counterclockwise)
        pygame.time.get_ticks(),  # start_time
        0       # spiral_type (can be used for variations)
    ]
    return run_illusion(draw_hypnotic_spiral, 
                       "Advanced hypnotic spiral - reverses direction every 20s!",
                       initial_state)

def alternating_spirals():
    initial_state = [
        0,      # current_angle  
        1,      # direction
        pygame.time.get_ticks(),  # start_time
        3       # spiral_count
    ]
    return run_illusion(draw_alternating_spirals,
                       "Multiple intertwined spirals - strong motion aftereffects!",
                       initial_state)

# Main menu
def main_menu():
    global strobe_state, strobe_counter
    strobe_state = False
    strobe_counter = 0

    warning_pattern = "◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘"
    
    # Create text surfaces
    warnings = [
        font_small.render(warning_pattern, True, WARNING_COLOR),
        font_small.render("[ Warning May Cause Seizures ] ", True, WARNING_COLOR),
        font_small.render(warning_pattern, True, WARNING_COLOR)
    ]
    
    title_text = font_large.render("Enhanced Optical Illusions", True, TEXT_COLOR)
    
    # Button configurations - UPDATED WITH NEW CONCENTRIC PATTERNS
    button_configs = [
        ("Vertical Motion", vertical_motion),
        ("Spiral Motion", spiral_motion),
        ("Hypnotic Spiral", hypnotic_spiral),
        ("Alternating Spirals", alternating_spirals),
        ("Radial Motion", radial_motion),
        ("Enhanced Radial", enhanced_radial),
        ("Concentric Circles", concentric_circles),
        ("Multi Concentric", multi_concentric),
        ("Tunnel Effect", tunnel_effect),
        ("Peripheral Drift", peripheral_drift),
        ("Checkerboard", checkerboard_motion),
        ("Hermann Grid", hermann_grid),
        ("Breathing Square", breathing_square),
        ("Hering Lines", hering_illusion),
        ("Ebbinghaus", ebbinghaus_illusion),
        ("Ambiguous Figure", ambiguous_figure),
        ("BW Strobe", bw_strobe),
        ("Rainbow Strobe", rainbow_strobe),
    ]
    
    # FIXED BUTTON SIZES
    button_width = 280
    button_height = 45
    button_spacing = 55
    
    # Create buttons - now in 4 columns to accommodate more illusions
    buttons = []
    col1_x = SCREEN_WIDTH // 8 - button_width // 2
    col2_x = 3 * SCREEN_WIDTH // 8 - button_width // 2
    col3_x = 5 * SCREEN_WIDTH // 8 - button_width // 2
    col4_x = 7 * SCREEN_WIDTH // 8 - button_width // 2
    
    # Distribute buttons across 4 columns
    buttons_per_col = (len(button_configs) + 3) // 4
    y_start = SCREEN_HEIGHT // 2 - (buttons_per_col * button_spacing) // 2
    
    for i, (label, handler) in enumerate(button_configs):
        if i < buttons_per_col:
            x = col1_x
            y = y_start + i * button_spacing
        elif i < 2 * buttons_per_col:
            x = col2_x
            y = y_start + (i - buttons_per_col) * button_spacing
        elif i < 3 * buttons_per_col:
            x = col3_x
            y = y_start + (i - 2 * buttons_per_col) * button_spacing
        else:
            x = col4_x
            y = y_start + (i - 3 * buttons_per_col) * button_spacing
            
        rect = pygame.Rect(x, y, button_width, button_height)
        text = font_medium.render(label, True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        buttons.append((rect, text, text_rect, handler))
    
    # Exit button
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - 100, button_width, button_height)
    exit_text = font_medium.render("Exit", True, TEXT_COLOR)
    exit_text_rect = exit_text.get_rect(center=exit_rect.center)
    
    # Instructions - FIXED POSITIONS
    instructions = [
        "Click any button to start illusion",
        "Press F to toggle fullscreen",
        "Press ESC to quit",
        "Drag window edges to resize"
    ]
    
    instr_surfaces = []
    for i, text in enumerate(instructions):
        surf = font_medium.render(text, True, (128, 128, 128))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180 + i * 30))
        instr_surfaces.append((surf, rect))
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_f:
                    toggle_fullscreen()
                    # Recreate menu after fullscreen toggle
                    return main_menu()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check illusion buttons
                for rect, _, _, handler in buttons:
                    if rect.collidepoint(mouse_pos):
                        handler()
                        # Return to menu after illusion
                        return main_menu()
                
                # Check exit button
                if exit_rect.collidepoint(mouse_pos):
                    cleanup()
                    sys.exit()
        
        # Draw everything
        screen.fill((0, 0, 0))  # Black background for menu
        
        # Draw warnings - FIXED POSITIONS
        for i, warn_surface in enumerate(warnings):
            warn_rect = warn_surface.get_rect(center=(SCREEN_WIDTH // 2, 50 + i * 20))
            screen.blit(warn_surface, warn_rect)
        
        # Draw title - FIXED POSITION
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Draw buttons
        for rect, text, text_rect, _ in buttons:
            color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            screen.blit(text, text_rect)
        
        # Draw exit button
        exit_color = BUTTON_HOVER_COLOR if exit_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, exit_color, exit_rect)
        screen.blit(exit_text, exit_text_rect)
        
        # Draw instructions
        for surf, rect in instr_surfaces:
            screen.blit(surf, rect)
        
        pygame.display.flip()
        clock.tick(FPS)

# Add cleanup handler
def cleanup():
    """Safely quit pygame"""
    try:
        pygame.quit()
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Add event handling for window resize
def handle_window_events(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    
    if event.type == pygame.VIDEORESIZE:
        if not (screen.get_flags() & pygame.FULLSCREEN):
            SCREEN_WIDTH = max(event.w, 800)
            SCREEN_HEIGHT = max(event.h, 600)
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            # Return to main menu to refresh layout
            return main_menu()
    
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_f:  # F key toggles fullscreen
            toggle_fullscreen()
            return main_menu()

# Modify main guard to include error handling
if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        cleanup()