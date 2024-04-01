import os
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox, StringVar
import pygame.mixer
import shutil
import random
from pytube import YouTube
from moviepy.editor import AudioFileClip
from bs4 import BeautifulSoup
import requests

# Define global variables
pygame.mixer.init()
volume = 0.5
music_player_window = None
music_listbox = None
music_list = []
equalizer_window = None
equalizer_sliders = []
equalizer_labels = ["Bass", "Mid", "Treble"]
song_slider_dragging = False  # Variable to track if the song slider is being dragged
current_song_position = 0
current_song_index = 0

main_gui_window = None

def adjust_equalizer():
    global equalizer_sliders

    # Get the slider values for each band
    band_values = [slider.get() for slider in equalizer_sliders]

    # Apply equalizer adjustments (replace this with your actual equalizer adjustment logic)
    print("Equalizer adjusted:")
    for band, value in enumerate(band_values):
        print(f"{equalizer_labels[band]}: {value}")

def open_equalizer():
    global equalizer_window, equalizer_sliders

    if equalizer_window and equalizer_window.winfo_exists():
        equalizer_window.lift()  
        return

    equalizer_window = tk.Toplevel()
    equalizer_window.title("Equalizer")
    equalizer_window.geometry("400x300")

    style = ttk.Style()
    style.configure("Equalizer.TFrame", background="#333333")  # Set background color using style

    equalizer_frame = ttk.Frame(equalizer_window, style="Equalizer.TFrame")
    equalizer_frame.pack(pady=20, padx=10, fill="both", expand=True)

    for i, label in enumerate(equalizer_labels):
        ttk.Label(equalizer_frame, text=label, background="#333333", foreground="#ffffff").grid(row=i, column=0, padx=10, pady=5)
        slider = ttk.Scale(equalizer_frame, from_=-12, to=12, orient="horizontal")
        slider.grid(row=i, column=1, padx=10, pady=5)
        equalizer_sliders.append(slider)

    apply_button = ttk.Button(equalizer_window, text="Apply", command=adjust_equalizer)
    apply_button.pack(pady=10)

def play_music(event=None):
    global current_song_index, current_song_position

    # Stop the currently playing song
    stop_music()

    # Get the selected song from the listbox
    selected_song_index = music_listbox.curselection()[0]
    current_song_index = selected_song_index

    # Load and play the selected song
    selected_song = music_list[selected_song_index]
    pygame.mixer.music.load(selected_song)
    pygame.mixer.music.play()

    # Update song information
    update_song_info(selected_song)

    # Update current song position
    current_song_position = 0

    # Update position and slider immediately
    update_position_and_slider()


def stop_music():
    pygame.mixer.music.stop()

def set_volume(event=None, vol=None):
    try:
        if vol is None:
            vol = volume_slider.get()

        vol = int(vol)

        if vol < 0:
            vol = 0
        elif vol > 100:
            vol = 100

        volume = vol / 100
        pygame.mixer.music.set_volume(volume)  
    except ValueError:
        print("Invalid volume input. Please enter a valid integer.")

