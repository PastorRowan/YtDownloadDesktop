
import Types

import tkinter as tk
from tkinter import ttk

class DownloadDataView(ttk.Frame):

    def __init__(
        self,
        master: tk.Misc,
        downloadData: Types.DownloadData
    ) -> None:
        super().__init__(
            master
        )

        self.downloadId = downloadData.id

        self.titleLabel = ttk.Label(
            master=self,
            anchor="w"
        )
        self.titleLabel.pack(fill="x")

        self.progressBar = ttk.Progressbar(
            master=self,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
            style="Download.Horizontal.TProgressbar"
        )
        self.progressBar.pack(fill="x")

        self.updateDownloadData(downloadData)

    def updateDownloadData(
        self,
        downloadData: Types.DownloadData
    ) -> None:

        title = downloadData.title or "Preparing download..."
        progress = downloadData.progress * 100

        if title != self.titleLabel.cget("text"):
            self.titleLabel.configure(
                text=title
            )

        if progress != self.progressBar.cget("value"):
            self.progressBar.configure(
                value=progress
            )