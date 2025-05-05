#!/usr/bin/env python3

import argparse
import logging
import os
import os.path
import time

import epub_meta

logging.basicConfig(format="%(levelname)s:%(funcName)s:%(message)s", level=logging.INFO)
log = logging.getLogger("epubsetdate")


def main():
    cmd_parse = argparse.ArgumentParser(
        description="Print filename and author " + "of EPub files"
    )
    cmd_parse.add_argument("files", nargs="+", help="list of files to be processed")

    args = cmd_parse.parse_args()

    for inf_name in args.files:
        lu_str = ""
        try:
            mdata = epub_meta.get_epub_metadata(inf_name)
            if "authors" in mdata and mdata["authors"]:
                print(f"{inf_name}\t{', '.join(mdata['authors'])}")
        except epub_meta.exceptions.EPubException:
            log.exception(
                "Invalid EPub file or %s isn't an EPub document at all!",
                os.path.realpath(inf_name),
            )
