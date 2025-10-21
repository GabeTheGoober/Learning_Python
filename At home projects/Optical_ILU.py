import turtle as t
import time
import math

def screen_setup():
    screen = t.Screen()
    screen.title("Strobing Optical Illusion")
    screen.bgcolor("black")
    screen.setup(width=1.0, height=1.0)
    screen.tracer(0)  # Turn off animation for instant drawing
    return screen

def create_button(x, y, label, click_handler):
    """Create a clickable button with text"""
    button = t.Turtle()
    button.shape("square")
    button.shapesize(1.5, 4)  # Size the button
    button.color("white", "gray")
    button.penup()
    button.goto(x, y)
    button.onclick(lambda x, y: click_handler())
    
    # Add text to button
    text = t.Turtle()
    text.hideturtle()
    text.penup()
    text.goto(x, y-10)
    text.color("white")
    text.write(label, align="center", font=("Consolas", 12, "normal"))
    
    return button, text

def return_to_menu():
    """Return to main menu from any illusion"""
    t.clearscreen()
    main_menu()

def add_return_handler():
    """Add click to return functionality"""
    screen = t.Screen()
    screen.onclick(lambda x, y: return_to_menu())
    
    # Add return instruction
    instruction = t.Turtle()
    instruction.hideturtle()
    instruction.penup()
    instruction.goto(0, -300)
    instruction.color("gray")
    instruction.write("Click anywhere to return to menu", align="center", font=("Consolas", 14, "normal"))
    return instruction

def breathing_square_illusion():
    """Breathing Square Illusion with strobing effect"""
    t.clearscreen()
    screen = t.Screen()
    screen.bgcolor("black")
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    
    frame = 0
    strobe_counter = 0
    
    def draw_frame():
        nonlocal frame, strobe_counter
        drawer.clear()
        
        # Strobing background effect
        if strobe_counter % 10 == 0:  # Every 10 frames
            screen.bgcolor("white")
        elif strobe_counter % 5 == 0:  # Every 5 frames
            screen.bgcolor("black")
        
        # Calculate breathing effect
        breath_size = 100 + 30 * math.sin(frame * 0.1)
        
        # Draw the breathing square
        drawer.goto(-breath_size/2, -breath_size/2)
        drawer.pendown()
        drawer.color("black" if screen.bgcolor() == ("white",) else "white")
        drawer.begin_fill()
        for _ in range(4):
            drawer.forward(breath_size)
            drawer.left(90)
        drawer.end_fill()
        drawer.penup()
        
        frame += 1
        strobe_counter += 1
        screen.update()
        screen.ontimer(draw_frame, 50)  # 20 FPS
    
    draw_frame()
    add_return_handler()

def ebbinghaus_illusion():
    """Ebbinghaus Illusion with strobing effect"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    
    strobe_state = False
    frame = 0
    
    def draw_frame():
        nonlocal strobe_state, frame
        
        # Strobe effect
        if frame % 6 == 0:  # Change every 6 frames
            strobe_state = not strobe_state
            screen.bgcolor("white" if strobe_state else "black")
        
        drawer.clear()
        
        # Colors that contrast with background
        dot_color = "black" if strobe_state else "white"
        
        # Draw first central circle surrounded by large circles
        drawer.goto(-150, 0)
        drawer.color(dot_color)
        drawer.dot(80)  # Central circle
        
        # Surround with large circles
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            drawer.goto(-150 + 120 * math.cos(rad), 0 + 120 * math.sin(rad))
            drawer.dot(40)
        
        # Draw second central circle surrounded by small circles  
        drawer.goto(150, 0)
        drawer.color(dot_color)
        drawer.dot(80)  # Central circle (same size as first)
        
        # Surround with small circles
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            drawer.goto(150 + 120 * math.cos(rad), 0 + 120 * math.sin(rad))
            drawer.dot(20)
        
        frame += 1
        screen.update()
        screen.ontimer(draw_frame, 80)  # Slower strobe
    
    draw_frame()
    add_return_handler()

def hering_illusion():
    """Hering Illusion with strobing effect"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    
    strobe_state = False
    frame = 0
    
    def draw_frame():
        nonlocal strobe_state, frame
        
        # Strobe effect
        if frame % 8 == 0:
            strobe_state = not strobe_state
            screen.bgcolor("white" if strobe_state else "black")
        
        drawer.clear()
        line_color = "black" if strobe_state else "white"
        drawer.color(line_color)
        
        # Draw radiating lines
        for angle in range(0, 180, 12):  # Fewer lines for better performance
            drawer.goto(0, 0)
            drawer.setheading(angle)
            drawer.pendown()
            drawer.forward(250)
            drawer.penup()
        
        # Draw straight vertical lines (will appear curved)
        drawer.pensize(3)
        for x in [-80, 80]:
            drawer.goto(x, -180)
            drawer.pendown()
            drawer.setheading(90)
            drawer.forward(360)
            drawer.penup()
        
        frame += 1
        screen.update()
        screen.ontimer(draw_frame, 70)
    
    draw_frame()
    add_return_handler()

