import turtle as t
import time
import math

# Global strobe control
strobe_state = False
last_strobe_time = 0

def screen_setup():
    screen = t.Screen()
    screen.title("Strobing Optical Illusion")
    screen.bgcolor("black")
    screen.setup(width=1.0, height=1.0)
    screen.tracer(0)
    return screen

def create_button(x, y, label, click_handler):
    """Create a clickable button with text on the side"""
    button = t.Turtle()
    button.shape("square")
    button.shapesize(1.5, 1.5)
    button.color("white", "gray")
    button.penup()
    button.goto(x, y)
    button.onclick(lambda x, y: click_handler())
    
    text = t.Turtle()
    text.hideturtle()
    text.penup()
    text.goto(x + 25, y - 5)
    text.color("white")
    text.write(label, align="left", font=("Consolas", 12, "normal"))
    return button, text

def clear_and_start(illusion_func):
    """Clear screen and start illusion"""
    try:
        # Clear all existing turtles
        for turtle in t.Screen().turtles():
            turtle.hideturtle()
            turtle.clear()
        t.Screen().clear()
        t.bgcolor("black")
        illusion_func()
    except Exception as e:
        print(f"Error starting illusion: {e}")

def update_strobe():
    """Update strobe background - called by all illusions"""
    global strobe_state, last_strobe_time
    current_time = time.time()
    if current_time - last_strobe_time >= 0.05:
        strobe_state = not strobe_state
        t.bgcolor("white" if strobe_state else "black")
        last_strobe_time = current_time
    return "black" if strobe_state else "white"

def create_illusion(draw_func, instruction):
    """Generic illusion runner with strobe"""
    try:
        screen = t.Screen()
        screen.clear()
        screen.tracer(0)
        
        # Create single turtle for drawing
        drawer = t.Turtle()
        drawer.speed(0)
        drawer.hideturtle()
        drawer.penup()
        
        # Add instruction with same turtle
        drawer.goto(0, -350)
        drawer.color("yellow")
        drawer.write(instruction, align="center", font=("Consolas", 14, "normal"))
        drawer.color("white")  # Reset color for main drawing
        
        running = True
        def stop_illusion():
            nonlocal running
            running = False
        
        screen.onkey(stop_illusion, "Escape")
        screen.listen()
        
        def frame():
            if not running:
                drawer.clear()
                main_menu()
                return
            color = update_strobe()
            draw_func(drawer, color)
            screen.update()
            screen.ontimer(frame, 16)
        
        frame()
        
    except Exception as e:
        print(f"Error in illusion: {e}")
        main_menu()

# ILLUSION DRAWING FUNCTIONS
def draw_vertical_motion(drawer, color):
    """Vertical moving stripes"""
    stripe_width = 30
    if not hasattr(draw_vertical_motion, 'offset'):
        draw_vertical_motion.offset = 0
    
    drawer.clear()
    drawer.color(color)
    
    for x in range(-400, 400, stripe_width * 2):
        drawer.penup()
        drawer.goto(x + draw_vertical_motion.offset, -300)
        drawer.pendown()
        drawer.begin_fill()
        for _ in range(2):
            drawer.forward(stripe_width)
            drawer.left(90)
            drawer.forward(600)
            drawer.left(90)
        drawer.end_fill()
    
    draw_vertical_motion.offset = (draw_vertical_motion.offset + 4) % (stripe_width * 2)

def draw_spiral(drawer, color):
    """Rotating spiral"""
    if not hasattr(draw_spiral, 'angle'):
        draw_spiral.angle = 0
    
    drawer.clear()
    drawer.color(color)
    drawer.pensize(2)
    
    drawer.goto(0, 0)
    drawer.pendown()
    for i in range(150):
        drawer.forward(i * 0.2)
        drawer.left(15)
    drawer.penup()
    
    draw_spiral.angle += 4

def draw_radial(drawer, color):
    """Expanding/contracting radial lines"""
    if not hasattr(draw_radial, 'frame'):
        draw_radial.frame = 0
    
    drawer.clear()
    drawer.color(color)
    drawer.pensize(2)
    
    for angle in range(0, 360, 15):
        drawer.goto(0, 0)
        drawer.setheading(angle)
        drawer.pendown()
        pulse = 200 + 50 * math.sin(draw_radial.frame * 0.1)
        drawer.forward(pulse)
        drawer.penup()
    
    draw_radial.frame += 1

def draw_checkerboard(drawer, color):
    """Moving checkerboard"""
    if not hasattr(draw_checkerboard, 'offset_x'):
        draw_checkerboard.offset_x = 0
        draw_checkerboard.offset_y = 0
    
    drawer.clear()
    square_size = 40
    alt_color = "black" if color == "white" else "white"
    
    for row in range(-8, 8):
        for col in range(-8, 8):
            drawer.color(color if (row + col) % 2 == 0 else alt_color)
            drawer.penup()
            drawer.goto((col * square_size) + draw_checkerboard.offset_x, 
                       (row * square_size) + draw_checkerboard.offset_y)
            drawer.pendown()
            drawer.begin_fill()
            for _ in range(4):
                drawer.forward(square_size)
                drawer.left(90)
            drawer.end_fill()
    
    draw_checkerboard.offset_x = (draw_checkerboard.offset_x + 4) % square_size
    draw_checkerboard.offset_y = (draw_checkerboard.offset_y + 4) % square_size

