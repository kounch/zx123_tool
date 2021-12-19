#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
"""
Copyright (c) 2021, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

This is a tool that analyzes, extracts and injects data in SPI flash image
files for ZX-Uno, ZXDOS and similar devices.

These are the main features:

- List the contents of a ZX-Uno, etc. SPI flash image, showing, if possible,
  the version of BIOS, esxdos, main Spectrum core and optional cores, Spectrum
  ROMs and several BIOS settings
- Extract BIOS, esxdos ROM, Spectrum core and/or other cores, Spectrum ROMs to
  individual files
- Change some BIOS default options (video mode, keyboard layout, default core,
  default ROM, etc.)
- Add or replace FPGA cores and/or Spectrum ROM images (from individual ROM
  files or ROMPack files)
- Wipe with zeros all Cores and ZX Spectrum ROMs data
- If supplied a different kind of file (like a core or BIOS installation file)
  it will also try to identify its contents

Requires a zx123_hash.json file with block structure for a kind of SPI flash
file (e.g.: ZXD) and, optionally, hashes to identify the blocks inside.
"""

import os
import sys
import pathlib
from shutil import copy
import zx123_tool as zx123
import zx123_tool_gui

MY_DIRPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_DIRPATH)
JSON_DIR = APP_RESDIR = MY_DIRPATH
if sys.platform == 'darwin':
    JSON_DIR = os.path.join(os.environ.get('HOME'), 'Library',
                            'Application Support', 'ZX123 Tool')
    APP_RESDIR = os.path.abspath(os.path.join(MY_DIRPATH, '..', 'Resources'))
elif sys.platform == 'win32':
    JSON_DIR = os.path.join(os.path.expandvars('%LOCALAPPDATA%'), 'ZX123 Tool')
    APP_RESDIR = MY_DIRPATH


def main():
    """Main Routine"""

    if not os.path.isdir(JSON_DIR):
        print('Initializing Resources...')
        pathlib.Path(JSON_DIR).mkdir(parents=True, exist_ok=True)
        copy(os.path.join(APP_RESDIR, 'zx123_hash.json'), JSON_DIR)
        for str_ext in ['ZX1', 'ZX2', 'ZXD']:
            copy(os.path.join(APP_RESDIR, f'FLASH16_empty.{str_ext}.zip'),
                 JSON_DIR)

    if len(sys.argv) > 1:
        if sys.argv[1] == '--command':
            sys.argv = sys.argv[:1] + sys.argv[2:]
            zx123.MY_DIRPATH = JSON_DIR
            zx123.main()
            sys.exit(0)

    zx123_tool_gui.MY_DIRPATH = MY_DIRPATH
    zx123_tool_gui.JSON_DIR = JSON_DIR
    zx123_tool_gui.APP_RESDIR = APP_RESDIR

    app = zx123_tool_gui.App()
    app.mainloop()


if __name__ == '__main__':
    main()
