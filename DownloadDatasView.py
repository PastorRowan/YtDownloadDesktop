
import Types
from DownloadDataView import DownloadDataView

import tkinter as tk
from tkinter import ttk

class DownloadDatasView(ttk.Frame):

    def __init__(
        self,
        master: tk.Misc
    ) -> None:
        super().__init__(
            master
        )

        self.downloadDataViews: dict[
            Types.DownloadData.Id,
            DownloadDataView
        ] = {}

        self.downloadsContainer = ttk.Frame(
            master=self
        )
        self.downloadsContainer.pack(
            fill="both",
            expand=True
        )

    def addDownload(
        self,
        downloadData: Types.DownloadData
    ) -> DownloadDataView:

        downloadDataView = DownloadDataView(
            master=self.downloadsContainer,
            downloadData=downloadData
        )

        downloadDataView.pack(
            fill="x",
            expand=True,
            padx=5,
            pady=3
        )

        self.downloadDataViews[downloadData.id] = downloadDataView

        return downloadDataView

    def updateDownload(
        self,
        downloadData: Types.DownloadData
    ) -> None:
        downloadDataView = self.downloadDataViews.get(
            downloadData.id
        )
        if downloadDataView is not None:
            downloadDataView.updateDownloadData(downloadData)

    def removeDownload(
        self,
        downloadId: Types.DownloadData.Id
    ) -> None:

        downloadDataView = self.downloadDataViews.pop(
            downloadId,
            None
        )

        if downloadDataView is not None:
            downloadDataView.destroy()

    def updateDownloads(
        self,
        downloadDatas: Types.DownloadDatas
    ) -> None:

        # Remove views for downloads that no longer exist.
        for downloadId in list(self.downloadDataViews.keys()):
            if downloadId not in downloadDatas:
                self.removeDownload(downloadId)

        # Add or update download views.
        for downloadId, downloadData in downloadDatas.items():
            downloadDataView = self.downloadDataViews.get(downloadId)
            if downloadDataView is None:
                self.addDownload(downloadData)
            else:
                downloadDataView.updateDownloadData(downloadData)

    def clearDownloads(self) -> None:
        for downloadDataView in self.downloadDataViews.values():
            downloadDataView.destroy()
        self.downloadDataViews.clear()
