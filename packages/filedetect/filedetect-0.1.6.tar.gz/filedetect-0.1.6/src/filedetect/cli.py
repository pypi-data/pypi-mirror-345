# SPDX-FileCopyrightText: 2025-present Marceau <git@marceau-h.fr>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from argparse import ArgumentParser, Namespace

from .FileDetect import FileDetect


def run(args: Namespace) -> FileDetect:
    return FileDetect.find(
        path=args.path,
        format=args.format,
        deep=args.deep,
        only_stems=args.only_stems,
    )

def parse_args() -> Namespace:
    from .Formats import Formats
    from .__about__ import __version__

    formats_ = [f"- {format.name}\n\t- {format.value}\n" for format in Formats]
    formats_ = "\n".join(formats_)
    formats_ = f"""Available file types: \n{formats_}"""

    parser = ArgumentParser(description="Find files in a directory.")
    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to search in.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="",
        help="Format to search for.",
        choices=[f.name for f in Formats] + ["all", ""],
    )
    parser.add_argument(
        "--deep",
        type=int,
        default=-1,
        help="Depth of the search (-1 for infinite depth).",
    )
    parser.add_argument(
        "--only_stems",
        type=str,
        help="Only include files with these stems.",
    )
    parser.add_argument(
        "--suffixes",
        type=str,
        help="File suffixes to search for (e.g., .mp4, .jpg) if format is not specified.",
    )
    parser.add_argument(
        "--list_formats",
        action="version",
        version=formats_,
        help="List all available formats and exit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit.",
    )

    args = parser.parse_args()

    # if args.list_formats:
    #     from .Formats import Formats
    #     print("Available file types:")
    #     for file_type in Formats:
    #         print(f"- {file_type.name}\n\t- {file_type.value}\n")
    #
    #     exit(0)

    if args.suffixes:
        args.suffixes = set(a.strip() for a in args.suffixes.split(",")if a.strip())
    else:
        args.suffixes = None

    if args.only_stems:
        args.only_stems = set(a.strip() for a in args.only_stems.split(",") if a.strip())
    else:
        args.only_stems = None

    if args.format:
        args.format = args.format.lower()
        if args.format in {"", "all"}:
            args.format = None

    return args

def main() -> None:
    args = parse_args()
    finder = run(args)
    files = "\n".join(str(file) for file in finder) # \n not ok in f-strings prior to 3.12
    print(
f"""\
Found {len(finder)} files matching the criteria in {args.path}:
File type: {args.format}
Deepness: {args.deep}
Only stems: {args.only_stems}
Files:
{files}\
"""
    )
if __name__ == "__main__":
    main()
