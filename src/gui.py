import tkinter as tk
from tkinter import font, messagebox
from news_gpt import NewsGPT
import asyncio
import threading
import time
from exceptions import OpenAiApiError, GoogleApiError, HttpsError

class NewsGPTGui:
    def __init__(self):
        # Initialize instance variables for GUI theme and debounce timing
        self.dark_background = "#2A2A2A"
        self.light_text = "#E1E1E1"
        self.border_color = "#6C7A89"  # Bluish-grey color for the border
        self.debounce_delay = 250  # Time in milliseconds for debounce in resize event
        self.last_resize_time = time.time()  # Stores the last time the window was resized

        # Initialize main Tkinter window
        self.root = tk.Tk()
        self.root.title("News GPT")

        # Flag to control the thinking animation
        self.animate_thinking_running = False

        # Placeholder for NewsGPT object
        self.news_gpt = None

        # Placeholder for API keys and search engine ID
        self.openai_api_key = None
        self.google_api_key = None
        self.search_engine_id = None

    def initialize(self):
        # Configure the main window and display the popup
        self.root.configure(bg=self.dark_background)
        self.root.withdraw()  # Initially hide the main chat window
        self.display_popup()
        self.build_chat_window()
        self.root.mainloop()  # Start the Tkinter event loop    
        
    def display_popup(self):
        # Create and configure the popup window for API key entry
        self.popup = tk.Toplevel(self.root)
        self.popup.configure(bg=self.dark_background)
        self.popup.title("Enter API Keys and Search Engine ID")
        self.popup.geometry('600x300')  # Set the initial size of the popup

        # Create a frame to center elements vertically and horizontally
        self.center_frame = tk.Frame(self.popup, bg=self.dark_background, width=400)
        self.center_frame.pack(expand=True)

        # Reserve a space for the error message with an empty label
        self.error_message_frame = tk.Frame(self.center_frame, height=40, bg=self.dark_background)  # Increased height
        self.error_message_frame.pack(fill='x', expand=True)

        self.error_message_label = tk.Label(self.error_message_frame, text="", fg="red", bg=self.dark_background, wraplength=580)  # Enable text wrapping
        self.error_message_label.pack()

        # Create a font for the entry widgets
        self.entry_font_size = 20
        self.entry_font = font.Font(size=self.entry_font_size)

        # Create and pack the API key and search engine ID entry widgets within the center frame
        self.openai_api_key_label = tk.Label(self.center_frame, text="OpenAI API Key:", bg=self.dark_background, fg=self.light_text)
        self.openai_api_key_label.pack(fill='x')
        self.openai_api_key_entry = tk.Entry(self.center_frame, font=self.entry_font, fg="cyan", bg=self.dark_background)
        self.openai_api_key_entry.pack()

        self.google_api_key_label = tk.Label(self.center_frame, text="Google API Key:", bg=self.dark_background, fg=self.light_text)
        self.google_api_key_label.pack(fill='x')
        self.google_api_key_entry = tk.Entry(self.center_frame, font=self.entry_font, fg="cyan", bg=self.dark_background)
        self.google_api_key_entry.pack()

        self.search_engine_id_label = tk.Label(self.center_frame, text="Search Engine ID:", bg=self.dark_background, fg=self.light_text)
        self.search_engine_id_label.pack(fill='x')
        self.search_engine_id_entry = tk.Entry(self.center_frame, font=self.entry_font, fg="cyan", bg=self.dark_background)
        self.search_engine_id_entry.pack()

        # Create and pack the button to enter the chat window
        self.access_button = tk.Button(self.center_frame, text="Enter Chat", command=self.show_chat_window, bg=self.dark_background, fg=self.light_text)
        self.access_button.pack(pady=10, ipadx=10, ipady=5)  # Increase padding inside the button

    def build_chat_window(self):
        # Set a large font for the chat window elements
        self.large_font = font.Font(size=15)  # Font size can be adjusted as needed

        # Creating the main frame to hold chat history and scrollbar
        self.chat_frame = tk.Frame(self.root, bg=self.dark_background)
        self.chat_frame.pack(padx=10, pady=(10, 2), fill='both', expand=True)

        # Text area for displaying chat history
        self.chat_history = tk.Text(self.chat_frame, height=8, bg=self.dark_background, fg=self.light_text, 
                                    insertbackground=self.light_text, state=tk.DISABLED, 
                                    font=self.large_font, wrap=tk.WORD)
        self.chat_history.pack(side=tk.LEFT, padx=(0, 10), fill='both', expand=True)

        # Configuring text tags for styling certain text parts
        self.chat_history.tag_configure('name_color', foreground='green', font=font.Font(size=15, weight="bold")) 
        self.chat_history.tag_configure('spaced_line', spacing3=15)  # Adds extra space after tagged lines

        # Adding a scrollbar to the chat history
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_history.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.chat_history['yscrollcommand'] = self.scrollbar.set  # Linking scrollbar to chat history

        # Bottom frame for message input and send button
        self.bottom_frame = tk.Frame(self.root, bg=self.dark_background)
        self.bottom_frame.pack(padx=10, pady=2, fill='x')

        # Frame for message entry with a white border
        self.entry_border_frame = tk.Frame(self.bottom_frame, background=self.dark_background, 
                                           highlightbackground='white', highlightthickness=1)
        self.entry_border_frame.grid(row=0, column=0, sticky='ew', padx=(0.475, 12), pady=10, ipady=10)
        self.entry_border_frame.columnconfigure(0, weight=1)  # Make the frame expandable

        # Message entry box
        self.message_entry = tk.Entry(self.entry_border_frame, insertbackground='white', bd=0, 
                                      bg=self.dark_background, fg=self.light_text, font=('Arial', 20), width=30)
        self.message_entry.pack(fill='both', expand=True, padx=8)  # Filling the available space
        self.message_entry.bind('<Return>', lambda event: self.run_async_coroutine(self.send_message()))  # Bind enter key to send message

        # Configuring the grid to allocate more space to the message entry
        self.bottom_frame.columnconfigure(0, weight=6)

        # Defining a large font for the send button
        self.button_font = font.Font(family="Helvetica", size=16, weight="bold") 

        # Creating the send button
        self.send_button = tk.Button(self.bottom_frame, text="Send", 
                                     command=lambda: self.run_async_coroutine(self.send_message()),
                                     bg=self.dark_background, fg=self.light_text, font=self.button_font)
        self.send_button.grid(row=0, column=1, sticky='ew', ipady=10)

        # Configuring the grid to allocate space to the send button
        self.bottom_frame.columnconfigure(1, weight=1)

    def show_chat_window(self):
        """
        Retrieves API keys from the entry fields in the pop-up window and displays the main chat window.
        Initializes the NewsGPT class with the provided API keys if they are valid.
        """

        # Retrieve the API keys entered by the user
        self.openai_api_key = self.openai_api_key_entry.get()
        self.google_api_key = self.google_api_key_entry.get()
        self.search_engine_id = self.search_engine_id_entry.get()
        
        # Check if all required API keys are entered
        if self.openai_api_key and self.google_api_key and self.search_engine_id:
            # Close the pop-up window and reveal the main chat window
            self.popup.destroy()
            self.root.deiconify()
            
            # Initialize the NewsGPT class with the entered API keys
            self.news_gpt = NewsGPT(self.openai_api_key, self.google_api_key, self.search_engine_id)

            # Debug print statement - can be removed in production
            print(self.news_gpt)
        
        # If any API key is missing, keep the pop-up window open
        else:
            # Identify which fields are missing
            missing_fields = []
            if not self.openai_api_key:
                missing_fields.append("OpenAI API Key")
            if not self.google_api_key:
                missing_fields.append("Google API Key")
            if not self.search_engine_id:
                missing_fields.append("Search Engine ID")

            # Create a message for the missing fields
            missing_fields_message = "Please enter your input in the following field(s): " + ", ".join(missing_fields)

            # Update and display the error message label
            self.error_message_label.config(text=missing_fields_message)

            # Automatically hide the message after a delay
            self.popup.after(3500, lambda: self.error_message_label.config(text=""), lambda: self.run_async_coroutine(self.send_message()))

    def animate_thinking(self, dots=1):
        """
        Animates a 'thinking' indicator in the chat history to show that the program is processing.
        
        Args:
            dots (int): Number of dots to display in the animation. Cycles through 1 to 3 dots.
        """
        # Exit the function if the animation should not be running
        if not self.animate_thinking_running:
            return
        
        # Prepare the base text and dynamic dot text for the animation
        base_text = "GPT: "
        dot_text = f"Thinking{'.' * dots}\n"  # Text like 'Thinking...', changing with the number of dots
        
        # Make the chat history widget editable before inserting text
        self.chat_history.config(state=tk.NORMAL)

        # Retrieve the content of the last line in the chat history
        last_line = self.chat_history.get("end-2l", "end-1l")

        # If the last line is part of the animation (starts with "GPT"), remove it to update
        if last_line.startswith("GPT"):
            self.chat_history.delete("end-2l", "end-1l")

        # Insert the base text and the dot text for the current animation frame
        self.chat_history.insert(tk.END, base_text, 'name_color')
        self.chat_history.insert(tk.END, dot_text)

        # Scroll the chat history to the end to ensure the animation is visible
        self.chat_history.see(tk.END)

        # Set the chat history widget back to read-only
        self.chat_history.config(state=tk.DISABLED)

        # Determine the number of dots for the next frame of the animation
        next_dots = (dots % 3) + 1  # Cycle through 1, 2, 3 dots in sequence

        # Schedule the next frame of the animation after a brief pause
        self.root.after(500, self.animate_thinking, next_dots)

    async def send_message(self, event=None):
        """
        Handles the process of sending a message in a chat application. 
        """

        # Get and strip the message from the message entry widget
        message = self.message_entry.get().strip()

        # Check if the message is not empty
        if message:
            # Disable the send button and unbind the Return key to prevent duplicate sends
            self.send_button.config(state=tk.DISABLED)
            self.message_entry.unbind('<Return>')

            # Insert the user's message into the chat history
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, "You: ", 'name_color')
            self.chat_history.insert(tk.END, f"{message}\n\n", 'spaced_line')
            self.chat_history.config(state=tk.DISABLED)
            self.message_entry.delete(0, tk.END)

            # Start the "Thinking..." animation to indicate processing
            self.animate_thinking_running = True
            self.animate_thinking(3)

            # Attempt to get a response from the news_gpt service
            try:
                response = await self.news_gpt.get_response(message) 
            except (OpenAiApiError, GoogleApiError, HttpsError, Exception) as e:
                # Handle different types of exceptions and set an appropriate response message
                if isinstance(e, OpenAiApiError):
                    response = f"OpenAI API error: {e}"
                elif isinstance(e, GoogleApiError):
                    response = f"Google API error: {e}"
                elif isinstance(e, HttpsError):  
                    response = f"Https error: {e}"
                else: 
                    response = f"Unexpected error: {e}"

            # Process the response if it's in dict format
            if isinstance(response, dict):
                response = response['choices'][0]['message']['content']
            
            # Stop the "Thinking..." animation
            self.animate_thinking_running = False

            # Delete the "Thinking..." message from the chat history
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("end-2l linestart", "end-1l lineend")

            # Insert the response from GPT into the chat history
            self.chat_history.insert(tk.END, f"GPT: ", 'name_color')
            self.chat_history.insert(tk.END, f"{response}\n\n", 'spaced_line')

            # Scroll the chat history to the latest message
            self.chat_history.see(tk.END)
            self.chat_history.config(state=tk.DISABLED)

            # Re-enable the send button and re-bind the Return key to send_message
            self.send_button.config(state=tk.NORMAL)
            self.message_entry.bind('<Return>', lambda event: self.run_async_coroutine(self.send_message()))


    @staticmethod
    def run_async_coroutine(coroutine):
        """
        Runs an asynchronous coroutine in a separate thread.

        This method is a utility to run async coroutines in a GUI environment where 
        the main thread is blocked by the GUI loop and can't be used for async operations.

        Args:
            coroutine: The asynchronous coroutine that needs to be run.
        """

        # Define a function to run the coroutine
        def run():
            # Create a new event loop for the coroutine
            # This is necessary because each thread must have its own event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the coroutine to completion in the new event loop
            loop.run_until_complete(coroutine)

        # Start a new thread targeting the 'run' function
        # This allows the coroutine to run asynchronously without blocking the main thread
        threading.Thread(target=run).start()
