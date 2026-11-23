
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
            value=0
        )
        self.progressBar.pack(fill="x")

        self.updateDownloadData(downloadData)

    def updateDownloadData(
        self,
        downloadData: Types.DownloadData
    ) -> None:
        self.titleLabel.configure(
            text=downloadData.title or "Preparing download..."
        )
        self.progressBar.configure(
            value=downloadData.progress * 100
        )