def open_music_player():
    global music_listbox, volume_slider, music_player_window, position_label, duration_label, music_length, song_slider, song_slider_dragging, main_gui_window

    # Hide the main GUI window
    main_gui_window.withdraw()

    if music_player_window and music_player_window.winfo_exists():
        music_player_window.lift()
        return

    if not music_player_window or not music_player_window.winfo_exists():
        music_player_window = tk.Toplevel()
        music_player_window.title("Music Player")
        music_player_window.geometry("800x600")
        music_player_window.configure(bg="#333333")

        # Set the end event for music mixer to play the next song automatically
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        
        
        
        header_frame = tk.Frame(music_player_window, bg="#333333")
        header_frame.pack(fill="x")

        home_button = ttk.Button(header_frame, text="Home", command=go_to_main_gui)
        home_button.pack(side="left", padx=10, pady=5)

        equalizer_button = ttk.Button(header_frame, text="Equalizer", command=open_equalizer)
        equalizer_button.pack(side="left", padx=10, pady=5)

     
        file_button = ttk.Button(header_frame, text="File", command=upload_music)
        file_button.pack(side="left", padx=10, pady=5)
        
        
        
        music_list_frame = tk.Frame(music_player_window, bg="#333333")
        music_list_frame.pack(pady=20, padx=10, fill="both", expand=True)

        music_list_label = tk.Label(music_list_frame, text="Music Player", font=("Helvetica", 24), bg="#333333", fg="#ffffff")
        music_list_label.pack(side="top", pady=10)

        music_listbox = tk.Listbox(music_list_frame, width=70, height=15, bg="#ffffff", fg="#333333", selectbackground="#cccccc", selectforeground="#333333")
        music_listbox.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(music_list_frame, orient="vertical", command=music_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        music_listbox.config(yscrollcommand=scrollbar.set)

        music_listbox.bind("<Double-Button-1>", play_music)

        update_music_list()

        shuffle_button = ttk.Button(music_player_window, text="Shuffle", command=lambda: shuffle_music(time_label))
        shuffle_button.pack(pady=5)


        play_button = ttk.Button(music_player_window, text="Play", command=play_music)
        play_button.pack(pady=5)

        

        stop_button = ttk.Button(music_player_window, text="Stop", command=stop_music)
        stop_button.pack(pady=5)

        

        prev_button = ttk.Button(music_player_window, text="◄", command=play_prev_song)
        prev_button.pack(side="left", padx=10)

        next_button = ttk.Button(music_player_window, text="►", command=play_next_song)
        next_button.pack(side="right", padx=10)

        volume_label = ttk.Label(music_player_window, text="Volume", background="#333333", foreground="#ffffff")
        volume_label.pack()
        volume_slider = ttk.Scale(music_player_window, from_=0, to=100, orient="horizontal", command=set_volume)
        volume_slider.set(50)  
        volume_slider.pack(pady=5)

        # Position Label
        position_label = ttk.Label(music_player_window, text="0:00", background="#333333", foreground="#ffffff")
        position_label.pack()

        # Duration Label
        duration_label = ttk.Label(music_player_window, text="0:00", background="#333333", foreground="#ffffff")
        duration_label.pack()

        time_label = ttk.Label(music_player_window, text="", background="#333333", foreground="#ffffff")
        time_label.pack()



        # Song Slider
        global song_slider
        song_slider = ttk.Scale(music_player_window, from_=0, to=100, orient="horizontal")
        song_slider.pack(fill="x", padx=20, pady=10)

        # Bind events to the song slider
        song_slider.bind("<ButtonRelease-1>", on_song_slider_release)
        #song_slider.bind("<ButtonPress-1>", on_song_slider_drag)

        # Start a timer to update position label and song slider position periodically
        update_position_and_slider()

        # Set the end event for music mixer to play the next song automatically
        pygame.mixer.music.set_endevent(pygame.USEREVENT)


#queue box







def go_to_main_gui():
    global main_gui_window, music_player_window

    if music_player_window and music_player_window.winfo_exists():
        music_player_window.destroy()


    # Show the main GUI window
    main_gui_window.deiconify()

    # Set music_player_window to None when returning to the main GUI
    music_player_window = None


def update_position_and_slider():
    global song_slider

    # Get the current position of the song in milliseconds
    current_position_ms = pygame.mixer.music.get_pos()

    # Convert milliseconds to seconds
    current_position_sec = current_position_ms / 1000

    # Update position label with current position
    position_label.config(text=format_time(current_position_sec))

    # Update song slider position
    if not song_slider_dragging:  # Update the song slider position only if it's not being dragged
        song_slider.set(current_position_sec)

    # Schedule the function to run again after 100ms (0.1 second)
    music_player_window.after(100, update_position_and_slider)

def on_song_slider_release(event):
    # Restart the timer for updating position and slider
    update_position_and_slider()

def format_time(seconds):
    # Format seconds to MM:SS format
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_song_info(music_file):
    global current_song_position

    # Get the duration of the song
    audio = AudioFileClip(music_file)
    duration = audio.duration
    audio.close()

    # Update duration label
    duration_label.config(text=format_time(duration))

    # Update song slider range
    song_slider.config(to=duration)

    # Update current song position
    if current_song_position > duration:
        current_song_position = 0

def play_prev_song():
    selection = music_listbox.curselection()
    if selection:
        index = selection[0]
        if index > 0:
            music_listbox.selection_clear(0, tk.END)
            music_listbox.selection_set(index - 1)
            music_listbox.activate(index - 1)
            play_music()

def play_next_song():
    global current_song_index
    if shuffle_mode:
        current_song_index = random.randint(0, len(music_list) - 1)
    elif current_song_index < len(music_list) - 1:
        current_song_index += 1
    else:
        current_song_index = 0
    play_music(music_list[current_song_index])

def download_youtube_mp3():
    def download_video(url):
        try:
            download_folder = r'D:\code dir\PYTHON\music\MusicV1'
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            download_path = os.path.join(download_folder, f"{yt.title}.mp4")
            stream.download(output_path=download_folder, filename=f"{yt.title}.mp4")  
            audio_clip = AudioFileClip(download_path)
            audio_clip.write_audiofile(os.path.join(download_folder, f"{yt.title}.mp3"))  
            audio_clip.close()
            os.remove(download_path)  
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def submit_links():
        links = entry.get().split('\n')
        for link in links:
            if link.strip():
                status = download_video(link)
                status_label.config(text=f"Download {'successful' if status else 'failed'} for: {link}")

    def show_youtube_links():
        query = search_entry.get().strip()
        if query:
            search_results = search_youtube(query)
            if search_results:
                links_text.config(state=tk.NORMAL)
                links_text.delete(1.0, tk.END)
                for result in search_results:
                    links_text.insert(tk.END, f"{result['title']}: {result['link']}\n")
                links_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("No Results", "No YouTube links found for the search query.")
        else:
            messagebox.showinfo("Empty Query", "Please enter a search query.")

    def search_youtube(query):
        search_query = query.replace(" ", "+")
        search_url = f"https://www.youtube.com/results?search_query={search_query}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        search_results = soup.find_all("a", {"class": "yt-simple-endpoint style-scope ytd-video-renderer"})
        results = []
        for result in search_results:
            video_title = result.get("title")
            video_link = "https://www.youtube.com" + result.get("href")
            results.append({"title": video_title, "link": video_link})
        return results

    # Create the GUI for the YouTube downloader
    root = tk.Tk()
    root.title("Music Downloader")
    root.geometry("600x400")

    label = tk.Label(root, text="Enter YouTube URLs (one per line):")
    label.pack()

    entry = tk.Entry(root, width=50, borderwidth=3)
    entry.pack()

    submit_button = tk.Button(root, text="Submit", command=submit_links)
    submit_button.pack()

    status_label = tk.Label(root, text="")
    status_label.pack()

    search_frame = ttk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Search YouTube:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=show_youtube_links)
    search_button.grid(row=0, column=2)

    links_text = tk.Text(root, width=80, height=15, state=tk.DISABLED)
    links_text.pack(pady=10)

    root.mainloop()