def draw_breathing_square(drawer, color):
    """Breathing square"""
    if not hasattr(draw_breathing_square, 'size'):
        draw_breathing_square.size = 0
        draw_breathing_square.growing = True
    
    drawer.clear()
    drawer.color(color)
    
    drawer.goto(-draw_breathing_square.size/2, -draw_breathing_square.size/2)
    drawer.pendown()
    drawer.begin_fill()
    for _ in range(4):
        drawer.forward(draw_breathing_square.size)
        drawer.left(90)
    drawer.end_fill()
    
    if draw_breathing_square.growing:
        draw_breathing_square.size += 3
        if draw_breathing_square.size > 300:
            draw_breathing_square.growing = False
    else:
        draw_breathing_square.size -= 3
        if draw_breathing_square.size < 50:
            draw_breathing_square.growing = True

def draw_tunnel(drawer, color):
    """Tunnel effect"""
    if not hasattr(draw_tunnel, 'frame'):
        draw_tunnel.frame = 0
    
    drawer.clear()
    drawer.color(color)
    drawer.pensize(2)
    
    for radius in range(20, 300, 30):
        pulse = radius + 10 * math.sin(draw_tunnel.frame * 0.1 + radius * 0.05)
        drawer.penup()
        drawer.goto(0, -pulse)
        drawer.pendown()
        drawer.circle(pulse)
    
    draw_tunnel.frame += 1

def draw_hering(drawer, color):
    """Hering illusion"""
    drawer.clear()
    drawer.color(color)
    drawer.pensize(1)
    
    for angle in range(0, 180, 10):
        drawer.goto(0, 0)
        drawer.setheading(angle)
        drawer.pendown()
        drawer.forward(300)
        drawer.penup()
    
    drawer.pensize(3)
    for x in [-100, 100]:
        drawer.goto(x, -200)
        drawer.pendown()
        drawer.setheading(90)
        drawer.forward(400)
        drawer.penup()

def draw_ebbinghaus(drawer, color):
    """Ebbinghaus illusion"""
    drawer.clear()
    drawer.color(color)
    
    drawer.goto(-150, 0)
    drawer.dot(80)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        drawer.goto(-150 + 120 * math.cos(rad), 0 + 120 * math.sin(rad))
        drawer.dot(40)
    
    drawer.goto(150, 0)
    drawer.dot(80)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        drawer.goto(150 + 120 * math.cos(rad), 0 + 120 * math.sin(rad))
        drawer.dot(20)

# SIMPLE STROBES
def bw_strobe():
    """Pure black/white strobe"""
    t.clearscreen()
    def strobe():
        while True:
            t.bgcolor("black")
            time.sleep(0.05)
            t.bgcolor("white")
            time.sleep(0.05)
    strobe()

def rainbow_strobe():
    """Rainbow strobe"""
    t.clearscreen()
    def strobe():
        colours = ["red", "blue", "green"]
        while True:
            for colour in colours:
                t.bgcolor(colour)
                time.sleep(0.03)
    strobe()

# ILLUSION WRAPPERS
def vertical_motion(): create_illusion(draw_vertical_motion, "Stare at center for 30s, then look at wall to see it melt!")
def spiral_motion(): create_illusion(draw_spiral, "Stare at center for 30s, then look away to see everything swirl!")
def radial_motion(): create_illusion(draw_radial, "Stare at center, then look at surface to see it breathe!")
def checkerboard_motion(): create_illusion(draw_checkerboard, "Stare at pattern, then look away to see ghostly motion!")
def breathing_square(): create_illusion(draw_breathing_square, "Stare at square, then look away to see size aftereffects!")
def tunnel_effect(): create_illusion(draw_tunnel, "Stare at center, then look away to see tunnel motion!")
def hering_illusion(): create_illusion(draw_hering, "Stare at the illusion - the straight lines will appear curved!")
def ebbinghaus_illusion(): create_illusion(draw_ebbinghaus, "Stare at the circles - they appear different sizes!")

def main_menu():
    """Create main menu instantly"""
    try:
        # Clear everything first
        screen = t.Screen()
        for turtle in screen.turtles():
            turtle.hideturtle()
            turtle.clear()
        screen.clear()
        t.bgcolor("black")
        
        # Warning
        warning_text = "☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻"
        warnings = [
            (0, 280, warning_text),
            (0, 250, "☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻[ Warning May Cause Seizures ] ☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻"),
            (0, 220, warning_text)
        ]
        
        for x, y, text in warnings:
            w = t.Turtle()
            w.hideturtle()
            w.penup()
            w.goto(x, y)
            w.color("red")
            w.write(text, align="center", font=("Consolas", 10, "normal"))
        
        # Title
        title = t.Turtle()
        title.hideturtle()
        title.penup()
        title.goto(0, 180)
        title.color("white")
        title.write("Optical Illusions", align="center", font=("Consolas", 24, "bold"))
        
        # Buttons
        button_configs = [
            (-300, 120, "Vertical Motion", vertical_motion),
            (-300, 80, "Spiral Motion", spiral_motion),
            (-300, 40, "Radial Motion", radial_motion),
            (-300, 0, "Checkerboard", checkerboard_motion),
            (-300, -40, "Breathing Square", breathing_square),
            (-300, -80, "Tunnel Effect", tunnel_effect),
            (100, 120, "Hering Lines", hering_illusion),
            (100, 80, "Ebbinghaus", ebbinghaus_illusion),
            (100, 40, "BW Strobe", bw_strobe),
            (100, 0, "Rainbow Strobe", rainbow_strobe),
            (100, -80, "Exit", t.bye)
        ]
        
        for x, y, label, handler in button_configs:
            create_button(x, y, label, lambda h=handler: clear_and_start(h))
        
        # Instructions
        instr = t.Turtle()
        instr.hideturtle()
        instr.penup()
        instr.goto(0, -150)
        instr.color("gray")
        instr.write("Click any button to start illusion", align="center", font=("Consolas", 14, "normal"))
        
        t.update()

    except Exception as e:
        print(f"Error in main menu: {e}")

# Start application
screen = screen_setup()
main_menu()
t.mainloop()