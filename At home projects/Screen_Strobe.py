#☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻
# ☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻[ Warning May Cause Seizures ] ☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻
#☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻☺☺☻☻

import turtle as t
import time

def screen_setup():
    screen = t.Screen()
    screen.title("Screen Strobe")
    screen.bgcolor("black")
    # Fullscreen setup for when run
    screen.setup(width = 1.0, height = 1.0)

    # Strobe Functions
    def rainbow_strobe():
        t.clearscreen()
        colours = ["red", "blue", "green"]
        while True:
            for colour in colours:
                t.bgcolor(colour)
                time.sleep(0.03)
                
    def bw_strobe():
        t.clearscreen()
        while True:
            t.bgcolor("black")
            time.sleep(0.05)
            t.bgcolor("white")
            time.sleep(0.05)


    # Button to start black and white strobe
    def bw_btn():
        bw_btn = t.Turtle()
        bw_btn.shape("square")
        bw_btn.color("white")
        bw_btn.penup()
        bw_btn.goto(-200, 0)
        bw_btn.onclick(lambda x, y: bw_strobe())

        def bw_strobe_txt():
            bw_text = t.Turtle()
            bw_text.hideturtle()
            bw_text.color("white")
            bw_text.penup()
            bw_text.goto(-200, 7)
            bw_text.write("BW", align="center", font=("Consolas", 16, "normal"))
        bw_strobe_txt()

    # Button to start rainbow strobe
    def rainbow_strobe_btn():
        rainbow_strobe_btn = t.Turtle()
        rainbow_strobe_btn.shape("square")
        rainbow_strobe_btn.color("white")
        rainbow_strobe_btn.penup()
        rainbow_strobe_btn.goto(200, 0)
        rainbow_strobe_btn.onclick(lambda x, y: rainbow_strobe())

        def rainbow_strobe_txt():
            rainbow_text = t.Turtle()
            rainbow_text.hideturtle()
            rainbow_text.color("white")
            rainbow_text.penup()
            rainbow_text.goto(200, 7)
            rainbow_text.write("RGB", align="center", font=("Consolas", 16, "normal"))
        rainbow_strobe_txt()


    bw_btn()
    rainbow_strobe_btn()

screen_setup()
t.done()