def update_music_list():
    global music_list
    music_listbox.delete(0, tk.END)
    music_folder = r"D:\code dir\PYTHON\music\MusicV1"
    music_list = [os.path.join(music_folder, filename) for filename in os.listdir(music_folder) if filename.endswith((".mp3", ".wav", ".mp4"))]

    if music_list:
        for music_file in music_list:
            music_listbox.insert(tk.END, os.path.basename(music_file))
    else:
        music_listbox.insert(tk.END, "No music files found")

def upload_music():
    file_paths = filedialog.askopenfilenames(initialdir="/", title="Select Music Files", filetypes=(("Audio Files", "*.mp3 *.wav *.mp4"), ("All Files", "*.*")))
    if file_paths:
        output_path = r"D:\code dir\PYTHON\test\MusicV1"  
        for file_path in file_paths:
            # Move the file to the music folder
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(output_path, file_name)
            shutil.copy(file_path, destination_path)
        # Update the music list
        update_music_list()

def open_settings():
    def save_settings():
        settings_window.destroy()  

    settings_window = tk.Toplevel(app_window)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#333333")  

    dark_mode_var = StringVar(value=0)
    dark_mode_checkbox = ttk.Checkbutton(settings_window, text="Dark Mode", variable=dark_mode_var, onvalue=1, offvalue=0)
    dark_mode_checkbox.pack(pady=10)

    adpass_button = ttk.Button(settings_window, text="Admin", command=open_admin_panel)
    adpass_button.pack(pady=10)

    save_button = ttk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)

