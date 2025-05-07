# FileDetect

[![PyPI - Version](https://img.shields.io/pypi/v/filedetect.svg)](https://pypi.org/project/filedetect)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/filedetect.svg)](https://pypi.org/project/filedetect)

-----

## Table of Contents

- [Installation](#installation)
- [Description](#description)
- [Usage](#usage)
- [License](#license)

## Installation

```bash
pip install filedetect
```

## Description
`filedetect` is a Python package that provides a simple way to detect file formats in a directory tree. 
This project relies on the `pathlib` library to traverse the directory tree and separate files suffixes from their full name.
One can specify the suffixes to detect, the maximum depth of detection, and the formats to look for.

For convinence, some common suffixes are already defined for the following formats:
- video => {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp", ".3g2", ".vob", ".ts", ".m2ts", ".rmvb", ".mxf", ".drc", ".amv", ".f4v", ".svi", ".m1v", ".m2v"}
- audio => {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".alac", ".aiff"}
- image => {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heif", ".raw"}
- plain_text => {".txt"}
- csv => {".csv"}
- json => {".json"}
- html => {".html", ".htm"}
- xml => {".xml"}
- excel => {".xls", ".xlsx", ".odf", ".ods"}
- pdf => {".pdf"}
- doc => {".doc", ".docx", ".odt"}
- ppt => {".ppt", ".pptx", ".odp"}
- archive => {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tar.gz", ".tar.bz2", ".tar.xz"}
- text => {".txt", ".csv", ".json", ".xml", ".html", ".htm", ".py", ".java", ".c", ".cpp", ".h", ".js", ".css", ".md", ".rst", ".tex", ".sql", ".css", ".yaml", ".yml", ".toml", ".ini", ".properties", ".log"}

But you can also specify your own suffixes to detect by passing a set of suffixes to the `suffixes` parameter instead of the `format` parameter.
And you also are welcome to suggest new formats to be added to the package or existing formats to be updated by creating a pull request or an issue on the [GitHub repository](https://github.com/Marceau-h/filedetect/) !

## Usage
### CLI
```bash
filedetect [-h] [--list_formats] [--version] path [--format {video,image,audio,plain_text,csv,json,html,xml,excel,pdf,doc,ppt,archive,text,all,}] [--deep int] [--only_stems stem1,stem2] [--suffixes sfx1,sfx2]
```

- The `path` argument is required and should be the path to the directory you want to scan.

- You can either specify the `--format` or the `--suffixes` to detect, but not both at the same time. If both aren't specified, all formats will be detected.
- The `--only_stems` option allows you to specify a set of stems to detect to filter for but is optional.
- The `--deep` option allows you to specify the maximum depth of detection. If not specified, the default value is -1, which means unlimited depth.

- The `--list_formats` option allows you to list all the formats available in the package and their corresponding suffixes and exits.
- The `--version` option allows you to display the version of the package and exits.
- The `--help` option allows you to display the help message and exits."


### Python
```python
from filedetect import FileDetect

detector = FileDetect.find(
path="path/to/dir",
format=None, # ["video", "audio", "image", "text", "csv"; "json", "html"] | None for all formats
deep=-1, # positive int for maximum depth of detection or -1 for unlimited
only_stems=None, # None | a set of stems to detect,
suffixes=None, # None | a set of suffixes to detect (in place of format),
)
print(detector.result)
```

or 


```python
from filedetect import FileDetect

detector = FileDetect(
format=None, # ["video", "audio", "image", "text", "csv"; "json", "html"] | None for all formats
deep=-1, # positive int for maximum depth of detection or -1 for unlimited
only_stems=None, # None | a set of stems to detect,
suffixes=None, # None | a set of suffixes to detect (in place of format),
)

detector.run(
    path="path/to/dir",
)

detector.run(
    path="another/path/to/dir",
)

...

print(detector.result)
```


## License

`filedect` is distributed under the terms of the [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) license.
