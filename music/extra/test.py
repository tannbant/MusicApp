from tkinter import Tk, Label, Entry, Button, Toplevel, Checkbutton, IntVar, filedialog
from pytube import YouTube
import os
from moviepy.editor import AudioFileClip

download_folder = 'D:\code dir\PYTHON\test\MusicV1'

def download_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        download_path = os.path.join(download_folder, f"{yt.title}.mp4")
        stream.download(output_path=download_folder, filename=f"{yt.title}.mp4")  # Download video
        audio_clip = AudioFileClip(download_path)
        audio_clip.write_audiofile(os.path.join(download_folder, f"{yt.title}.mp3"))  # Convert to MP3 with video title
        audio_clip.close()
        os.remove(download_path)  # Remove downloaded video file
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

def show_download_status_window():
    status_window = Toplevel(root)
    status_window.title("Download Status")
    
    links = entry.get().split('\n')
    for i, link in enumerate(links):
        if link.strip():
            Checkbutton(status_window, text=link, variable=IntVar(value=1) if download_video(link) else IntVar()).grid(row=i, sticky='w')

# Main GUI
root = Tk()
root.title("YouTube to MP4 Downloader")
root.geometry("400x200")

label = Label(root, text="Enter YouTube URLs (one per line):")
label.pack()

entry = Entry(root, width=50, borderwidth=3)
entry.pack()

submit_button = Button(root, text="Submit", command=submit_links)
submit_button.pack()

status_label = Label(root, text="")
status_label.pack()

status_button = Button(root, text="Show Download Status", command=show_download_status_window)
status_button.pack()

root.mainloop()
