from dataclasses import dataclass

from virtual_fs import FSPath


@dataclass
class DownloadRequest:
    url: str
    outmp3: FSPath
    download_vid: bool
    download_date: bool
