#!/usr/bin/python
#
# Copyright 2015 The Pennsylvania State University.
#
# Created by Matt Hansen (mah60@psu.edu) on 2015-02-13.
#
# Extracts the .exe or .msi file using the 7z utility.

import os
import sys
import subprocess
import shutil
import stat

from autopkglib import Processor, ProcessorError


__all__ = ["WinInstallerExtractor"]


class WinInstallerExtractor(Processor):
    description = "Extracts the Windows archive meta-data using 7z."
    input_variables = {
        "exe_path": {
            "required": False,
            "description": "Path to exe or msi, defaults to %pathname%",
        },
        "preserve_paths": {
            "required": False,
            "description": "eXtract archive with full paths, defaults to 'True'",
        },
        "extract_dir": {
            "required": True,
            "description": "Output path for the extracted archive.",
        },
        "ignore_pattern": {
            "required": False,
            "description": "Wildcard pattern to ignore files from the archive.",
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the extraction.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):

        exe_path = self.env.get('exe_path', self.env.get('pathname'))
        preserve_paths = self.env.get('preserve_paths', 'True')
        working_directory = self.env.get('RECIPE_CACHE_DIR')
        extract_directory = self.env.get('extract_dir', 'ExtractedInstaller')
        ignore_pattern = self.env.get('ignore_pattern', '')
        ignore_errors = self.env.get('ignore_errors', 'False')
        verbosity = self.env.get('verbose', 0)

        extract_flag = 'x' if preserve_paths == 'True' else 'e'
        extract_path = "%s/%s" % (working_directory, extract_directory)

        source_7z = os.path.join(os.path.dirname(os.path.abspath(__file__)), '7z')
        dir_7z = os.path.join(working_directory, '7z')
        file_7z = os.path.join(dir_7z, '7z')

        shutil.copytree(source_7z, dir_7z)
        os.chmod(file_7z, stat.S_IEXEC)

        self.output("Extracting: %s" % exe_path)
        cmd = [file_7z, extract_flag, '-y', '-o%s' % extract_path , exe_path]

        if ignore_pattern:
            cmd.append('-x!%s' % ignore_pattern)

        try:
            if verbosity > 1:
                subprocess.check_call(cmd)
            else:
                subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            if ignore_errors != 'True':
                raise

        self.output("Extracted Archive Path: %s" % extract_path)

        shutil.rmtree(dir_7z)

if __name__ == '__main__':
    processor = WinInstallerExtractor()
    processor.execute_shell()
