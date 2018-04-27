#! /usr/bin/env python
# coding=utf-8
"""  """

import os
import glob

def get_filenames_recursively(path):
    if os.path.isfile(path):
        return [path]
    if not path.endswith("/"):
        path = path + "/"
    filenames = []
    for filename in glob.iglob(path + '**/*', recursive=True):
        filenames.append(filename)
    return filenames