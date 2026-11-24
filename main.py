
import Types
from DownloadQueue import DownloadQueue
from DownloadDatasView import DownloadDatasView
import utils
import yt_dlp_package_manager

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import messagebox
import threading

def main():

    downloadQueue: DownloadQueue = DownloadQueue()

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

    # Scrollable container
    scrollCanvas: tk.Canvas = tk.Canvas(
        master=root,
        highlightthickness=0
    )

    scrollBar: ttk.Scrollbar = ttk.Scrollbar(
        master=root,
        orient="vertical",
        command=scrollCanvas.yview
    )

    scrollableFrame: ttk.Frame = ttk.Frame(
        master=scrollCanvas
    )

    scrollableFrameWindow: int = scrollCanvas.create_window(
        (0, 0),
        window=scrollableFrame,
        anchor="nw"
    )

    scrollCanvas.configure(
        yscrollcommand=scrollBar.set
    )

    scrollCanvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollBar.pack(
        side="right",
        fill="y"
    )

    # Update scrollable area when its contents change
    def on_scrollable_frame_configure(event: tk.Event) -> None:
        scrollCanvas.configure(
            scrollregion=scrollCanvas.bbox("all")
        )

    scrollableFrame.bind(
        "<Configure>",
        on_scrollable_frame_configure
    )

    # Make the scrollable frame match the canvas width
    def on_scroll_canvas_configure(event: tk.Event) -> None:
        scrollCanvas.itemconfigure(
            scrollableFrameWindow,
            width=event.width
        )

    scrollCanvas.bind(
        "<Configure>",
        on_scroll_canvas_configure
    )

    # Mouse-wheel scrolling (Windows and macOS)
    def on_mouse_wheel(event: tk.Event) -> str:
        scrollCanvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )
        return "break"

    scrollCanvas.bind_all(
        "<MouseWheel>",
        on_mouse_wheel
    )

    # Mouse-wheel scrolling (Linux)
    scrollCanvas.bind_all(
        "<Button-4>",
        lambda event: scrollCanvas.yview_scroll(-1, "units")
    )

    scrollCanvas.bind_all(
        "<Button-5>",
        lambda event: scrollCanvas.yview_scroll(1, "units")
    )

    validateBinariesResult: utils.ValidateBinariesResult = utils.validateBinaries()

    errorMessage: str | None = validateBinariesResult.errorMessage()

    if errorMessage is not None:
        messagebox.showerror(
            title="Missing or Malfunctioning Binaries",
            message=errorMessage,
            parent=root
        )

    updatingYtDlpPlaceholderLabel: ttk.Label = ttk.Label(
        master=scrollCanvas,
        text="Updating yt-dlp..."
    )
    updatingYtDlpPlaceholderLabel.pack()

    def on_yt_dlp_update_finish():

        updatingYtDlpPlaceholderLabel.pack_forget()

        titleLabel: ttk.Label = ttk.Label(
            master=scrollCanvas,
            text="YtDownloadDesktop"
        )
        titleLabel.pack()

        # Spacer
        ttk.Frame(
            master=scrollCanvas,
            width=1,
            height=20
        ).pack()

        videoLinkEntryLabel: ttk.Label = ttk.Label(
            master=scrollCanvas,
            text="Video link"
        )
        videoLinkEntryLabel.pack()

        videoLinkEntry: ttk.Entry = ttk.Entry(
            master=scrollCanvas,
            width=52
        )
        videoLinkEntry.pack()

        downloadSettingsFrame: ttk.LabelFrame = ttk.LabelFrame(
            master=scrollCanvas,
            text="Download Settings",
            padding=10
        )

        # Media selection
        downloadVideoBooleanVar: tk.BooleanVar = tk.BooleanVar(value=True)
        downloadAudioBooleanVar: tk.BooleanVar = tk.BooleanVar(value=True)
        downloadSubtitlesBooleanVar: tk.BooleanVar = tk.BooleanVar(value=False)

        downloadMediaSelectionFrame: ttk.Frame = ttk.Frame(
            master=downloadSettingsFrame
        )
        downloadMediaSelectionFrame.pack(fill="x")

        downloadVideoCheckbox: ttk.Checkbutton = ttk.Checkbutton(
            master=downloadMediaSelectionFrame,
            text="Video",
            variable=downloadVideoBooleanVar
        )
        downloadVideoCheckbox.pack(anchor="w")
        downloadAudioCheckbox: ttk.Checkbutton = ttk.Checkbutton(
            master=downloadMediaSelectionFrame,
            text="Audio",
            variable=downloadAudioBooleanVar
        )
        downloadAudioCheckbox.pack(anchor="w")
        downloadSubtitlesCheckbox: ttk.Checkbutton = ttk.Checkbutton(
            master=downloadMediaSelectionFrame,
            text="Subtitles",
            variable=downloadSubtitlesBooleanVar
        )
        downloadSubtitlesCheckbox.pack(anchor="w")

        # Video download settings

        downloadVideoSettingsFrame: ttk.Frame = ttk.Frame(
            master=downloadSettingsFrame
        )
        downloadVideoSettingsFrame.pack(fill="x")

        downloadVideoSettingsLabel: ttk.Label = ttk.Label(
            master=downloadVideoSettingsFrame,
            text="Video settings"
        )
        downloadVideoSettingsLabel.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=(10, 2)
        )

        downloadVideoMaximumHeightFrame: ttk.Frame = ttk.Frame(
            master=downloadVideoSettingsFrame
        )
        downloadVideoMaximumHeightFrame.grid(row=2, column=0, sticky="ew", padx=5)

        downloadVideoMaximumHeightLabel: ttk.Label = ttk.Label(
            master=downloadVideoMaximumHeightFrame,
            text="Video height"
        )
        downloadVideoMaximumHeightLabel.pack(anchor="w")

        downloadVideoMaximumHeightComboBox: ttk.Combobox = ttk.Combobox(
            master=downloadVideoMaximumHeightFrame,
            values=("2160", "1440", "1080", "720", "480", "360", "240", "144")
        )
        downloadVideoMaximumHeightComboBox.pack(fill="x")

        downloadVideoCodecFrame: ttk.Frame = ttk.Frame(downloadVideoSettingsFrame)
        downloadVideoCodecFrame.grid(row=2, column=1, sticky="ew", padx=5)

        downloadVideoCodecLabel: ttk.Label = ttk.Label(
            master=downloadVideoCodecFrame,
            text="Video codec"
        )
        downloadVideoCodecLabel.pack(anchor="w")

        downloadVideoCodecComboBox: ttk.Combobox = ttk.Combobox(
            master=downloadVideoCodecFrame,
            values=tuple(codec.value for codec in Types.VideoData.videoCodecs),
            state="readonly"
        )
        downloadVideoCodecComboBox.pack(fill="x")

        def _onDownloadVideoChanged(*args) -> None:
            enabled: bool = downloadVideoBooleanVar.get()
            utils.setWidgetState(
                widget=downloadVideoSettingsFrame,
                enabled=enabled
            )

        downloadVideoBooleanVar.trace_add(
            "write",
            _onDownloadVideoChanged
        )
        _onDownloadVideoChanged()

        # Audio download settings

        downloadAudioSettingsFrame: ttk.Frame = ttk.Frame(
            master=downloadSettingsFrame
        )
        downloadAudioSettingsFrame.pack(fill="x")

        downloadAudioSettingsLabel: ttk.Label = ttk.Label(
            master=downloadAudioSettingsFrame,
            text="Audio settings"
        )
        downloadAudioSettingsLabel.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            padx=5,
            pady=(10, 2)
        )

        downloadAudioMaximumBitRateFrame: ttk.Frame = ttk.Frame(downloadAudioSettingsFrame)
        downloadAudioMaximumBitRateFrame.grid(row=4, column=0, sticky="ew", padx=5)

        downloadAudioMaximumBitRateLabel: ttk.Label = ttk.Label(
            master=downloadAudioMaximumBitRateFrame,
            text="Maximum bitrate (kbps)"
        )
        downloadAudioMaximumBitRateLabel.pack(anchor="w")

        downloadAudioMaximumBitRateComboBox: ttk.Combobox = ttk.Combobox(
            master=downloadAudioMaximumBitRateFrame,
            values=("190", "160", "140"),
            state="readonly"
        )
        downloadAudioMaximumBitRateComboBox.pack(fill="x")

        downloadAudioCodecFrame: ttk.Frame = ttk.Frame(downloadAudioSettingsFrame)
        downloadAudioCodecFrame.grid(row=4, column=1, sticky="ew", padx=5)

        downloadAudioCodecLabel: ttk.Label = ttk.Label(
            master=downloadAudioCodecFrame,
            text="Audio codec"
        )
        downloadAudioCodecLabel.pack(anchor="w")

        downloadAudioCodecComboBox: ttk.Combobox = ttk.Combobox(
            master=downloadAudioCodecFrame,
            values=tuple(codec.value for codec in Types.AudioData.audioCodecs),
            state="readonly"
        )
        downloadAudioCodecComboBox.pack(fill="x")

        def _onDownloadAudioChanged(*args) -> None:
            enabled: bool = downloadAudioBooleanVar.get()
            utils.setWidgetState(
                widget=downloadAudioSettingsFrame,
                enabled=enabled
            )
        downloadAudioBooleanVar.trace_add(
            "write",
            _onDownloadAudioChanged
        )
        _onDownloadAudioChanged()

        downloadButton: ttk.Button = ttk.Button(
            master=downloadSettingsFrame,
            text="Download"
        )
        downloadButton.pack(anchor="center")

        downloadSettingsFrame.pack()

        downloadDatasView: DownloadDatasView = DownloadDatasView(
            master=root
        )
        downloadDatasView.pack(fill="x", expand=True)

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

        def _onDownloadRequest() -> None:

            # Collect the general form data.
            videoUrl: str = videoLinkEntry.get().strip()

            isVideoDownload: bool = downloadVideoBooleanVar.get()
            isAudioDownload: bool = downloadAudioBooleanVar.get()
            isSubtitleDownload: bool = downloadSubtitlesBooleanVar.get()

            # Validate the URL.
            if not videoUrl:
                messagebox.showwarning(
                    title="Missing URL",
                    message="Please enter a video URL.",
                    parent=root
                )
                videoLinkEntry.focus_set()
                return

            # Validate media selection.
            if not any((isVideoDownload, isAudioDownload, isSubtitleDownload)):
                messagebox.showwarning(
                    title="No Media Selected",
                    message="Please select at least one media type to download.",
                    parent=root
                )
                return

            try:

                # Collect video settings.
                videoData: Types.VideoData = Types.VideoData()

                if isVideoDownload:
                    videoData = Types.VideoData(
                        maximumVideoHeight=int(
                            downloadVideoMaximumHeightComboBox.get()
                        ),
                        videoCodec=Types.VideoData.VideoCodec(
                            downloadVideoCodecComboBox.get()
                        )
                    )

                # Collect audio settings.
                audioData: Types.AudioData = Types.AudioData()

                if isAudioDownload:
                    audioData = Types.AudioData(
                        maximumAudioBitRate=int(
                            downloadAudioMaximumBitRateComboBox.get()
                        ),
                        audioCodec=Types.AudioData.AudioCodec(
                            downloadAudioCodecComboBox.get()
                        )
                    )

                # Construct the download data.
                downloadData: Types.DownloadData = Types.DownloadData(
                    url=videoUrl,
                    isVideoDownload=isVideoDownload,
                    isAudioDownload=isAudioDownload,
                    isSubtitleDownload=isSubtitleDownload,
                    videoData=videoData,
                    audioData=audioData
                )

                # Submit the download to the queue.
                if not downloadQueue.addDownload(downloadData):
                    messagebox.showerror(
                        title="Download Error",
                        message="Failed to add the download to the queue.",
                        parent=root
                    )

            except (ValueError, TypeError) as e:
                messagebox.showerror(
                    title="Invalid Download Settings",
                    message=f"One or more download settings are invalid.\n\n{e}",
                    parent=root
                )

            videoLinkEntry.bind(
                "<Return>",
                lambda event: _onDownloadRequest()
            )

            # Download button click.
            downloadButton.bind(
                "<Button-1>",
                lambda event: _onDownloadRequest()
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
