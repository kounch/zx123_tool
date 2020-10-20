# zx123_tool

Copyright (c) 2020, kounch
All rights reserved.

## Description

Analyzes and extracts data from ZXDOS, etc. SPI flash image files.

Requires a 'zx123_hash.json' file with block estructure (e.g.: ZXD) and,
optionally, hashes to identify the blocks inside.

    Arguments:
      -h, --help          show help and exit
      -v, --version       show program's version number and exit
      -i INPUT_FILE, --input_file INPUT_FILE
                          ZX-Uno, ZXDOS, etc. File
      -d OUTPUT_DIR, --output_dir OUTPUT_DIR
                            Output directory for extracted files
      -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            Output flash file to copy
      -f, --force           Force overwrite of existing files
      -l, --list_contents List file contents
      -s, --show_hashes   Show computed hashes
      -x EXTRACT, --extract EXTRACT
                    Item(s) to extract: BIOS, Spectrum, esxdos or Core Number(s)
      -n N_CORES, --number_of_cores N_CORES
                    Number of cores to store on output file
      -m VIDEO_MODE, --video_mode VIDEO_MODE
                    Default BIOS video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
      -k KEYBOARD_LAYOUT, --keyboard_layout KEYBOARD_LAYOUT
                    Default BIOS Keyboard Layout:
                                    0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)

## Examples

Show contents of file:

    python3 zx123_tool.py -i FLASH.ZXD -l

Extract FIRMWARE.ZXD file from FLASH32.ZXD file (on Windows):

    py -3 zx123_tool.py -i FLASH32.ZXD -x BIOS

Show contents of file and extract SPECTRUM.ZXD, ESXDOS.ZXD and .ZXD files for cores 1 and 3:

    .../zx123_tool.py -l -i FLASH32.ZXD -x Spectrum,3,1,esxdos

Create a copy of FLASH32.ZXD, but removing all cores and setting BIOS default to VGA and Spectrum keyboard layout:

    .../zx123_tool.py -l -i FLASH32.ZXD -o FlashGDOSPlus.ZXD -n 0 -m 2 -k 3

## License

BSD 2-Clause License

Copyright (c) 2020, kounch
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