def wall_melt_effect():
    """Wall melting effect with intense strobing"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    drawer.pensize(2)
    
    frame = 0
    
    def draw_frame():
        nonlocal frame
        drawer.clear()
        
        # Intense strobing background
        if frame % 3 == 0:
            screen.bgcolor("white")
        else:
            screen.bgcolor("black")
        
        line_color = "black" if screen.bgcolor() == ("white",) else "white"
        drawer.color(line_color)
        
        # Draw melting vertical lines
        for x in range(-300, 301, 25):
            drawer.penup()
            drawer.goto(x, -250)
            drawer.pendown()
            
            # Create melting/wavy effect
            for y in range(-250, 251, 15):
                offset = 15 * math.sin(y * 0.02 + frame * 0.3) * math.sin(x * 0.01 + frame * 0.1)
                drawer.goto(x + offset, y)
        
        frame += 1
        screen.update()
        screen.ontimer(draw_frame, 40)  # Fast animation
    
    draw_frame()
    add_return_handler()

def spiral_illusion():
    """Rotating spiral illusion with strobing"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    drawer.pensize(2)
    
    frame = 0
    angle = 0
    
    def draw_frame():
        nonlocal frame, angle
        
        # Strobe background
        if frame % 5 == 0:
            screen.bgcolor("white")
        elif frame % 3 == 0:
            screen.bgcolor("black")
        
        drawer.clear()
        spiral_color = "black" if screen.bgcolor() == ("white",) else "white"
        drawer.color(spiral_color)
        
        # Draw rotating spiral
        drawer.goto(0, 0)
        for i in range(100):
            drawer.forward(i * 0.3)
            drawer.left(20 + angle * 0.1)
        
        angle += 2
        frame += 1
        screen.update()
        screen.ontimer(draw_frame, 50)
    
    draw_frame()
    add_return_handler()

def bw_strobe():
    """Simple but intense black and white strobe"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(1)  # Keep tracer on for smooth strobing
    
    strobe_state = False
    
    def strobe():
        nonlocal strobe_state
        strobe_state = not strobe_state
        screen.bgcolor("white" if strobe_state else "black")
        screen.ontimer(strobe, 60)  # Fast strobe
    
    strobe()
    add_return_handler()

def zigzag_strobe():
    """Zigzag pattern with strobing effect"""
    t.clearscreen()
    screen = t.Screen()
    screen.tracer(0)
    
    drawer = t.Turtle()
    drawer.speed(0)
    drawer.hideturtle()
    drawer.penup()
    drawer.pensize(3)
    
    frame = 0
    
    def draw_frame():
        nonlocal frame
        
        # Strobe background
        if frame % 4 == 0:
            screen.bgcolor("white")
        else:
            screen.bgcolor("black")
        
        drawer.clear()
        line_color = "black" if screen.bgcolor() == ("white",) else "white"
        drawer.color(line_color)
        
        # Draw zigzag patterns
        for y in range(-200, 201, 40):
            drawer.penup()
            drawer.goto(-300, y)
            drawer.pendown()
            
            x = -300
            direction = 1
            while x < 300:
                drawer.goto(x, y + 20 * direction)
                x += 30
                direction *= -1
                drawer.goto(x, y + 20 * direction)
        
        frame += 1
        screen.update()
        screen.ontimer(draw_frame, 60)
    
    draw_frame()
    add_return_handler()

def main_menu():
    """Create the main menu with illusion options"""
    t.clearscreen()
    screen = t.Screen()
    screen.bgcolor("black")
    screen.tracer(0)
    
    # Clear any existing event handlers
    screen.onclick(None)
    
    # Warning message
    warning = t.Turtle()
    warning.hideturtle()
    warning.penup()
    warning.goto(0, 250)
    warning.color("red")
    warning.write("WARNING: May cause seizures or discomfort!", align="center", font=("Consolas", 16, "bold"))
    
    # Title
    title = t.Turtle()
    title.hideturtle()
    title.penup()
    title.goto(0, 180)
    title.color("white")
    title.write("Optical Illusions", align="center", font=("Consolas", 24, "bold"))
    
    # Create menu buttons in two columns
    buttons = []
    
    left_column = [
        (0, 100, "Breathing Square", breathing_square_illusion),
        (0, 50, "Ebbinghaus Illusion", ebbinghaus_illusion),
        (0, 0, "Hering Illusion", hering_illusion),
        (0, -50, "Wall Melt", wall_melt_effect),
    ]
    
    right_column = [
        (200, 100, "Spiral", spiral_illusion),
        (200, 50, "Zigzag Strobe", zigzag_strobe),
        (200, 0, "BW Strobe", bw_strobe),
        (200, -50, "Exit", t.bye)
    ]
    
    for x, y, label, handler in left_column + right_column:
        button, text = create_button(x, y, label, handler)
        buttons.append((button, text))
    
    # Instructions
    instructions = t.Turtle()
    instructions.hideturtle()
    instructions.penup()
    instructions.goto(0, -150)
    instructions.color("gray")
    instructions.write("Click any button to start illusion", align="center", font=("Consolas", 14, "normal"))
    
    screen.update()

# Setup and start the application
screen = screen_setup()
main_menu()

# Main loop
t.mainloop()