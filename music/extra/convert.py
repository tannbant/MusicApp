import os
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pygame.mixer
import shutil
import random
from moviepy.editor import *

# Initialize Tkinter
app_window = tk.Tk()
app_window.title("SARF Player")
app_window.geometry("800x800")
app_window.configure(bg="#333333")  # Dark background color

# Global variable to hold the music listbox
music_listbox = None

# Global variable to hold the list of music files
music_list = []

# Initialize mixer
pygame.mixer.init()
volume = 0.5  # Default volume

# Function to play selected music
def play_music(event=None):
    selection = music_listbox.curselection()
    if selection:
        index = selection[0]
        music_file = music_list[index]
        try:
            pygame.mixer.music.load(music_file)  # Load music file
            pygame.mixer.music.play()  # Start music playback
        except pygame.error as e:
            messagebox.showerror("Error", str(e))

# Function to stop music playback
def stop_music():
    pygame.mixer.music.stop()  # Stop music playback

# Function to set volume
def set_volume(vol):
    try:
        # Convert the string input to an integer
        vol = int(vol)
        # Ensure that the volume is within a valid range (0-100)
        if vol < 0:
            vol = 0
        elif vol > 100:
            vol = 100
        # Convert to decimal
        volume = vol / 100
        pygame.mixer.music.set_volume(volume)  # Set volume
    except ValueError:
        # Handle the case where the input cannot be converted to an integer
        print("Invalid volume input. Please enter a valid integer.")

