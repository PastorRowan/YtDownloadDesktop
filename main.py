
import tkinter as tk
from tkinter import ttk
import threading
import ytdlp_package_manager

# def download():

def on_video_link_entry_key_press(event: tk.Event):
    print("Current value:", event.widget.get())

def main():

    root: tk.Tk = tk.Tk()
    root.title("YtDownloadDesktop")
    root.minsize(
        width=320,
        height=240
    )

    updatingYtDlpPlaceholderLabel = tk.Label(
        master=root,
        text="Updating yt-dlp..."
    )
    updatingYtDlpPlaceholderLabel.pack()

    def on_yt_dlp_update_finish():

        updatingYtDlpPlaceholderLabel.pack_forget()

        titleLabel: tk.Label = tk.Label(
            master=root,
            text="YtDownloadDesktop"
        )
        titleLabel.pack()

        videoLinkEntry: tk.Entry = tk.Entry(
            master=root
        )
        videoLinkEntry.bind(
            "<Return>",
            on_video_link_entry_key_press
        )
        videoLinkEntry.pack()

        downloadFrame: tk.Frame = tk.Frame(
            master=root
        )
        downloadFrame.pack()
        downloadThumbnailLabel: tk.Label = tk.Label(
            master=downloadFrame,
            text="Video Thumbnail"
        )
        downloadThumbnailLabel.pack()
        downloadProgressBar: ttk.Progressbar = ttk.Progressbar(
            master=downloadFrame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0
        )
        downloadProgressBar.pack(fill="x")
        

    def update_yt_dlp_worker():
        try:
            ytdlp_package_manager.update_yt_dlp()
        except Exception as e:
            print("Failed to update yt-dlp:", e)
        finally:
            root.after(0, on_yt_dlp_update_finish)

    t = threading.Thread(
        target=update_yt_dlp_worker
    )
    t.start()

    root.mainloop()

if __name__ == "__main__":
    main()