def open_admin_panel():
    password = simpledialog.askstring("Admin Password", "Enter admin password:", show="*")
    if password == "8197":  # Replace "admin" with your actual admin password
        admin_window = tk.Toplevel(app_window)
        admin_window.title("Admin Panel")
        admin_window.geometry("400x300")
        admin_window.configure(bg="#333333")
        admin_label = tk.Label(admin_window, text="Welcome to Admin Panel", font=("Arial", 14), fg="white", bg="#333333")
        admin_label.pack(pady=20)
    else:
        tk.messagebox.showerror("Error", "Incorrect password")

def shuffle_music(time_label):
    global current_song_index

    if music_list:
        # Select a random song index different from the current one
        new_song_index = current_song_index
        while new_song_index == current_song_index:
            new_song_index = random.randint(0, len(music_list) - 1)

        # Get the duration of the current song
        current_song_file = music_list[current_song_index]
        current_song_duration = AudioFileClip(current_song_file).duration

        # Get the time left in the current song
        current_song_position = pygame.mixer.music.get_pos() / 1000
        time_left = current_song_duration - current_song_position

        current_song_index = new_song_index

        random_music_file = music_list[current_song_index]
        try:
            pygame.mixer.music.load(random_music_file)
            pygame.mixer.music.play()

            music_listbox.selection_clear(0, tk.END)
            music_listbox.selection_set(current_song_index)
            music_listbox.activate(current_song_index)
            music_listbox.see(current_song_index)

            
            time_label.config(text=f"Time Left: {int(time_left)} seconds")

            
            music_player_window.after(1000, lambda: update_time_left(time_label, current_song_duration))
        except pygame.error as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showinfo("No Music", "No music files available.")

def update_time_left(time_label, duration):
    # Get the current song position
    current_song_position = pygame.mixer.music.get_pos() / 1000

    # Calculate the time left
    time_left = max(0, duration - current_song_position)

    # Update the time left label
    time_label.config(text=f"Time Left: {int(time_left)} seconds")

    # Schedule the function to update time left label again after 1 second
    music_player_window.after(1000, lambda: update_time_left(time_label, duration))




def handle_end_of_song(event):
    global paused, current_song_index

    print("End of song event triggered")  # Add this line to check event triggering

    if not paused:  # Only proceed if the music is not paused
        if shuffle_mode:
            current_song_index = random.randint(0, len(music_list) - 1)
        elif current_song_index < len(music_list) - 1:
            current_song_index += 1
        else:
            current_song_index = 0
        play_music()




app_window = tk.Tk()
app_window.title("Music Player")
app_window.geometry("400x400")
app_window.configure(bg="#333333") 

modern_button_style = ttk.Style()
modern_button_style.configure("Modern.TButton", font=("Arial", 12), foreground="black", background="#4CAF50")
button_frame = tk.Frame(app_window, bg="#333333")
button_frame.pack(pady=50)

music_player_button = ttk.Button(button_frame, text="Music Player", command=open_music_player, style="Modern.TButton")
music_player_button.pack(fill="x", padx=20, pady=10)

add_music_button = ttk.Button(button_frame, text="Add Music", command=download_youtube_mp3, style="Modern.TButton")
add_music_button.pack(fill="x", padx=20, pady=10)

settings_button = ttk.Button(button_frame, text="Settings", command=open_settings, style="Modern.TButton")
settings_button.pack(fill="x", padx=20, pady=10)

# Store a reference to the main GUI window
main_gui_window = app_window

# Bind the event handler for the end of the song
app_window.bind(pygame.USEREVENT, handle_end_of_song)

app_window.mainloop()