# Function to open the music player window
def open_music_player():
    global music_listbox
    # Initialize music player window
    music_player_window = tk.Toplevel(app_window)
    music_player_window.title("SARF Player")
    music_player_window.geometry("800x600")
    music_player_window.configure(bg="#333333")  # Dark background color

    # Create a frame for the music list
    music_list_frame = tk.Frame(music_player_window, bg="#333333")
    music_list_frame.pack(pady=20, padx=10, fill="both", expand=True)

    # Label for the music list
    music_list_label = tk.Label(music_list_frame, text="SARF Player", font=("Helvetica", 24), bg="#333333", fg="#ffffff")
    music_list_label.pack(side="top", pady=10)

    # Listbox to display the music list
    music_listbox = tk.Listbox(music_list_frame, width=70, height=15, bg="#ffffff", fg="#333333", selectbackground="#cccccc", selectforeground="#333333")
    music_listbox.pack(side="left", padx=10, pady=10, fill="both", expand=True)

    # Scrollbar for the listbox
    scrollbar = ttk.Scrollbar(music_list_frame, orient="vertical", command=music_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    music_listbox.config(yscrollcommand=scrollbar.set)

    # Bind double click event to play selected music
    music_listbox.bind("<Double-Button-1>", play_music)

    # List music files in listbox
    update_music_list()

    # Play Button
    play_button = ttk.Button(music_player_window, text="Play", command=play_music)
    play_button.pack(pady=5)

    # Stop Button
    stop_button = ttk.Button(music_player_window, text="Stop", command=stop_music)
    stop_button.pack(pady=5)

    # Volume Control
    volume_label = ttk.Label(music_player_window, text="Volume", background="#333333", foreground="#ffffff")
    volume_label.pack()
    volume_slider = ttk.Scale(music_player_window, from_=0, to=100, orient="horizontal", command=set_volume)
    volume_slider.set(50)  # Set default volume to 50%
    volume_slider.pack(pady=5)

# Function to download and convert YouTube video to MP3
def download_youtube_mp3():
    try:
        # Ask for YouTube link
        youtube_link = simpledialog.askstring("YouTube Link", "Enter the YouTube video link:")
        if youtube_link:
            chrome_options = Options()
            #chrome_options.add_argument("--headless")   

            # Initialize the Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            try:
                driver.get("https://mp3-convert.org/youtube-to-mp3-converterss/")
                time.sleep(2)  # Wait for the page to load
                # Fill in the URL
                url_input = driver.find_element(By.ID, "input")
                url_input.send_keys(youtube_link)
                # Click the convert button
                convert_button = driver.find_element(By.ID, "submit")
                convert_button.click()
                time.sleep(2)
                main_window_handle = driver.current_window_handle
                for handle in driver.window_handles:
                    if handle != main_window_handle:
                        advertisement_window_handle = handle
                        driver.switch_to.window(advertisement_window_handle)
                        break
                driver.close()
                driver.switch_to.window(main_window_handle)
                time.sleep(2)
                driver.close()
                download_link = driver.find_element(By.ID, "download_url")
                download_link.click()
                time.sleep(10)  # Assuming some time to download
                # Close the driver after completion
            except Exception as e:
                print("An error occurred:", e)
                
            finally: 
                driver.quit()
                messagebox.showinfo("Success", "Conversion completed successfully!")
                # Refresh the music list
                update_music_list()
                
    except Exception as e:
        print("An error occurred:", e)
        messagebox.showerror("Error", str(e))

# Function to update the music list
def update_music_list():
    global music_list
    music_listbox.delete(0, tk.END)
    music_folder = r"D:\code dir\PYTHON\test\MusicV1"
    music_list = [os.path.join(music_folder, filename) for filename in os.listdir(music_folder) if filename.endswith((".mp3", ".wav", ".mp4"))]
    if music_list:
        for music_file in music_list:
            music_listbox.insert(tk.END, os.path.basename(music_file))
    else:
        music_listbox.insert(tk.END, "No music files found")

# Function to upload music files
def upload_music():
    file_paths = filedialog.askopenfilenames(initialdir="/", title="Select Music Files", filetypes=(("Audio Files", "*.mp3 *.wav *.mp4"), ("All Files", "*.*")))
    if file_paths:
        output_path = r"D:\code dir\PYTHON\test\MusicV1"  # Specify your desired output directory
        for file_path in file_paths:
            # Move the file to the music folder
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(output_path, file_name)
            shutil.copy(file_path, destination_path)
            if file_path.endswith(".mp4"):
                os.chdir(output_path)
                clip = AudioFileClip(file_path)
                clip.write_audiofile("temp_audio.mp3")
                clip.close()
                os.chdir(r'D:\code dir\PYTHON\test\MusicV1')
            else:
                print(f"{file_path} is not an MP4 file.")
        # Update the music list
        update_music_list()

# Frame for buttons
button_frame = tk.Frame(app_window, bg="#333333")
button_frame.pack(pady=20)

# Button to open music player
open_music_player_button = ttk.Button(button_frame, text="Music Player", command=open_music_player, style="TButton")
open_music_player_button.pack(side=tk.TOP, pady=10)

# Button to add music from YouTube
add_music_button = ttk.Button(button_frame, text="Add Music", command=download_youtube_mp3, style="TButton")
add_music_button.pack(side=tk.TOP, pady=10)

# Button to upload music files
upload_button = ttk.Button(button_frame, text="Upload", command=upload_music, style="TButton")
upload_button.pack(side=tk.TOP, pady=10)

# Button for settings
def open_settings():
    settings_window = tk.Toplevel(app_window)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#333333")  # Dark background color

    # Dark Mode Checkbox
    dark_mode_var = tk.IntVar()
    dark_mode_checkbox = ttk.Checkbutton(settings_window, text="Dark Mode", variable=dark_mode_var, onvalue=1, offvalue=0)
    dark_mode_checkbox.pack(pady=10)

settings_button = ttk.Button(button_frame, text="Settings", command=open_settings, style="TButton")
settings_button.pack(side=tk.TOP, pady=10)

# Button for home
def home():
    pass

home_button = ttk.Button(app_window, text="Home", command=home, style="TButton")
home_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Function for shuffling music
def shuffle_music():
    if music_list:
        random_music_file = random.choice(music_list)
        try:
            pygame.mixer.music.load(random_music_file)
            pygame.mixer.music.play()
        except pygame.error as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showinfo("No Music", "No music files available.")

# Shuffle Button
shuffle_button = ttk.Button(app_window, text="Shuffle", command=shuffle_music)
shuffle_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Main event loop
app_window.mainloop()
