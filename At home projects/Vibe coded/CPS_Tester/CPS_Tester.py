import tkinter as tk
import winsound

# Main application class for the CPS Tester
class CPSTesterApp:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("CPS Tester")
        self.root.configure(bg="#00268E")
        self.width = 500
        self.height = 300
        self.center_window()  # Center the window on the screen

        # Initialize test variables
        self.test_duration = 5  # Default test duration in seconds
        self.count = 0          # Number of clicks
        self.time_left = 0      # Time left in the test
        self.timer_id = None    # ID for the timer event
        self.build_menu()       # Show the main menu

    def center_window(self):
        # Center the window on the user's screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def clear_window(self):
        # Remove all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_menu(self):
        # Build the main menu with test duration options
        self.clear_window()
        tk.Label(self.root, text="CPS Tester", font=("Arial", 20, "bold"), bg="#00268E", fg="white").pack(pady=20)
        tk.Label(self.root, text="Choose test duration:", font=("Arial", 14), bg="#00268E", fg="white").pack(pady=10)
        btn_frame = tk.Frame(self.root, bg="#00268E")
        btn_frame.pack(pady=10)
        # Buttons for 5, 15, and 30 second tests
        tk.Button(btn_frame, text="5 Seconds", font=("Arial", 14), width=12, command=lambda: self.start_test(5)).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="15 Seconds", font=("Arial", 14), width=12, command=lambda: self.start_test(15)).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="30 Seconds", font=("Arial", 14), width=12, command=lambda: self.start_test(30)).grid(row=0, column=2, padx=5)

    def start_test(self, duration):
        # Set up the test screen for the selected duration
        self.clear_window()
        self.test_duration = duration
        self.count = 0
        self.time_left = duration
        self.timer_id = None
        self.timer_running = False  # Timer starts on first click

        # Timer label at the top
        self.timer_label = tk.Label(self.root, text=f"Time left: {self.time_left:.1f}s", font=("Arial", 14), bg="#00268E", fg="white")
        self.timer_label.pack(pady=10)

        # Click count label
        self.click_label = tk.Label(self.root, text="Clicks: 0", font=("Arial", 16), bg="#00268E", fg="white")
        self.click_label.pack(pady=10)

        # Main "Click ME!" button
        self.click_btn = tk.Button(self.root, text="Click ME!", font=("Arial", 18), width=12, height=2, command=self.increment)
        self.click_btn.pack(pady=20)

        # "View Results" button, hidden until test ends
        self.view_results_btn = tk.Button(self.root, text="View Results", font=("Arial", 12), command=self.show_results)
        self.view_results_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        self.view_results_btn.lower()  # Hide until test ends

    def increment(self):
        # Handle click events on the "Click ME!" button
        # Start the timer on the first click
        if not hasattr(self, 'timer_running') or not self.timer_running:
            self.timer_running = True
            self.update_timer()
        # Only count clicks if time is left
        if self.time_left > 0:
            self.count += 1
            self.click_label.config(text=f"Clicks: {self.count}")

    def update_timer(self):
        # Update the timer every 0.1 seconds
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left:.1f}s")
            self.time_left -= 0.1
            self.timer_id = self.root.after(100, self.update_timer)
        else:
            # Time's up: disable the click button and show "View Results"
            self.timer_label.config(text="Time's up!")
            self.click_btn.config(state="disabled")
            self.view_results_btn.lift()  # Show the "View Results" button
            winsound.MessageBeep(winsound.MB_ICONHAND)  # Play a Windows built-in sound when time is up

    def show_results(self):
        # Show the results screen with CPS calculation
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        cps = self.count / self.test_duration
        self.clear_window()
        tk.Label(self.root, text="Results", font=("Arial", 20, "bold underline"), bg="#00268E", fg="white").pack(pady=20)
        tk.Label(self.root, text=f"Total Clicks: {self.count}", font=("Arial", 16), bg="#00268E", fg="white").pack(pady=10)
        tk.Label(self.root, text=f"Test Duration: {self.test_duration} seconds", font=("Arial", 14), bg="#00268E", fg="white").pack(pady=5)
        tk.Label(self.root, text=f"Clicks Per Second: {cps:.2f}", font=("Arial", 16), bg="#00268E", fg="white").pack(pady=10)
        btn_frame = tk.Frame(self.root, bg="#00268E")
        btn_frame.pack(pady=20)
        # Button to return to menu
        tk.Button(btn_frame, text="Menu", font=("Arial", 12), width=10, command=self.build_menu).grid(row=0, column=0, padx=10)
        # Button to close the app, now calls self.close_app
        tk.Button(btn_frame, text="Close app", font=("Arial", 12), width=10, command=self.close_app).grid(row=0, column=1, padx=10)

    def close_app(self):
        # Play error sound and close the app
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        self.root.destroy()

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CPSTesterApp(root)
    # Play sound when window is closed via the X button
    def on_closing():
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()