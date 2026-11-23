
import Types
from DownloadQueue import DownloadQueue
from DownloadDatasView import DownloadDatasView
import utils

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

import threading
import yt_dlp_package_manager

def main():

    downloadQueue: DownloadQueue = DownloadQueue()

    def on_video_link_entry_key_press(event: tk.Event):
        print("Current value:", event.widget.get())
        videoUrl: str = event.widget.get()
        downloadQueue.addDownload(
            Types.DownloadData(
                url=videoUrl
            )
        )

    root: tk.Tk = tk.Tk()
    root.title("YtDownloadDesktop")
    root.minsize(
        width=640,
        height=480
    )

    default_font: tkFont.Font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(
        family="Segoe UI",
        size=10
    )

    text_font: tkFont.Font = tkFont.nametofont("TkTextFont")
    text_font.configure(
        family="Segoe UI",
        size=10
    )

    validateBinariesResult = utils.validateBinaries()
    binariesNotWorkingMessage: tk.StringVar = tk.StringVar(
        value=""
    )

    updatingYtDlpPlaceholderLabel: ttk.Label = ttk.Label(
        master=root,
        text="Updating yt-dlp..."
    )
    updatingYtDlpPlaceholderLabel.pack()

    def on_yt_dlp_update_finish():

        updatingYtDlpPlaceholderLabel.pack_forget()

        titleLabel: ttk.Label = ttk.Label(
            master=root,
            text="YtDownloadDesktop"
        )
        titleLabel.pack()

        # Spacer
        ttk.Frame(
            master=root,
            width=1,
            height=20
        ).pack()

        videoLinkEntryLabel: ttk.Label = ttk.Label(
            master=root,
            text="Video link"
        )
        videoLinkEntryLabel.pack()

        videoLinkEntry: ttk.Entry = ttk.Entry(
            master=root
        )
        videoLinkEntry.bind(
            "<Return>",
            on_video_link_entry_key_press
        )
        videoLinkEntry.pack()

        downloadDatasView: DownloadDatasView = DownloadDatasView(
            master=root
        )
        downloadDatasView.pack(fill="both", expand=True)

        def updateDownloadQueueView() -> None:
            downloadDatas: Types.DownloadDatas = downloadQueue.getDownloads()
            downloadDatasView.updateDownloads(downloadDatas)
            root.after(
                ms=2000,
                func=updateDownloadQueueView
            )

        root.after(
            ms=0,
            func=updateDownloadQueueView
        )

    def update_yt_dlp_worker():
        try:
            yt_dlp_package_manager.update_yt_dlp()
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

"""
        testThumbnail: tk.PhotoImage = tk.PhotoImage(file="test.png")
        downloadThumbnailLabel.image = testThumbnail
"""
