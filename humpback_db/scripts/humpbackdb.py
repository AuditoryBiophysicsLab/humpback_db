#! /usr/bin/env python
"""

"""

from attrs_utils.interop import from_docopt
import sys
import os
from os import path
from typing import Optional, List
from humpback_db.core import Metadata, Args
import lxml


def main(inputargs) -> int:
    args = from_docopt(inputargs, docstring=__doc__)
    validate_input(args)
    validate_dirs(args.root_dir)
    return 0


def validate_input(args) -> None:
    error_text = ''
    if not os.path.isdir(args.root_dir):
        error_text += f'\n\t{args.root_dir} is not a directory!'
    if error_text:
        exit(f'Found the following problems with the input:{error_text}')


def validate_dirs(root: str) -> None:
    def is_unique(mylist: List) -> bool:
        return len(mylist) == len(set(mylist))

    def is_bijective(tifflist: List, metalist: List) -> bool:
        tiff_stripped = sorted([path.splitext(x)[0] for x in tifflist])
        meta_stripped = sorted([path.splitext(x)[0] for x in metalist])
        return tiff_stripped == meta_stripped

    error_text = ''
    for dirpath, dirnames, fnames in os.walk(root):
        tiffs = [f for f in fnames if path.splitext(f)[1].lower() == ".tiff"]
        metadata = [f for f in fnames if path.splitext(f)[1].lower() == ".xml"]
        if not (is_unique(tiffs) and is_unique(metadata)):
            error_text += f'\n\tduplicate files found in {path.abspath(dirpath)}'
        if not is_bijective(tiffs, metadata):
            error_text += f'\n\tdifferent number of metadata (n = {len(metadata)}) and tiff (n = {len(tiffs)})' \
                          f' found in {path.abspath(dirpath)}'

    if error_text:
        exit(f'Fund the following problems with the target root directory {root}:{error_text}')


def read_metadata(xml_file: str) -> Metadata:
    pass


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
