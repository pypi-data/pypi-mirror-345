# SPDX-FileCopyrightText: 2025-present Marceau <git@marceau-h.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from enum import Enum

class Formats(Enum):
    video = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2", ".vob", ".ts", ".m2ts", ".rmvb", ".mxf", ".drc", ".amv", ".f4v", ".svi", ".m1v", ".m2v"}
    image = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heif", ".raw"}
    audio = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".alac", ".aiff"}
    plain_text = {".txt"}
    csv = {".csv"}
    json = {".json"}
    html = {".html", ".htm"}
    xml = {".xml"}
    excel = {".xls", ".xlsx", ".odf", ".ods"}
    pdf = {".pdf"}
    doc = {".doc", ".docx", ".odt"}
    ppt = {".ppt", ".pptx", ".odp"}
    archive = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tar.gz", ".tar.bz2", ".tar.xz"}
    text = {".txt", ".csv", ".json", ".xml", ".html", ".htm", ".py", ".java", ".c", ".cpp", ".h", ".js", ".css", ".md", ".rst", ".tex", ".sql", ".css", ".yaml", ".yml", ".toml", ".ini", ".properties", ".log"}

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: "Formats") -> bool:
        if isinstance(other, Formats):
            return self.value == other.value
        return False

    def __ne__(self, other: "Formats") -> bool:
        if isinstance(other, Formats):
            return self.value != other.value
        return True

    def __contains__(self, other: str) -> bool:
        if isinstance(other, str):
            return other in self.value
        return False
