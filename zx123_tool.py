#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
# pylint: disable=too-many-lines
"""
Copyright (c) 2020-2021, kounch
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
- Create a copy of the flash image and, optionally, and/or truncate some (or
  all) of the optional cores
- Change some BIOS default options (video mode, keyboard layout, default core,
  default ROM, etc.)
- Add or replace FPGA cores and/or Spectrum ROM images (from individual ROM
  files or ROMPack files)
- Wipe with 0s all Cores and ZX Spectrum ROMs data
- List, add or extract ROM files from a ZX1 ROMPack v2 file
- If supplied a different kind of file (like a core or BIOS installation file)
  it will also try to identify its contents

Requires a zx123_hash.json file with block structure for a kind of SPI flash
file (e.g.: ZXD) and, optionally, hashes to identify the blocks inside.
"""

from __future__ import print_function
import logging
import sys
import argparse
import os
import json
import hashlib
from binascii import unhexlify
import struct
import ssl
from zipfile import ZipFile, is_zipfile
import tempfile
import shutil
import ctypes
if sys.version_info.major == 3:
    import urllib.request
if os.name == 'nt':
    import msvcrt  # pylint: disable=import-error

__MY_VERSION__ = '3.2.1'

MAIN_URL = 'https://raw.githubusercontent.com/kounch/zx123_tool/main'
MY_DIRPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_DIRPATH)
STR_OUTDIR = ''
IS_COL_TERM = False

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter(
    '%(asctime)s [%(levelname)-5.5s] - %(name)s: %(message)s')
LOG_STREAM = logging.StreamHandler(sys.stdout)
LOG_STREAM.setFormatter(LOG_FORMAT)
LOGGER.addHandler(LOG_STREAM)

if sys.version_info < (3, 6, 0):
    LOGGER.error('This software requires Python version 3.6 or greater')
    sys.exit(1)

ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=protected-access


def main():
    """Main routine"""

    global STR_OUTDIR  # pylint: disable=global-statement

    enable_term_col()

    LOGGER.debug('Starting up...')
    arg_data = parse_args()

    str_file = arg_data['input_file']
    STR_OUTDIR = arg_data['output_dir']
    output_file = arg_data['output_file']

    fulldict_hash = load_json_bd(str_file, output_file, arg_data['update'])
    if not fulldict_hash:
        sys.exit(2)

    if arg_data['stats']:
        print_stats(fulldict_hash, arg_data['detail'])
        sys.exit(3)

    # Analyze/initialize input file and output dir location and extension
    b_new_img = False
    if not str_file:
        if arg_data['output_file']:
            str_file, _ = unzip_image(MY_DIRPATH, arg_data['output_file'],
                                      fulldict_hash, arg_data['force'])
            b_new_img = True
            arg_data['force'] = True
            if not str_file:
                sys.exit(3)
        else:
            LOGGER.error("There's no input file")
            sys.exit(3)
    else:
        if not STR_OUTDIR:
            STR_OUTDIR = os.path.dirname(str_file)

    str_extension, dict_hash, filetype = detect_file(str_file, fulldict_hash)

    if filetype == 'FlashImage':
        supported_exts = ['ZX1', 'ZX2', 'ZXD', 'ZXT']

        # List main ROMs, Cores and BIOS settings
        if arg_data['list']:
            list_zxdata(str_file, dict_hash, arg_data['show_hashes'],
                        arg_data['check_updated'], arg_data['1core'],
                        arg_data['2mb'], arg_data['detail'])

        # List ZX Spectrum ROMs
        if arg_data['roms']:
            list_romsdata(str_file, fulldict_hash, str_extension,
                          arg_data['show_hashes'])

        # Extract Cores and/or ROMs
        for x_item in arg_data['extract']:
            extractfrom_zxdata(str_file, x_item, fulldict_hash, STR_OUTDIR,
                               str_extension, arg_data['force'],
                               not arg_data['roms'])

        # Expand image file if needed
        if arg_data['expand_flash']:
            if not output_file:
                output_file = str_file
            img_len = 33554432
            if expand_image(str_file, output_file, img_len, arg_data['force']):
                arg_data['force'] = True
                str_file = output_file

        # Try to update contents from internet
        if arg_data['update'] != '':
            if str_extension in supported_exts:
                print('\nStarting update...')
                if not output_file:
                    output_file = str_file
                arr_upd = []
                if arg_data['update'].lower() in ['all', 'bios']:
                    prep_update_zxdata(arr_upd, str_file, fulldict_hash,
                                       str_extension, ['BIOS'])
                if arg_data['update'].lower() in ['all', 'spectrum']:
                    prep_update_zxdata(arr_upd,
                                       str_file,
                                       fulldict_hash,
                                       str_extension, ['Spectrum'],
                                       get_1core=arg_data['1core'],
                                       get_2mb=arg_data['2mb'])
                if arg_data['update'].lower() in ['all', 'special']:
                    prep_update_zxdata(arr_upd, str_file, fulldict_hash,
                                       str_extension, ['Special'])
                if arg_data['update'].lower() in ['all', 'cores']:
                    prep_update_cores(arr_upd,
                                      str_file,
                                      fulldict_hash,
                                      str_extension,
                                      b_new_img,
                                      get_1core=arg_data['1core'],
                                      get_2mb=arg_data['2mb'])
                if b_new_img or arg_data['update'].lower() == 'roms':
                    prep_update_roms(arr_upd, fulldict_hash, str_extension,
                                     b_new_img)
                if arg_data['update'].lower() == 'arcade':
                    prep_update_zxdata(arr_upd, str_file, fulldict_hash,
                                       str_extension, ['BIOS'])
                    prep_update_cores(arr_upd, str_file, fulldict_hash,
                                      str_extension, b_new_img, 'arcade')
                    prep_update_roms(arr_upd, fulldict_hash, str_extension,
                                     b_new_img, True)
                if arg_data['update'].lower() == 'varcade':
                    prep_update_zxdata(arr_upd, str_file, fulldict_hash,
                                       str_extension, ['BIOS'], True)
                    prep_update_cores(arr_upd, str_file, fulldict_hash,
                                      str_extension, b_new_img, 'varcade')
                    prep_update_roms(arr_upd, fulldict_hash, str_extension,
                                     b_new_img, True)

                if arr_upd:
                    if inject_zxfiles(str_file,
                                      arr_upd,
                                      output_file,
                                      fulldict_hash,
                                      str_extension,
                                      b_force=arg_data['force'])[0]:
                        arg_data['force'] = True
                        str_file = output_file
                else:
                    print('Nothing to update')

        # Wipe Secondary Cores and all ZX Spectrum ROMs
        if arg_data['wipe_flash']:
            if str_extension in supported_exts:
                if not output_file:
                    output_file = str_file
                wipe_zxdata(str_file, output_file, dict_hash,
                            arg_data['video_mode'],
                            arg_data['keyboard_layout'],
                            arg_data['boot_timer'], arg_data['force'])

        # Inject Cores and/or ROMs
        if arg_data['inject']:
            if str_extension in supported_exts:
                b_force = arg_data['force']
                if arg_data['wipe_flash']:
                    b_force = True
                    str_file = output_file
                else:
                    if not output_file:
                        output_file = str_file
                inject_zxfiles(
                    str_file, arg_data['inject'], output_file, fulldict_hash,
                    str_extension, arg_data['video_mode'],
                    arg_data['keyboard_layout'], arg_data['boot_timer'],
                    arg_data['default_core'], arg_data['default_rom'], b_force)
            else:
                LOGGER.error('Not a valid filetype: %s', str_extension)

        # Truncate image
        elif arg_data['output_file'] and not arg_data['wipe_flash']:
            savefrom_zxdata(str_file, dict_hash, arg_data['output_file'],
                            arg_data['n_cores'], arg_data['video_mode'],
                            arg_data['keyboard_layout'],
                            arg_data['boot_timer'], arg_data['default_core'],
                            arg_data['default_rom'], arg_data['force'])
    elif filetype == 'ROMPack v2':
        # List ZX Spectrum ROMs
        if not arg_data['extract'] and not arg_data['inject']:
            list_romsdata(str_file, fulldict_hash, 'RPv2',
                          arg_data['show_hashes'], True)

        # Extract ROMs
        for x_item in arg_data['extract']:
            extractfrom_zxdata(str_file, x_item, fulldict_hash, STR_OUTDIR,
                               'RPv2', arg_data['force'], False)

        # Inject  ROMs
        if arg_data['inject']:
            if not output_file:
                output_file = str_file
            inject_zxfiles(str_file, arg_data['inject'], output_file,
                           fulldict_hash, 'RPv2', -1, -1, -1, -1,
                           arg_data['default_rom'], arg_data['force'])

    else:
        # Convert between Standard and Spectrum Core?
        if arg_data['convert_core']:
            if output_file:
                print(f'Trying to convert {str_file}...')
                convert_core(str_file, dict_hash, output_file,
                             arg_data['force'])
            else:
                LOGGER.error('Output file not defined!')
        else:
            # File header unknown, try to guess only from hash and size
            try:
                find_zxfile(str_file, fulldict_hash, str_extension,
                            arg_data['show_hashes'], arg_data['detail'])
            except FileNotFoundError:
                LOGGER.error('Input file not found!')

    print('')
    LOGGER.debug("Finished.")


def enable_term_col():
    """
    Enable TERM colours (Windows 10)
    https://stackoverflow.com/questions/53574442/how-to-reliably-test-color-capability-of-an-output-terminal-in-python3
    """

    global IS_COL_TERM  # pylint: disable=global-statement

    if os.name == 'nt':
        enable_virtual_terminal_processing = 4
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        hstdout = msvcrt.get_osfhandle(sys.stdout.fileno())
        mode = ctypes.c_ulong()  # pylint: disable = no-value-for-parameter
        IS_COL_TERM = kernel32.GetConsoleMode(
            hstdout, ctypes.byref(mode)) and (
                mode.value & enable_virtual_terminal_processing != 0)

        if not IS_COL_TERM:
            IS_COL_TERM = kernel32.SetConsoleMode(
                hstdout, mode.value | enable_virtual_terminal_processing) > 0
    else:
        IS_COL_TERM = True


# https://ozzmaker.com/add-colour-to-text-in-python/
class Colours:
    """Colour handling for terminal"""
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[1;36m'
    ENDC = '\033[m'


def printcol(str_col, str_txt, end=''):
    """Print with TERM colour"""
    if IS_COL_TERM:
        print(f'{str_col}{str_txt}{Colours.ENDC}', end=end)
    else:
        print(str_txt, end=end)


def parse_args():
    """
    Parses command line
    :return: Dictionary with different options
    """
    global LOGGER  # pylint: disable=global-statement
    global IS_COL_TERM  # pylint: disable=global-statement

    values = {}
    values['input_file'] = ''
    values['output_dir'] = ''
    values['output_file'] = ''
    values['force'] = False
    values['list'] = False
    values['detail'] = False
    values['stats'] = False
    values['roms'] = False
    values['show_hashes'] = False
    values['extract'] = []
    values['n_cores'] = -1
    values['inject'] = []
    values['wipe_flash'] = False
    values['expand_flash'] = False
    values['convert_core'] = False
    values['1core'] = False
    values['2mb'] = False
    values['update'] = ''
    values['check_updated'] = False
    values['video_mode'] = -1
    values['keyboard_layout'] = -1
    values['default_core'] = -1
    values['default_rom'] = -1
    values['boot_timer'] = -1

    parser = argparse.ArgumentParser(
        description='ZX123 Tool',
        epilog='Analyze and extract data from ZXDOS, etc. files')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version=f'%(prog)s {__MY_VERSION__}')
    parser.add_argument('-i',
                        '--input_file',
                        required=False,
                        action='store',
                        dest='input_file',
                        help='ZX-Uno, ZXDOS, etc. File')
    parser.add_argument('-d',
                        '--output_dir',
                        required=False,
                        action='store',
                        dest='output_dir',
                        help='Output directory for extracted files')
    parser.add_argument('-o',
                        '--output_file',
                        required=False,
                        action='store',
                        dest='output_file',
                        help='Output file to copy')
    parser.add_argument('-f',
                        '--force',
                        required=False,
                        action='store_true',
                        dest='force',
                        help='Force overwrite of existing files')
    parser.add_argument('-l',
                        '--list_contents',
                        required=False,
                        action='store_true',
                        dest='list_contents',
                        help='List file contents')
    parser.add_argument('-D',
                        '--details',
                        required=False,
                        action='store_true',
                        dest='detail',
                        help='Show Core Features')
    parser.add_argument('--stats', action='store_true', dest='stats')
    parser.add_argument('-r',
                        '--roms',
                        required=False,
                        action='store_true',
                        dest='parse_roms',
                        help='Parse Spectrum ROMs data')
    parser.add_argument('-s',
                        '--show_hashes',
                        required=False,
                        action='store_true',
                        dest='show_hashes',
                        help='Show computed hashes')
    parser.add_argument('-x',
                        '--extract',
                        required=False,
                        action='store',
                        dest='extract',
                        help='Item(s) to extract')
    parser.add_argument('-n',
                        '--number_of_cores',
                        required=False,
                        type=int,
                        action='store',
                        dest='n_cores',
                        help='Number of cores to store on output file')
    parser.add_argument('-a',
                        '--add',
                        required=False,
                        action='append',
                        dest='inject',
                        help='Item to inject')
    parser.add_argument('-w',
                        '--wipe',
                        required=False,
                        action='store_true',
                        dest='wipe_flash',
                        help='Wipe all secondary cores and ROM data')
    parser.add_argument('-e',
                        '--32',
                        required=False,
                        action='store_true',
                        dest='expand_flash',
                        help='Expand, if needed, flash file to 32MiB')
    parser.add_argument('-t',
                        '--convert',
                        required=False,
                        action='store_true',
                        dest='convert_core',
                        help='Convert between Spectrum and standard core')
    parser.add_argument('-1',
                        '--1core',
                        required=False,
                        action='store_true',
                        dest='use_1core',
                        help='Use, if available, ZXUnCore cores for ZX-Uno')
    parser.add_argument('-2',
                        '--2mb',
                        required=False,
                        action='store_true',
                        dest='use_2mb',
                        help='Use, if available, 2MB cores for ZX-Uno')
    parser.add_argument('-u',
                        '--update',
                        required=False,
                        nargs='?',
                        choices=[
                            'all', 'bios', 'spectrum', 'special', 'cores',
                            'arcade', 'varcade', 'json', 'roms'
                        ],
                        const='all',
                        default='',
                        dest='update',
                        help='Update JSON or BIOS and/or Cores')
    parser.add_argument('-q',
                        '--check',
                        required=False,
                        action='store_true',
                        dest='check_updated',
                        help='Check if cores are up to date')
    parser.add_argument('-c',
                        '--default_core',
                        type=int,
                        required=False,
                        action='store',
                        dest='default_core',
                        help='Default core number: 1 and up')
    parser.add_argument('-z',
                        '--default_rom',
                        required=False,
                        type=int,
                        action='store',
                        dest='default_rom',
                        help='Default Spectrum ROM index: 0 and up')
    parser.add_argument('-m',
                        '--video_mode',
                        required=False,
                        type=int,
                        action='store',
                        dest='video_mode',
                        help='Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)')
    parser.add_argument(
        '-k',
        '--keyboard_layout',
        required=False,
        type=int,
        action='store',
        dest='keyboard_layout',
        help='Keyboard Layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)')
    parser.add_argument('-b',
                        '--boot_timer',
                        required=False,
                        type=int,
                        action='store',
                        dest='boot_timer',
                        help='Boot Timer: 0 (No Timer), 1, 2, 3 or 4')
    parser.add_argument('-N',
                        '--nocolours',
                        required=False,
                        action='store_true',
                        dest='nocol',
                        help='Do not use terminal colours')
    parser.add_argument('--debug', action='store_true', dest='debug')

    arguments = parser.parse_args()

    if arguments.nocol:
        IS_COL_TERM = False

    if arguments.debug:
        printcol(Colours.PURPLE, 'Debugging Enabled!!', end='\n')
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug(sys.argv)

    if arguments.input_file:
        values['input_file'] = os.path.abspath(arguments.input_file)

    if arguments.output_dir:
        values['output_dir'] = os.path.abspath(arguments.output_dir)

    if arguments.output_file:
        values['output_file'] = os.path.abspath(arguments.output_file)

    if arguments.force:
        values['force'] = arguments.force

    if arguments.list_contents:
        values['list'] = arguments.list_contents

    if arguments.detail:
        values['detail'] = arguments.detail

    if arguments.stats:
        values['stats'] = arguments.stats

    if arguments.parse_roms:
        values['roms'] = arguments.parse_roms

    if arguments.show_hashes:
        values['show_hashes'] = arguments.show_hashes

    if arguments.extract:
        values['extract'] = arguments.extract.split(',')

    if arguments.n_cores:
        values['n_cores'] = arguments.n_cores

    if arguments.inject:
        values['inject'] = arguments.inject

    if arguments.wipe_flash:
        values['wipe_flash'] = arguments.wipe_flash

    if arguments.expand_flash:
        values['expand_flash'] = arguments.expand_flash

    if arguments.convert_core:
        values['convert_core'] = arguments.convert_core

    if arguments.use_1core:
        values['1core'] = arguments.use_1core

    if arguments.use_2mb:
        values['2mb'] = arguments.use_2mb

    if arguments.update:
        values['update'] = arguments.update

    if arguments.check_updated:
        values['check_updated'] = arguments.check_updated

    if arguments.default_core:
        values['default_core'] = arguments.default_core - 1

    if arguments.default_rom is not None:
        values['default_rom'] = arguments.default_rom

    if arguments.video_mode is not None:
        values['video_mode'] = arguments.video_mode

    if arguments.keyboard_layout is not None:
        values['keyboard_layout'] = arguments.keyboard_layout

    if arguments.boot_timer is not None:
        values['boot_timer'] = arguments.boot_timer

    return values


# Main Functions


def load_json_bd(str_file='', output_file='', str_update='', base_dir=None):
    """
    Loads the Hash Database
    :param str_file: Input file (to determine if update)
    :param output_file: Output file (to determine if update)
    :param str_update: Update parameter from options
    :return: Dictionary with Hashes from database
    """

    str_json = os.path.join(MY_DIRPATH, 'zx123_hash.json')
    if base_dir:
        str_json = os.path.join(base_dir, 'zx123_hash.json')

    fulldict_hash = {}
    # Update JSON
    if str_update != '':
        if str_update == 'json' or (not str_file and not STR_OUTDIR
                                    and not output_file):
            if os.path.isfile(str_json):
                os.remove(str_json)

    if not os.path.isfile(str_json):
        dl_url = MAIN_URL + '/zx123_hash.json'
        print('\nDownloading JSON database...', end='')
        urllib.request.urlretrieve(dl_url, str_json)
        print('OK')
        #sys.exit(0)

    if not os.path.isfile(str_json):
        LOGGER.error('Hash database not found: %s', str_json)
        #sys.exit(2)
    with open(str_json, 'r', encoding='utf-8') as json_handle:
        LOGGER.debug('Loading dictionary with hashes...')
        fulldict_hash = json.load(json_handle)

    return fulldict_hash


def unzip_image(str_path, str_output, hash_dict, b_force):
    """
    Extract base image file from ZIP. Download ZIP from repository if needed.
    :param str_path: Directory where ZIP files are
    :param str_output: Path to image file to create
    :param hash_dict: Full dictionary of hashes
    :param b_force: Force overwriting file
    :return: New image file path if created or else an empty string
    """
    str_file = ''
    str_err = ''
    str_extension = os.path.splitext(str_output)[1]
    str_extension = str_extension[1:].upper()

    if str_extension in hash_dict:
        str_image = f'FLASH16_empty.{str_extension}'
        str_zip = f'{str_image}.zip'
        str_zipfile = os.path.join(str_path, str_zip)
        if not os.path.isfile(str_zipfile):
            dl_url = f'{MAIN_URL}/{str_zip}'
            print('\nDownloading base image ZIP file...', end='')
            urllib.request.urlretrieve(dl_url, str_zipfile)
            print('OK')

        if is_zipfile(str_zipfile):
            with ZipFile(str_zipfile, 'r') as zip_obj:
                arr_files = zip_obj.namelist()
                for str_name in arr_files:
                    if str_name == str_image:
                        with tempfile.TemporaryDirectory() as str_tmpdir:
                            print('\nExtracting image...', end='')
                            zip_obj.extract(str_name, str_tmpdir)
                            print('OK')
                            str_file = os.path.join(str_tmpdir, str_name)
                            if b_force or check_overwrite(str_output):
                                try:
                                    shutil.move(str_file, str_output)
                                    str_file = str_output
                                except FileNotFoundError:
                                    str_file = ''
                            else:
                                str_file = ''
            if not str_file:
                str_err = 'Image file not extracted. Bad destination path?'
        else:
            str_err = 'Could not get base image file'
    else:
        str_err = f'Unknown extension: {str_extension}'

    if str_err:
        LOGGER.error(str_err)
    return str_file, str_err


def detect_file(str_file, fulldict_hash):
    """
    Analyzes a file and tries to determine it's kind (Flash Image, etc.)
    :param str_file: Input file to analyze
    :param fulldict_hash: Dictionary with hash database
    :return: Normalized extension, subDictionary of hashes and filetype
    """

    str_extension = os.path.splitext(str_file)[1]
    str_extension = str_extension[1:].upper()

    # Check that file extension is available in Hash Database
    dict_hash = {}
    if str_extension in fulldict_hash:
        dict_hash = fulldict_hash[str_extension]
    else:
        for str_kind in fulldict_hash:
            if "extensions" in fulldict_hash[str_kind]:
                for str_tmp in fulldict_hash[str_kind]['extensions']:
                    if str_tmp == str_extension:
                        str_extension = str_kind
                        dict_hash = fulldict_hash[str_extension]
                        break

    filetype = 'Unknown'
    if not dict_hash:
        LOGGER.error('Unknown file extension: %s', str_extension)
        #sys.exit(4)
    else:
        # Is the file header known?
        if validate_file(str_file, dict_hash['parts']['header'][3]):
            filetype = 'FlashImage'
        else:
            # Check if it's ROMPack v2
            rpk_header = fulldict_hash['RPv2']['parts']['header']
            try:
                f_size = os.stat(str_file).st_size
            except FileNotFoundError:
                f_size = -1
            if validate_file(str_file, rpk_header[3]) and int(
                    rpk_header[1]) == f_size:
                if str_extension == 'ZX1':
                    filetype = 'ROMPack v2'

    return str_extension, dict_hash, filetype


def print_stats(fulldict_hash, b_detail=False):
    """Show Stats"""

    print('')
    printcol(Colours.CYAN, 'JSON Database Stats', end='\n')
    if 'version' in fulldict_hash:
        print(f'Version: {fulldict_hash["version"]}')
    print('')

    total = 0
    total_cores = 0
    total_hashes = 0
    total_hashes_cores = 0
    for str_kind in fulldict_hash:
        if str_kind != 'version':
            printcol(Colours.BLUE,
                     fulldict_hash[str_kind]['description'],
                     end='\n')

            subtotal = 0
            subtotal_hashes = 0
            for chld in fulldict_hash[str_kind]:
                if isinstance(fulldict_hash[str_kind][chld], dict):
                    count, part = count_hashes(fulldict_hash[str_kind][chld])
                    if count:
                        if b_detail:
                            print('')
                            for str_name, h_count in part.items():
                                printcol(Colours.BLUE,
                                         f'{str_name} ({h_count}')
                                printcol(Colours.BLUE, ' hash')
                                if h_count > 1:
                                    printcol(Colours.BLUE, 'es')
                                printcol(Colours.BLUE, ')', end='\n')
                                dict_det = fulldict_hash[str_kind][chld][
                                    str_name]
                                feat_det = dict_det.get('features', {})
                                print_detail(str_name, feat_det)
                        print(f'{chld}: {len(part):>4} ({count:03} hashes)')
                        subtotal += len(part)
                        subtotal_hashes += count

            total += subtotal
            total_cores += subtotal
            total_hashes += subtotal_hashes
            total_hashes_cores += subtotal_hashes

            count, part = count_hashes(fulldict_hash[str_kind])
            if count:
                print(f'Other: {len(part):>4} ({count:03} hashes)')
                total += len(part)
                subtotal += len(part)
                subtotal_hashes += count
                total_hashes += count

            if subtotal:
                print(f'Total: {subtotal:>4} ({subtotal_hashes:03} hashes)')
                print('')

    print('')
    print(f'Total Cores: {total_cores:>4} ({total_hashes_cores:03} hashes)')
    print(f'      Total: {total:>4} ({total_hashes:03} hashes)')
    print('')


def print_detail(str_name, dict_det):
    """Print detailed info"""

    if dict_det:
        for str_feature in dict_det:
            arr_feat, str_note = dict_det[str_feature]
            if arr_feat[0]:
                printcol(Colours.BLUE, f'   {str_feature}: ', end='')
                print(f'{", ".join(arr_feat)}', end='')
                if str_note:
                    print(f' ({str_note})', end='')
                print('')
        print('')
    else:
        printcol(Colours.RED,
                 f' No details available for {str_name}',
                 end='\n')


def count_hashes(subdict_hash):
    """Used by print_stats to count elements and hashes"""

    i_cnt = 0
    dict_cnt = {}
    for chld in subdict_hash:
        if 'versions' in subdict_hash[chld]:
            i_hashes = len(subdict_hash[chld]['versions'])
            i_cnt += i_hashes
            dict_cnt[chld] = i_hashes

    return i_cnt, dict_cnt


def list_zxdata(str_in_file,
                hash_dict,
                show_hashes,
                check_updated=False,
                get_1core=False,
                get_2mb=False,
                b_detail=False):
    """
    List contents of file
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param show_hashes: If True, print also block hashes
    :param check_updated: If True, check with 'latest', '1core' or '2m'
    """
    LOGGER.debug('Listing contents of file: %s', str_in_file)
    str_name = os.path.basename(str_in_file)
    str_description = hash_dict['description']

    dict_res = {}
    dict_res['description'] = str_description
    print(f'\nContents of {str_name} (possibly {str_description})\n')

    dict_blocks = {}
    block_list = ['BIOS', 'esxdos', 'Spectrum', 'Special']
    for block_name in block_list:
        if block_name in hash_dict['parts']:
            arr_block = get_version(str_in_file,
                                    hash_dict['parts'][block_name],
                                    hash_dict[block_name])
            block_version, block_hash = arr_block
            if block_version:
                dict_blocks[block_name] = arr_block
                print(f'{block_name}: {block_version}', end='')
                if check_updated:
                    update_check(hash_dict[block_name], block_version,
                                 get_1core, get_2mb)
                print('')
                if show_hashes:
                    print(f'Hash: {block_hash}')

    dict_cores = {}
    core_list = get_core_list(str_in_file, hash_dict['parts'])
    for index, name in enumerate(core_list):
        arr_core = get_core_version(str_in_file, index, hash_dict['parts'],
                                    hash_dict['Cores'])
        block_name, block_version, block_hash, dict_det = arr_core

        dict_cores[index + 2] = [name] + list(arr_core)
        print(
            f'Core {index + 2:02d} "{name}" -> {block_name}: {block_version}',
            end='')
        if check_updated:
            if block_name in hash_dict['Cores']:
                update_check(hash_dict['Cores'][block_name], block_version,
                             get_1core, get_2mb)
        print('')
        if b_detail:
            printcol(Colours.BLUE,
                     f' Features of "{block_name}" Cores:',
                     end='\n')
            print_detail(block_name, dict_det)
        if show_hashes:
            print(f'Core {index + 2:02d}: {block_hash}')

    dict_defaults = {}
    print('\nBIOS Defaults:')

    default_rom = get_peek(str_in_file, 28736)
    print(f'\tDefault ROM -> {default_rom:02}')
    dict_defaults['default_rom'] = default_rom

    default_core = get_peek(str_in_file, 28737) + 1
    print(f'\tDefault Core -> {default_core:02}')
    dict_defaults['default_core'] = default_core

    boot_timer = get_peek(str_in_file, 28738)
    print(f'\tBoot Timer -> {boot_timer}')
    dict_defaults['boot_timer'] = boot_timer

    keyb_layout = get_peek(str_in_file, 28746)
    print(f'\tKeyboard Layout -> {keyb_layout}')
    dict_defaults['keyb_layout'] = keyb_layout

    video_mode = get_peek(str_in_file, 28749)
    print(f'\tVideo Mode -> {video_mode}')
    dict_defaults['video_mode'] = video_mode

    dict_res['blocks'] = dict_blocks
    dict_res['cores'] = dict_cores
    dict_res['defaults'] = dict_defaults
    return dict_res


def update_check(hash_dict, block_version, get_1core=False, get_2mb=False):
    """
    Check block version against latest entry and print the result
    :param hash_dict: Dictionary for entry (e.g. Spectrum Core)
    :param block_version: Version string to check
    """
    last_version = hash_dict.get('latest', [''])[0]
    if (get_2mb or get_1core) and '2m' in hash_dict:
        last_version = hash_dict['2m'][0]
    if get_1core and '1core' in hash_dict:
        last_version = hash_dict['1core'][0]

    if last_version:
        if block_version == last_version:
            printcol(Colours.GREEN, '  >> Up to date', end='')
        else:
            printcol(Colours.YELLOW,
                     f'  >> Outdated!. Latest version: {last_version}',
                     end='')
    else:
        LOGGER.debug('Latest entry not found in JSON')


def list_romsdata(str_in_file,
                  hash_dict,
                  in_file_ext,
                  show_hashes,
                  roms_file=False):
    """
    List ZX Spectrum ROMs of file
    :param str_in_file: Path to file
    :param hash_dict: Dictionary
    :param in_file_ext: File key in dictionary (e.g. ZXD)
    :param show_hashes: If True, print also block hashes
    :param roms_file: If True, add extra offset as in ROMS.ZX1 file
    :return: True if there are ROMs to list
    """
    LOGGER.debug('Listing ROMs of file: %s', str_in_file)
    roms_list = get_rom_list(str_in_file, hash_dict[in_file_ext]['parts'])

    dict_res = {}
    if roms_list:
        if roms_file:
            if in_file_ext == 'RPv2':
                print('ZX ROMPack file (v2)')
            else:
                print('ZX1 ROMPack File')
            def_addr = int(hash_dict[in_file_ext]['parts']['roms_data'][0])
            default_rom = get_peek(str_in_file, def_addr)
            print(f'\tDefault ROM -> {default_rom:02}')

        print('\nZX Spectrum ROMs:')
        for rom in roms_list:
            rom_name = rom[2]
            block_version, block_hash, _ = get_rom(str_in_file, rom[1], rom[3],
                                                   hash_dict, in_file_ext,
                                                   roms_file)
            dict_res[rom[0]] = [
                rom[1], rom[4], rom[5], rom_name, rom[3] * 16, block_version,
                block_hash
            ]
            str_rominfo = f' {rom[0]:02d} (Slot {rom[1]:02d}) {rom[4]:>10} ({rom[5]:>16}) '
            str_rominfo += f'"{rom_name}" {rom[3] * 16}K -> {block_version}'
            print(str_rominfo)

            if show_hashes:
                print(f'Hash: {block_hash}')

    return dict_res


def extractfrom_zxdata(str_in_file,
                       extract_item,
                       fullhash_dict,
                       str_dir,
                       str_extension,
                       b_force=False,
                       cores=True):
    """
    Parse and extract data block to file
    :param str_in_file: Path to file
    :param extract_item: Block ID string  or Core Number
    :param fullhash_dict: Dictionary with hashes for different blocks
    :str_dir: Destination dir
    :param str_extension: Extension for Core files
    :param b_force: Force overwriting file
    :param cores: If True, export Core, if False, export ROM
    """
    hash_dict = fullhash_dict[str_extension]

    b_romfile = False
    if str_extension == 'RPv2':
        b_romfile = True

    block_list = ['BIOS', 'esxdos', 'Spectrum', 'Special']
    for block_name in block_list:
        if block_name in hash_dict['parts']:
            # Extract main ROMs
            if extract_item.upper() == block_name.upper():
                block_version, _ = get_version(str_in_file,
                                               hash_dict['parts'][block_name],
                                               hash_dict[block_name])
                print(f'Extracting {block_name}...')
                block_info = hash_dict['parts'][block_name]
                str_bin = f'{block_name}_{block_version}.{str_extension}'
                str_bin = os.path.join(str_dir, str_bin)
                block_magic = block_info[3]
                validate_and_export_bin(str_in_file, block_info, str_bin,
                                        b_force, block_magic)
                break

    if cores:
        # Extract Cores
        if extract_item.isdigit():
            core_number = int(extract_item)
            core_list = get_core_list(str_in_file, hash_dict['parts'])
            if core_number > 1 and core_number < (len(core_list) + 2):
                print(f'Extracting Core {core_number}...')
                core_number -= 2
                core_name = core_list[core_number].strip()
                block_name, block_version, _, _ = get_core_version(
                    str_in_file, core_number, hash_dict['parts'],
                    hash_dict['Cores'])
                if block_name == 'Unknown':
                    block_name = core_name
                splitcore_index = int(hash_dict['parts']['cores_dir'][4])
                core_bases = hash_dict['parts']['core_base']
                block_data = get_core_blockdata(core_number, splitcore_index,
                                                core_bases)
                str_bin = f'CORE{core_number + 2:02d}'
                str_bin += f'_{block_name.replace(" ", "_")}_v{block_version}'
                str_bin += f'.{str_extension}'
                str_bin = os.path.join(str_dir, str_bin)
                core_magic = core_bases[3]
                validate_and_export_bin(str_in_file, block_data, str_bin,
                                        b_force, core_magic)
            else:
                LOGGER.error('Invalid core number: %i', core_number)
    else:
        # Extract individual ZX Spectrum ROMs
        if extract_item.isdigit():
            rom_number = int(extract_item)
            rom_list = get_rom_list(str_in_file, hash_dict['parts'])
            if rom_number > -1 and rom_number < len(rom_list):
                print(f'Extracting ZX Spectrum ROM {rom_number}...')
                for rom in rom_list:
                    if rom[0] == rom_number:
                        rom_version, _, rom_data = get_rom(
                            str_in_file, rom[1], rom[3], fullhash_dict,
                            str_extension, b_romfile)
                        rom_name = rom[2].strip()
                        if rom_version != 'Unknown':
                            rom_name = rom_version.strip()
                        str_bin = f'{rom[0]:02d}_{rom_name}.rom'
                        str_bin = os.path.join(str_dir, str_bin)
                        export_bindata(rom_data, str_bin, b_force)
                        break
            else:
                LOGGER.error('Invalid ROM index: %i', rom_number)

    if extract_item.upper() == 'ROMS':
        # Extract all ZX Spectrum ROMs to ROMPack v1 file
        default_rom = get_peek(str_in_file, 28736).to_bytes(1, 'little')
        rom_dict_parts = fullhash_dict['ROMS']['parts']
        blk_info = rom_dict_parts['roms_dir']
        blk_bases = rom_dict_parts['roms_data']
        roms_data = 0x1000 * b'\x00' + 0x40 * b'\xff' + default_rom
        roms_data += 0x100000 * b'\x00'
        roms_list = get_rom_list(str_in_file, hash_dict['parts'])
        for rom_item in roms_list:
            rom_index = rom_item[0]
            rom_slt = rom_item[1]
            rom_name = rom_item[2]
            rom_params = rom_item[4]
            rom_crc = rom_item[5]

            rom_version, _, rom_data = get_rom(str_in_file, rom_slt,
                                               rom_item[3], fullhash_dict,
                                               str_extension)

            roms_data, _ = inject_rom_tobin(roms_data, blk_info, blk_bases,
                                            rom_index, rom_slt, rom_name,
                                            rom_params, rom_data, rom_crc,
                                            True)

        str_bin = 'ROMS.ZX1'
        str_bin = os.path.join(str_dir, str_bin)
        export_bindata(roms_data, str_bin, b_force)


def prep_update_zxdata(arr_in_files,
                       str_spi_file,
                       fullhash_dict,
                       str_extension,
                       block_list,
                       b_varcade='',
                       get_1core=False,
                       get_2mb=False):
    """
    Try to prepare to update several BIOS
    :param str_spi_file: Input SPI flash file
    :param hash_dict: Dictionary with hashes for different blocks
    :return: A valid array for inject_zxfiles
    """

    hash_dict = fullhash_dict[str_extension]

    if not block_list:
        block_list = ['BIOS', 'esxdos', 'Spectrum', 'Special']

    for block in block_list:
        if block in hash_dict['parts']:
            block_version, block_hash = get_version(str_spi_file,
                                                    hash_dict['parts'][block],
                                                    hash_dict[block])
            if block_version:
                hash_versions = hash_dict[block]
                if 'versions' in hash_versions:
                    hash_versions = hash_versions['versions']

                latest = hash_dict[block]['latest']
                if (get_2mb or get_1core) and '2m' in hash_dict[block]:
                    latest = hash_dict[block]['2m']
                if get_1core and '1core' in hash_dict[block]:
                    latest = hash_dict[block]['1core']

                if block == 'BIOS' and b_varcade:
                    latest = hash_dict[block]['vertical']
                latest_hash = hash_versions[latest[0]]

                str_file = f'{block}_{latest[0]}.{str_extension}'
                str_file = os.path.join(STR_OUTDIR, str_file)

                if block_hash != latest_hash:
                    b_append = check_and_update(str_file, latest_hash,
                                                latest[1:], block)

                    if b_append:
                        arr_in_files.append(f'{block},{str_file}')


def prep_update_cores(arr_in_files,
                      str_spi_file,
                      fullhash_dict,
                      str_extension,
                      b_new=False,
                      arcade_type='None',
                      get_1core=False,
                      get_2mb=False):
    """
    Try to prepare to update cores
    :param arr_in_files: Array for inject_zxfiles, updated if needed
    :param str_spi_file: Input SPI flash file
    :param hash_dict: Dictionary with hashes for different blocks
    :b_new: Is this a new Flash Image?
    :b_arcade: When new, only include arcades, else do not include any arcade
    """

    hash_dict = fullhash_dict[str_extension]

    core_list = []
    tmp_list = get_core_list(str_spi_file, hash_dict['parts'])
    if tmp_list:
        for index, name in enumerate(tmp_list):
            core_list.append([index, name.strip()] + list(
                get_core_version(str_spi_file, index, hash_dict['parts'],
                                 hash_dict['Cores']))[:-1])

    if b_new:
        for index, block_name in enumerate(hash_dict['Cores']):
            append = False
            if arcade_type == 'arcade' and ("Arcade " in block_name):
                append = True
            elif arcade_type == 'varcade' and ("ArcadeV " in block_name):
                append = True
            elif arcade_type == 'None':
                if ("Arcade " not in block_name) and ("ArcadeV "
                                                      not in block_name):
                    append = True
            if append:
                core_list.append(
                    [index, block_name, block_name, '0', 'Para Sara'])

    for index, name, block_name, _, block_hash in core_list:
        index += 2
        if block_name in hash_dict['Cores']:
            latest = hash_dict['Cores'][block_name].get('latest', [''])
            if (get_2mb
                    or get_1core) and '2m' in hash_dict['Cores'][block_name]:
                latest = hash_dict['Cores'][block_name]['2m']
            if get_1core and '1core' in hash_dict['Cores'][block_name]:
                latest = hash_dict['Cores'][block_name]['1core']

            latest_hash = hash_dict['Cores'][block_name]['versions'].get(
                latest[0], '')

            base = hash_dict['Cores'][block_name].get('base', [''])
            base_hash = hash_dict['Cores'][block_name]['versions'].get(
                base[0], '')

            str_file = f'CORE{index:0>2}_{block_name}_{latest[0]}.{str_extension}'
            str_file = os.path.join(STR_OUTDIR, str_file)

            if block_hash != latest_hash:
                b_append = check_and_update(str_file, latest_hash, latest[1:],
                                            block_name, block_hash, base_hash,
                                            base[1:])

                if b_append:
                    new_in_file = f'CORE,{index},{name},{str_file}'
                    arr_in_files.append(new_in_file)


def prep_update_roms(arr_in_files,
                     fullhash_dict,
                     str_extension,
                     b_new=False,
                     b_arcade=False):
    """
    Try to prepare to update ROMs
    :param arr_in_files: Array for inject_zxfiles, updated if needed
    :param fullhash_dict: Dictionary with hashes data
    :b_new: Is this a new Flash Image?
    """

    if 'ROMS' in fullhash_dict and b_new:
        hash_versions = fullhash_dict['ROMS']
        if 'versions' in hash_versions:
            hash_versions = hash_versions['versions']

        latest = fullhash_dict['ROMS']['latest']
        latest_hash = hash_versions[latest[0]]

        str_roms = os.path.join(STR_OUTDIR, 'ROMS.ZX1')
        b_append = check_and_update(str_roms, latest_hash, latest[1:], 'ROMS')

        if b_append:
            new_in_file = f'ROMS,{str_roms}'
            arr_in_files.append(new_in_file)

        if b_arcade:
            b_append = False
            jamma = fullhash_dict['ROM']['16K Spectrum ROM']['arcade']
            j_hash = fullhash_dict['ROM']['16K Spectrum ROM'][jamma[0]]

            str_rom = os.path.join(STR_OUTDIR, 'Jamma.rom')
            b_append = check_and_update(str_rom, j_hash, jamma[1:], 'Jamma')
            if b_append:
                roms_info = fullhash_dict[str_extension]['parts']['roms_dir']
                i_slot = roms_info[5] + roms_info[6] - 1
                new_in_file = f'ROM,{i_slot},hl17x,Jamma,{str_rom}'
                arr_in_files.append(new_in_file)


def check_and_update(update_file,
                     upd_hash,
                     upd_urls,
                     upd_name,
                     uchk='',
                     bs_hash='',
                     bs_urls=None):
    """
    Checks if a file with the desired hashexists. If not, download from the URL
    :param update_file: Path to the file
    :param upd_hash: Hash to check
    :param upd_urls: array of URLs to download if not found or wrong hash
    :param upd_name: Text to show while downloading
    :param uchk: Control text to download older versions
    :param bs_hash: Base hash (fallbak if there's not latest)
    :param bs_urls: Base download URIs
    :returns: True if a new file was needed, found and downloaded
    """

    if not bs_urls:
        bs_urls = []
    update_url = ''
    file_hash = ''
    update_extension = os.path.splitext(update_file)[1].upper()
    dl_result = False
    if os.path.isfile(update_file):
        file_hash = get_file_hash(update_file)
        if file_hash == upd_hash:
            LOGGER.debug('Not downloading, already available: %s', update_file)
            dl_result = True

    if upd_urls:
        update_url = upd_urls[0]

    if not update_url and bs_urls and uchk == 'Para Sara':
        if file_hash == bs_hash:
            LOGGER.debug('Not downloading base, available: %s', update_file)
            dl_result = True
        update_url = bs_urls[0]

    if not dl_result and update_url:
        print(f'Downloading {upd_name}...', end='')
        try:
            LOGGER.debug(update_url)
            urllib.request.urlretrieve(update_url, update_file)
            if is_zipfile(update_file):
                print('Extracting...', end='')
                b_found = False
                str_zipfile = update_file + '.zip'
                os.rename(update_file, str_zipfile)
                with ZipFile(str_zipfile, 'r') as zip_obj:
                    arr_files = zip_obj.namelist()
                    b_found = False
                    for str_name in arr_files:
                        str_extension = os.path.splitext(str_name)[1].upper()
                        if update_extension == str_extension:
                            with tempfile.TemporaryDirectory() as str_tmpdir:
                                zip_obj.extract(str_name, str_tmpdir)
                                str_file = os.path.join(str_tmpdir, str_name)
                                shutil.move(str_file, update_file)
                            b_found = True
                            break
                if not b_found:
                    LOGGER.warning('Not a valid ZIP file')
                os.remove(str_zipfile)
            print('OK')
            dl_result = True
        except urllib.error.HTTPError:
            print('Error! Is the JSON file up to date?')

    return dl_result


def expand_image(str_spi_file, str_outfile, flash_len, b_force=False):
    """
    Expands, if needed, an image file
    :param str_spi_file: Input SPI flash file
    :param str_outfile: New SPI flash file to create
    :param flash_len: Desired size, in bytes
    :param b_force: Force overwriting file
    """

    b_len = os.stat(str_spi_file).st_size
    if b_len < flash_len:
        extra_len = flash_len - b_len
        print('Expanding image file...')
        if b_force or check_overwrite(str_outfile):
            with open(str_spi_file, "rb") as in_zxdata:
                b_data = in_zxdata.read(b_len)

            # Extra 0s
            b_data += b'\x00' * extra_len

            with open(str_outfile, "wb") as out_zxdata:
                out_zxdata.write(b_data)
                print(f'{str_outfile} created OK.')
                b_force = True

    return b_force


def wipe_zxdata(str_spi_file,
                str_outfile,
                hash_dict,
                vid_mode=-1,
                keyb_layout=-1,
                boot_timer=-1,
                b_force=False):
    """
    Wipe all cores and ROMs
    :param str_spi_file: Input SPI flash file
    :param arr_in_files: Array with parameters and files to inject
    :param str_outfile: New SPI flash file to create
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param vid_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyb_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :param boot_timer: 0 (No timer), 1, 2 (2x), 3 (4x), 4 (8x)
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :param b_force: Force overwriting file
    """

    dict_parts = hash_dict['parts']

    LOGGER.debug('Reading Flash...')
    b_len = os.stat(str_spi_file).st_size
    with open(str_spi_file, "rb") as in_zxdata:
        b_data = in_zxdata.read(b_len)

    # SPI flash ROMs
    block_info = dict_parts['roms_dir']
    base_slots = int(block_info[5])
    max_slots = base_slots + int(block_info[6])
    rom_bases = dict_parts['roms_data']

    # SPI flash Cores
    blk_info = dict_parts['cores_dir']
    max_cores = splitcore_index = int(blk_info[4])
    if len(blk_info) > 5:
        max_cores += int(blk_info[5])
    core_bases = dict_parts['core_base']

    # Clear ROM names in directory
    cur_pos = int(block_info[0])
    br_data = b_data[:cur_pos]
    br_data += b'\x00' * 64 * max_slots
    cur_pos += 64 * max_slots

    # Clear ROMs list in SPI flash (Temp Binary Data)
    br_data += b_data[cur_pos:int(block_info[4])]
    cur_pos = int(block_info[4])
    br_data += b'\xff' * max_slots
    cur_pos += max_slots

    # Clear Core Names in directory
    br_data += b_data[cur_pos:int(blk_info[0]) + 0x100]
    cur_pos = int(blk_info[0]) + 0x100
    br_data += b'\x00' * 32 * max_cores
    cur_pos += 32 * max_cores

    # Clear data blocks of ROMs
    br_data += b_data[cur_pos:int(rom_bases[0])]
    cur_pos = int(rom_bases[0])
    br_data += b'\x00' * 16384 * base_slots
    cur_pos += 16384 * base_slots

    # Clear remaining data blocks (from Core 2)
    core_end = get_core_blockdata(0, splitcore_index, core_bases)[0]
    br_data += b_data[cur_pos:core_end]
    br_data += b'\x00' * (len(b_data) - core_end)

    br_data, _, _ = inject_biossettings(br_data, vid_mode, keyb_layout,
                                        boot_timer, 0, 0)

    # Write Data
    if b_force or check_overwrite(str_outfile):
        with open(str_outfile, "wb") as out_zxdata:
            out_zxdata.write(br_data)
            print(f'{str_outfile} created OK.')


def inject_zxfiles(str_spi_file,
                   arr_in_files,
                   str_outfile,
                   fullhash_dict,
                   str_extension,
                   video_mode=-1,
                   keyboard_layout=-1,
                   boot_timer=-1,
                   default_core=-1,
                   default_rom=-1,
                   b_force=False):
    """
    Add binary from one or more binary files to SPI flash or ROMPackV2 file
    :param str_spi_file: Input SPI flash or ROMPack v2 file
    :param arr_in_files: Array with parameters and files to inject
    :param str_outfile: New SPI flash file to create
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension (or RPv2 for ROMPack v2)
    :param video_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyboard_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :param boot_timer: 0 (No timer), 1, 2 (2x), 3 (4x), 4 (8x)
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :param b_force: Force overwriting file
    :return: Updated b_force and string array with errors (if any)
    """
    arr_err = []
    b_changed = False
    hash_dict = fullhash_dict[str_extension]

    def_rom_addr = 28736
    if str_extension == 'RPv2':
        def_rom_addr = int(hash_dict['parts']['roms_data'][0])

    LOGGER.debug('Reading Destination File...')
    b_len = os.stat(str_spi_file).st_size
    with open(str_spi_file, "rb") as in_zxdata:
        b_data = in_zxdata.read(b_len)

    for str_in_params in arr_in_files:
        # Inject main ROMs
        b_data, b_chg, str_err = inject_bindata(str_in_params, hash_dict,
                                                b_data)
        b_changed |= b_chg
        if str_err:
            arr_err.append(str_err)
        # Inject Cores
        b_data, b_chg, str_err = inject_coredata(str_in_params, hash_dict,
                                                 b_data)
        b_changed |= b_chg
        if str_err:
            arr_err.append(str_err)
        # Inject ZX Spectrum ROMs from individual files
        b_data, b_chg, str_err = inject_romdata(str_spi_file, str_in_params,
                                                fullhash_dict, str_extension,
                                                b_data)
        b_changed |= b_chg
        if str_err:
            arr_err.append(str_err)
        # Inject ZX Spectrum ROMs from ROMPack
        b_data, b_chg, str_err = inject_romszx1data(str_in_params,
                                                    fullhash_dict,
                                                    str_extension, b_data)
        b_changed |= b_chg
        if str_err:
            arr_err.append(str_err)

    # Modify BIOS settings
    b_data, b_chg, arr_bios_err = inject_biossettings(b_data,
                                                      video_mode,
                                                      keyboard_layout,
                                                      boot_timer,
                                                      default_core,
                                                      default_rom,
                                                      d_rom_addr=def_rom_addr)
    b_changed |= b_chg
    if arr_bios_err:
        arr_err += arr_bios_err

    if b_changed:
        if b_force or check_overwrite(str_outfile):
            b_force = True
            with open(str_outfile, "wb") as out_zxdata:
                out_zxdata.write(b_data)
                print(f'{str_outfile} created OK.')

    return b_force, arr_err


def savefrom_zxdata(str_in_file,
                    hash_dict,
                    str_outfile,
                    n_cores=-1,
                    video_mode=-1,
                    keyboard_layout=-1,
                    boot_timer=-1,
                    default_core=-1,
                    default_rom=-1,
                    b_force=False):
    """
    Create truncated SPI flash file
    :param str_in_file: Path to SPI file
    :param hash_dict: Dictionary with hashes for different blocks
    :param str_outfile: Path to SPI output file to save
    :param n_cores: Number of cores to keep
    :param video_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyboard_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :param boot_timer: 0 (No timer), 1, 2 (2x), 3 (4x), 4 (8x)
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :param b_force: Force overwriting file
    """

    dict_parts = hash_dict['parts']
    block_info = dict_parts['cores_dir']
    max_cores = int(block_info[4])

    flash_len = bin_len = os.stat(str_in_file).st_size
    if n_cores > -1:
        flash_len = int(hash_dict['parts']['core_base'][0])
        flash_len += int(hash_dict['parts']['core_base'][1]) * n_cores

    if bin_len > flash_len:
        bin_len = flash_len

    print('Copying Flash...')
    with open(str_in_file, "rb") as in_zxdata:
        bin_data = in_zxdata.read(bin_len)

    bin_data, _, _ = inject_biossettings(bin_data, video_mode, keyboard_layout,
                                         boot_timer, default_core, default_rom)

    if n_cores > -1:
        core_offset = 0x7100 + (n_cores * 0x20)
        core_len = (max_cores - n_cores) * 0x20
        bin_data = bin_data[:core_offset] + b'\x00' * core_len + bin_data[
            core_offset + core_len:]

    if b_force or check_overwrite(str_outfile):
        with open(str_outfile, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print(f'{str_outfile} created OK.')


def convert_core(str_in_file, hash_dict, str_outfile, b_force=False):
    """
    Convert between Spectrum core and Standard core
    :param str_in_file: Path to core file to convert from
    :param hash_dict: Dictionary with hashes for different blocks
    :param str_outfile: Path output file to save
    :param b_force: Force overwriting file
    """
    dict_parts = hash_dict['parts']

    # Standard core specs
    core_bases = dict_parts['core_base']
    b_corelen = int(core_bases[1])
    b_corehead = core_bases[3]

    # Spectrum core specs
    spectrum_bases = dict_parts['Spectrum']
    b_speclen = int(spectrum_bases[1])
    b_spechead = spectrum_bases[3]

    b_len = os.stat(str_in_file).st_size
    with open(str_in_file, "rb") as in_zxdata:
        b_data = in_zxdata.read(b_len)

    # Check header and length and convert data if needed
    b_convert = True
    if validate_bin(b_data, b_corehead) and b_len == b_corelen:
        LOGGER.debug('Looks like a standard core')
        b_data = b_data[:b_speclen]
    else:
        if validate_bin(b_data, b_spechead) and b_len == b_speclen:
            LOGGER.debug('Looks like a Spectrum core')
            b_data += b'\x00' * (b_corelen - b_speclen)
        else:
            LOGGER.error('Not a valid core file: %s', str_in_file)
            b_convert = False
    if b_convert:
        if b_force or check_overwrite(str_outfile):
            with open(str_outfile, "wb") as out_zxdata:
                out_zxdata.write(b_data)
                print(f'{str_outfile} created OK.')


def find_zxfile(str_in_file,
                fulldict_hash,
                str_extension,
                show_hashes,
                b_detail=False):
    """
    Try to guess ZX... file from hash
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param show_hashes: If True, print also found block hashes
    :param b_detail: If True, show extra info
    """
    found = False
    hash_dict = fulldict_hash[str_extension]
    d_parts = hash_dict['parts']

    dict_res = {}
    dict_res['detail'] = {}

    str_name = os.path.basename(str_in_file)
    print(
        f'\nAnalyzing {str_name} (possibly {hash_dict["description"]})...\n ')
    str_file_hash = get_file_hash(str_in_file)
    dict_res['hash'] = str_file_hash
    i_file_size = os.stat(str_in_file).st_size
    if show_hashes:
        print(f'Hash: {str_file_hash}')

    # Check if it's a known ZX Spectrum ROM
    for block_id in [
            '16K Spectrum ROM', '32K Spectrum ROM', '64K Spectrum ROM'
    ]:
        if block_id in d_parts:
            if i_file_size == int(d_parts[block_id][1]):
                LOGGER.debug('Looks like %s', block_id)
                block_version = get_data_version(str_file_hash,
                                                 hash_dict[block_id])
                if block_version != 'Unknown':
                    print(f'{block_id} -  Version: {block_version}')
                    dict_res['kind'] = block_id
                    dict_res['version'] = f'{block_version}'
                    found = True

    # Check if it's a main ROM
    for block_id in ['BIOS', 'Spectrum', 'Special', 'esxdos']:
        if not found and block_id in d_parts:
            if i_file_size == int(d_parts[block_id][1]) and validate_file(
                    str_in_file, d_parts[block_id][3]):
                LOGGER.debug('Looks like %s', block_id)
                block_version = get_data_version(str_file_hash,
                                                 hash_dict[block_id])
                if block_version != 'Unknown':
                    print(f'{block_id} -  Version: {block_version}')
                    dict_res['kind'] = block_id
                    dict_res['version'] = block_version
                    found = True

    # Check if it's a Core
    if not found and 'core_base' in d_parts:
        if validate_file(str_in_file,
                         d_parts['core_base'][3]) and i_file_size == int(
                             d_parts['core_base'][1]):
            LOGGER.debug('Looks like a core')
            for core_item in hash_dict['Cores']:
                block_version = get_data_version(str_file_hash,
                                                 hash_dict['Cores'][core_item])
                if block_version != 'Unknown':
                    print(f'Core: {core_item} - Version: {block_version}')
                    dict_res['kind'] = 'Core'
                    dict_res['version'] = f'{core_item}: {block_version}'
                    found = True
                    if b_detail:
                        printcol(Colours.BLUE,
                                 f' Features of "{core_item}" Cores:',
                                 end='\n')
                        dict_det = hash_dict['Cores'][core_item].get(
                            'features', {})
                        print_detail(core_item, dict_det)
                        dict_res['detail'] = dict_det
                    break

    # Check if it's a ROMPack ROMs file
    if not found and str_extension == 'ZX1':
        rompack = fulldict_hash['ROMS']['parts']
        i_rpck_size = int(rompack['header'][1])
        if i_rpck_size == i_file_size:
            found = list_romsdata(str_in_file, fulldict_hash, 'ROMS',
                                  show_hashes, True)
            dict_res['kind'] = 'ROMPack'
            dict_res['version'] = ''

    if not found:
        print('Unknown file')

    return dict_res


# Core Data Functions


def get_core_version(str_in_file, core_index, dict_parts, dict_cores):
    """
    Obtain name and version from core block in file
    :param str_in_file: Path to file
    :param core_index: Core Index in file
    :param dict_parts: Dictionary with file blocks info
    :param dict_cores: Dictionary with hashes and info for cores
    :return: List with name string, version string and hash string
    """

    block_info = dict_parts['cores_dir']
    max_cores = splitcore_index = int(block_info[4])

    if len(block_info) > 5:
        max_cores += int(block_info[5])
    if core_index > max_cores:
        LOGGER.error('Invalid core index: %i', core_index)

    core_bases = dict_parts['core_base']

    block_name = block_version = 'Unknown'
    block_hash = ''
    dict_details = {}
    block_data = get_core_blockdata(core_index, splitcore_index, core_bases)
    LOGGER.debug('Index %i: %X(%i)', core_index + 2, block_data[0],
                 block_data[0])

    for core_name in dict_cores:
        block_version, block_hash = get_version(str_in_file, block_data,
                                                dict_cores[core_name])
        if block_version != 'Unknown':
            block_name = core_name
            dict_details = dict_cores[core_name].get('features', {})
            break

    return block_name, block_version, block_hash, dict_details


def get_core_blockdata(core_index, spltcore_index, core_bases):
    """
    Get Core Offset and Length
    :param core_index: Index of the Core
    :param splitcore_index: Index of last core before split
    :param core_bases: Array with base offset and offset after split
    :return: Array with core offset and core length
    """

    core_base = int(core_bases[0])
    core_len = int(core_bases[1])

    core_split = 0
    if len(core_bases) > 4:
        core_split = int(core_bases[4])

    core_offset = core_base + core_index * core_len
    if core_split and core_index + 2 > spltcore_index:
        core_offset = core_split + (core_index - spltcore_index + 1) * core_len

    return [core_offset, core_len]


def get_core_list(str_in_file, dict_parts):
    """
    Obtain list of core names in file
    :param str_in_file: Path to file
    :param dict_parts: Dictionary with file blocks info
    :return: List of name strings
    """
    block_info = dict_parts['cores_dir']
    i_start = int(block_info[0])
    i_len = int(block_info[1])

    with open(str_in_file, "rb") as in_zxdata:
        in_zxdata.seek(i_start)
        bin_data = in_zxdata.read(i_len)

    name_list = get_core_list_bindata(bin_data, dict_parts)

    return name_list


def get_core_list_bindata(bin_data, dict_parts):
    """
    Obtain list of core names in binary data
    :param str_in_file: Binary data
    :param dict_parts: Dictionary with file blocks info
    :return: List of name strings
    """
    block_info = dict_parts['cores_dir']
    max_cores = int(block_info[4])
    if len(block_info) > 5:
        max_cores += int(block_info[5])

    name_offset = 0x100
    name_len = 0x20
    name_list = []
    for index in range(max_cores):
        str_name = bin_data[name_offset + index * name_len:name_offset +
                            (index + 1) * name_len]
        if str_name[0:1] == b'\x00':
            break
        else:
            name_list.append(str_name.decode('utf-8'))

    return name_list


# ROM data functions


def get_rom(str_in_file,
            rom_slot,
            rom_blocks,
            dict_full,
            in_file_ext,
            roms_file=False):
    """
    Obtain name, version and data from ROM block in file
    :param str_in_file: Path to file
    :param rom_slot: ROM slot number
    :param rom_blocks: Size of ROM in 16384 bytes blocks
    :param dict_full: Dictionary with hashes and info for cores
    :param in_file_ext: Extension of input file
    :param roms_file: If True, add extra offset as in ROM.ZX1 file
    :return: List with version string, hash string and offset
    """

    rom_split = int(dict_full[in_file_ext]['parts']['roms_dir'][5])
    block_bases = dict_full[in_file_ext]['parts']['roms_data']
    rom_data = get_rom_bin(str_in_file, rom_slot, rom_blocks, rom_split,
                           block_bases, roms_file)

    block_version, block_hash = get_romdata_version(rom_data, dict_full['ROM'])

    return block_version, block_hash, rom_data


def get_romdata_version(rom_data, dict_rom_hash):
    """
    Obtain name and version from ROM binary data
    :param rom_data: ROM binary data
    :param dict_rom_hash: Dictionary with hashes and info for ROMs
    :return: List with version string, hash string and offset
    """
    rom_blocks = int(len(rom_data) / 16384)
    block_hash = hashlib.sha256(rom_data).hexdigest()

    rom_types = [
        '16K Spectrum ROM', '32K Spectrum ROM', '', '64K Spectrum ROM'
    ]
    block_version = get_data_version(block_hash,
                                     dict_rom_hash[rom_types[rom_blocks - 1]])

    return block_version, block_hash


def get_rom_list(str_in_file, dict_parts, b_data=None):
    """
    Obtain list of ROM names ands slots in file
    :param str_in_file: Path to file
    :param dict_parts: Dictionary with file blocks info
    :return: List of slots, name strings and other info
    """
    roms_list = []

    block_info = dict_parts['roms_dir']
    if len(block_info) < 6:
        LOGGER.error('ROMs dir data missing from database')
    else:
        b_start = int(block_info[4])
        b_len = int(block_info[5]) + int(block_info[6])
        if b_data:
            roms_use = b_data[b_start:b_start + b_len]
        else:
            with open(str_in_file, "rb") as in_zxdata:
                in_zxdata.seek(b_start)
                roms_use = in_zxdata.read(b_len)

        for i, rom_index in enumerate(roms_use):
            if rom_index != 0xff:
                b_start = int(block_info[0]) + i * 64
                b_len = 64
                if b_data:
                    rom_data = b_data[b_start:b_start + b_len]
                else:
                    with open(str_in_file, "rb") as in_zxdata:
                        in_zxdata.seek(b_start)
                        rom_data = in_zxdata.read(b_len)

                rom_slot = rom_data[0]
                rom_size = rom_data[1]
                rom_flags = bit_to_flag(rom_data[2] ^ 0b00110000, '* icdnpt')
                rom_flags += bit_to_flag(rom_data[3] ^ 0b00000000, 'smhl172a')
                rom_flags += bit_to_flag(rom_data[4] ^ 0b00000000, '     rxu')
                rom_crc = ''
                for j in range(0, 16):
                    byte = rom_data[8 + j]
                    if byte:
                        rom_crc += f'{byte:02X}'
                rom_name = rom_data[32:]
                if rom_name[0] >= 32:
                    try:
                        roms_list.append([
                            rom_index, rom_slot,
                            rom_name.decode('utf-8'), rom_size, rom_flags,
                            rom_crc
                        ])
                    except UnicodeDecodeError:
                        LOGGER.debug('Bad ROM entry or corrupted ROM name')
            else:
                break

    return roms_list


def get_rom_bin(str_in_file,
                rom_slot,
                rom_blocks,
                rom_split,
                rom_bases,
                roms_file=False):
    """
    Extract ROM data blocks to memory
    :param str_in_file: Path to file
    :param rom_slot: Slot number
    :param rom_blocks: Size of ROM in 16384 bytes blocks
    :param rom_split: Slot number where rom binary data is split in two
    :param rom_bases: Offsets for ROM binary data
    :param roms_file: If True, add extra offset as in ROM.ZX1 file
    :return: Binary data of ROM
    """

    rom_data = b''
    for rom_blk in range(rom_slot, rom_slot + rom_blocks):
        rom_offset = get_romb_offset(rom_blk, rom_split, rom_bases, roms_file)
        LOGGER.debug('Slot %i: %X (%i)', rom_blk, rom_offset, rom_offset)

        with open(str_in_file, "rb") as in_zxrom:
            in_zxrom.seek(rom_offset)
            rom_data += in_zxrom.read(16384)

    return rom_data


def get_romb_offset(rom_slot, rom_split, rom_bases, roms_file=False):
    """
    Get ROM slot offset in SPI Flash or ROMS.ZX1 file
    :param rom_slot: ROM slot index
    :param rom_split: Slot number where rom binary data is split in two
    :param rom_bases: Offsets for ROM binary data
    :param roms_file: If True, add extra offset as in ROM.ZX1 file
    """
    if rom_slot < rom_split:
        rom_base = int(rom_bases[0])
        rom_offset = rom_base + rom_slot * 16384
    else:
        rom_base = int(rom_bases[4])
        rom_offset = rom_base + (rom_slot - rom_split) * 16384

    if roms_file:
        rom_offset += 1

    return rom_offset


def new_romentry(rom_slt, rom_name, rom_len, rom_params, rom_crc):
    """
    Creates binary ROM entry data (64 bytes)
    :param rom_slt: ROM slot number
    :param rom_name: ROM Name
    :param rom_len: ROM length (16384k blocks)
    :param rom_params: ROM parameters (icdnptsmhl172arxu)
    :param rom_crc: ROM CRC (string with hex values)
    :return: Binary data for ROM entry
    """
    new_entry = (rom_slt).to_bytes(1, byteorder='little')
    new_entry += (rom_len).to_bytes(1, byteorder='little')

    new_entry += flag_to_bits(rom_params, '* icdnpt', 0b00110000)
    new_entry += flag_to_bits(rom_params, 'smhl172a', 0b00000000)
    new_entry += flag_to_bits(rom_params, '     rxu', 0b00000000)
    new_entry += b'\x00' * 3
    new_entry += bytes.fromhex(rom_crc)
    new_entry += b'\x00' * (24 - int(len(rom_crc) / 2))
    new_entry += bytes(rom_name, 'utf-8')

    return new_entry


def get_rom_crc(rom_data):
    """
    Computes ROM crc as string
    :param data: ByteArray wich contains the data
    :return: String with CRC
    """
    rom_blocks = int(len(rom_data) / 16384)
    str_crc = ''
    for rom_block in range(0, rom_blocks):
        block_crc = get_crc16(rom_data, rom_block * 16384, 16384)
        str_crc = f'{block_crc:04X}{str_crc}'

    return str_crc


def get_crc16(data, offset, length):
    """
    Computes CRC16
    :param data: ByteArray wich contains the data
    :param offset: Data offset to begin the calculation
    :param length: Number of bytes after the offset
    :return: Integer (4 bytes) with CRC or 0000 on error
    """
    if data is None or offset < 0 or offset > len(
            data) - 1 and offset + length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for _ in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def bit_to_flag(b_input, str_flags):
    """
    Analyze byte and select string chars depending on bits
    :param b_input: Byte to analyze
    :param str_flags: String with chars to use
    :return: String with chars according to bit state
    """
    str_result = ''
    for i in range(8):
        if b_input << i & 128:
            if str_flags[i] != ' ':
                str_result += str_flags[i]
    return str_result


def flag_to_bits(str_input, str_flags, i_mask=0):
    """
    Analyze string  and create byte according to flags string
    :param str_input: String with 0 or more flags
    :param str_flags: 8 char string with flags
    :param i_mask: Byte mask to apply (xor) to result
    :return: Bytes with bits enabled according to flags
    """

    i_result = 0
    for i in range(8):
        if str_flags[7 - i] in str_input:
            i_result += 1 << i

    i_result ^= i_mask
    b_result = (i_result).to_bytes(1, 'little')
    return b_result


# Injection functions


def inject_bindata(str_in_params, hash_dict, b_data):
    """
    Add binary from one ROM binary file to SPI flash data
    :param str_in_params: String with one of BIOS, esxdos or Spectrum and,
     separated with ',', file path to the binary file
    :param hash_dict: Dictionary with hashes for different blocks
    :param b_data: SPI flash data
    :return: Altered binary data, boolean indicating changes and error string
    """
    b_changed = False
    str_err = ''
    arr_params = str_in_params.split(',')
    br_data = b_data

    for bl_id in ['BIOS', 'esxdos', 'Spectrum', 'Special']:
        hash_parts = hash_dict['parts'].get(bl_id, [])
        if arr_params[0].upper() == bl_id.upper():
            if len(arr_params) != 2:  # Filename
                str_err = f'Invalid data: {str_in_params}'
            else:
                str_in_file = arr_params[1]
                str_hash = get_file_hash(str_in_file)
                b_offset = int(hash_parts[0])
                b_len = int(hash_parts[1])
                b_head = hash_parts[3]
                if validate_file(
                        str_in_file,
                        b_head) and os.stat(str_in_file).st_size == b_len:
                    LOGGER.debug('Looks like %s', bl_id)
                    bl_version = get_data_version(str_hash, hash_dict[bl_id])
                    print(f'Adding {bl_id}: {bl_version}...')

                    with open(str_in_file, "rb") as in_zxdata:
                        in_data = in_zxdata.read(b_len)

                    if len(b_data) >= b_offset + b_len:
                        br_data = b_data[:b_offset] + in_data
                        br_data += b_data[b_offset + b_len:]
                        b_changed = True

    if str_err:
        LOGGER.error(str_err)
    return br_data, b_changed, str_err


def inject_coredata(str_in_params, hash_dict, b_data):
    """
    Add binary from one core binary file to SPI flash data
    :param str_in_params: String with CORE, and, separated with ',': core
     number, core name and file path to the core file
    :param hash_dict: Dictionary with hashes for different blocks
    :param b_data: SPI flash data
    :return: Altered binary data, boolean indicating changed and error string
    """
    str_err = ''
    b_changed = False
    dict_parts = hash_dict['parts']

    arr_params = str_in_params.split(',')
    br_data = b_data

    if arr_params[0].upper() == 'CORE':  # Number, Name, Filename
        block_info = dict_parts.get('cores_dir', [])
        max_cores = splitcore_index = int(block_info[4])
        if len(block_info) > 5:
            max_cores += int(block_info[5])
        core_bases = dict_parts['core_base']
        b_len = int(core_bases[1])
        b_head = core_bases[3]

        bl_data = b_data[int(block_info[0]):int(block_info[0]) +
                         int(block_info[1])]
        core_list = get_core_list_bindata(bl_data, dict_parts)

        if len(arr_params) != 4:
            str_err = f'Invalid argument: {str_in_params}'
        else:
            core_index = int(arr_params[1])
            str_name = f'{arr_params[2][:32]:<32}'
            str_in_file = arr_params[3]
            str_hash = get_file_hash(str_in_file)
            # Check header and length
            if validate_file(str_in_file,
                             b_head) and os.stat(str_in_file).st_size == b_len:
                LOGGER.debug('Looks like a core')
                core_name = ''
                block_version = 'Unknown'
                for core_item in hash_dict['Cores']:
                    block_version = get_data_version(
                        str_hash, hash_dict['Cores'][core_item])
                    if block_version != 'Unknown':
                        core_name = core_item
                        break

                if core_index > len(core_list) + 1:
                    core_index = len(core_list) + 2

                if core_index < 2 or core_index > max_cores:
                    str_err = f'Invalid core index: {core_index}'
                else:
                    print(
                        f'Adding core {core_index}: {core_name} ({block_version})...'
                    )
                    core_index -= 2
                    block_data = get_core_blockdata(core_index,
                                                    splitcore_index,
                                                    core_bases)
                    b_offset, b_len = block_data
                    LOGGER.debug('Offset: %X (%i)', b_offset, b_offset)

                    if b_offset + b_len > len(b_data):
                        str_err = 'Flash image too small for data'
                    else:
                        core_index = 0x100 + core_index * 32
                        bl_data = bl_data[:core_index] + bytes(
                            str_name, 'utf-8') + bl_data[core_index + 32:]

                        br_data = b_data[:int(block_info[0])] + bl_data
                        br_data += b_data[int(block_info[0]) +
                                          int(block_info[1]):]

                        with open(str_in_file, "rb") as in_zxdata:
                            in_data = in_zxdata.read()
                            br_data = br_data[:b_offset] + in_data

                        br_data += b_data[b_offset + b_len:]
                        b_changed = True

    if str_err:
        LOGGER.error(str_err)
    return br_data, b_changed, str_err


def inject_romdata(str_in_file, str_in_params, fullhash_dict, str_extension,
                   b_data):
    """
    Add binary from one Spectrum ROM binary file to SPI flash or RPv2 data
    :param str_in_file: File with SPI flash (or ROMPackV2) data
    :param str_in_params: String with ROM, and, separated with ',': ROM slot
     number, ROM params (icdnptsmhl172arxu), ROM name to use and file path to
     the ROM file
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param b_data: SPI flash data obtained from str_in_file
    :return: Altered binary data,boolean indicating changes, and error string
    """
    b_changed = False
    str_err = ''
    b_roms = False
    if str_extension == 'RPv2':
        b_roms = True

    hash_dict = fullhash_dict[str_extension]
    dict_parts = hash_dict['parts']

    arr_params = str_in_params.split(',')
    br_data = b_data

    free_slot = 0
    block_info = dict_parts['roms_dir']
    max_slots = int(block_info[5])
    max_slots += int(block_info[6])
    block_bases = dict_parts['roms_data']

    if arr_params[0].upper() == 'ROM':  # Slot, Params, Name, Filename
        if len(arr_params) != 5:
            str_err = f'Invalid argument: {str_in_params}'
        else:
            roms_list = get_rom_list(str_in_file, dict_parts, br_data)
            slot_use = []
            for rom_entry in roms_list:
                if rom_entry[1] + 1 > free_slot:
                    free_slot = rom_entry[1] + 1
                i_slot = rom_entry[1] + 1
                for _ in range(1, rom_entry[3]):
                    slot_use.append(i_slot)
                    i_slot += 1
                    if i_slot > free_slot:
                        free_slot = i_slot

            rom_slt = int(arr_params[1])
            rom_params = arr_params[2]
            str_name = arr_params[3]
            str_rom_file = arr_params[4]

            if rom_slt == 99:
                rom_slt = free_slot

            b_len = os.stat(str_rom_file).st_size
            if b_len != 0 and b_len % 16384 == 0:
                LOGGER.debug('Looks like a ROM')
                b_len = int(b_len / 16384)

                if rom_slt in slot_use or rom_slt < 0 or rom_slt > max_slots:
                    str_err = f'Invalid slot number: {rom_slt}'
                    rom_slt = -1

                if rom_slt + b_len > max_slots:
                    str_err = f'Slot number too high ({rom_slt})'
                    rom_slt = -1

                rom_index = len(roms_list)
                for rom_entry in roms_list:
                    if rom_slt == rom_entry[1]:
                        rom_index = rom_entry[0]
                        if b_len != rom_entry[3]:
                            str_err = f'Invalid ROM size for slot {rom_slt}'
                            rom_slt = -1
                        break

                if rom_slt > -1:
                    with open(str_rom_file, "rb") as in_zxdata:
                        rom_data = in_zxdata.read()

                    r_v = get_romdata_version(rom_data, fullhash_dict['ROM'])
                    print(f'Injecting ROM {rom_slt} ({r_v[0]})...')

                    br_data, b_changed = inject_rom_tobin(b_data,
                                                          block_info,
                                                          block_bases,
                                                          rom_index,
                                                          rom_slt,
                                                          str_name,
                                                          rom_params,
                                                          rom_data,
                                                          roms_file=b_roms)

    if str_err:
        LOGGER.error(str_err)
    return br_data, b_changed, str_err


def inject_romszx1data(str_in_params, fullhash_dict, str_extension, b_data):
    """
    Add ROMs from a Spectrum ROMS.ZX1 binary file to SPI flash or RPv2 data
    :param str_in_file: File with SPI flash (or ROMPackV2) data
    :param str_in_params: String with ROMS, and, separated with ',': file path
     to ROMS.ZX1
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param b_data: SPI flash data obtained from str_in_file
    :return: Altered binary data, boolean with change state and error strings
    """
    arr_err = []
    b_changed = False

    # SPI flash ROMs
    hash_dict = fullhash_dict[str_extension]
    dict_parts = hash_dict['parts']

    b_roms = False
    def_r_addr = 28736
    if str_extension == 'RPv2':
        b_roms = True
        def_r_addr = int(dict_parts['roms_data'][0])
    block_info = dict_parts['roms_dir']
    max_slots = int(block_info[5])
    max_slots += int(block_info[6])
    block_bases = dict_parts['roms_data']

    # Empty ROMs list
    roms_use = b'\xff' * (int(block_info[5]) + int(block_info[6]))

    # ZX1 ROMS
    rom_dict_parts = fullhash_dict['ROMS']['parts']
    blk_info = rom_dict_parts['roms_dir']
    rm_split = int(blk_info[5])
    blk_bases = rom_dict_parts['roms_data']

    arr_params = str_in_params.split(',')
    br_data = b_data

    if arr_params[0].upper() == 'ROMS':  # Filename
        if len(arr_params) != 2:
            str_err = f'Invalid argument: {str_in_params}'
            LOGGER.error(str_err)
            arr_err.append(str_err)
        else:
            str_name = arr_params[1]
            roms_list = get_rom_list(str_name, rom_dict_parts)

            if roms_list:
                def_rom = get_peek(str_name, 4160)
                # Clear ROMs list in SPI flash (Temp Binary Data)
                br_data = b_data[:int(block_info[4])] + roms_use
                br_data += b_data[int(block_info[4]) + len(roms_use):]

                print(f'Injecting ROMs from {str_name}...')
                for rom_item in roms_list:
                    rom_index = rom_item[0]
                    rom_slt = rom_item[1]
                    rom_name = rom_item[2]
                    rom_params = rom_item[4]
                    rom_crc = rom_item[5]

                    rom_data = get_rom_bin(str_name, rom_item[1], rom_item[3],
                                           rm_split, blk_bases, True)

                    rom_len = int(len(rom_data) / 16384)
                    if rom_slt + rom_len - 1 < max_slots:
                        LOGGER.debug('Injecting ROM %i (%s)...', rom_slt,
                                     rom_name)

                        br_data, b_chg = inject_rom_tobin(
                            br_data, block_info, block_bases, rom_index,
                            rom_slt, rom_name, rom_params, rom_data, rom_crc,
                            b_roms)
                        b_changed |= b_chg
                    else:
                        str_err = f'Slot number too high: {rom_slt}'
                        LOGGER.error(str_err)
                        arr_err.append(str_err)

                if b_changed:
                    br_data, b_chg, arr_b_err = inject_biossettings(
                        br_data, default_rom=def_rom, d_rom_addr=def_r_addr)
                    if arr_b_err:
                        arr_err += arr_b_err

    return br_data, b_changed, arr_err


def inject_rom_tobin(b_data,
                     block_info,
                     block_bases,
                     rom_index,
                     rom_slt,
                     rom_name,
                     rom_params,
                     rom_data,
                     rom_crc=None,
                     roms_file=False):
    """
    Add binary data of a ROM to binary file data (SPI Flash or ROMS.ZX1)
    :param b_data: SPI flash data obtained from str_in_file
    :param block_info: 'roms_dir' entry of hashes dict
    :param block_bases: 'roms_data' entry of hashes dict
    :param rom_index: ROM index number
    :param rom_slt: ROM slot number
    :param rom_name: String with ROM name
    :param rom_params: String tiwh ROM params (icdnptsmhl172arxu)
    :param rom_data: ROM binary data
    :param rom_crc: Optional string with ROM crc16
    :param roms_file: If True, parse output data as ROMS.ZX1 file
    :return: Altered binary file data and boolean indicating if it changed
    """
    b_changed = False
    rom_split = int(block_info[5])

    rom_name = f'{rom_name[:32]:<32}'
    rom_len = int(len(rom_data) / 16384)
    if not rom_crc:
        rom_crc = get_rom_crc(rom_data)
    rom_entry = new_romentry(rom_slt, rom_name, rom_len, rom_params, rom_crc)

    # Inject ROM entry
    cur_pos = int(block_info[0]) + rom_index * 64
    br_data = b_data[:cur_pos]
    br_data += rom_entry
    cur_pos += 64

    # Inject ROM index
    br_data += b_data[cur_pos:int(block_info[4])]
    cur_pos = int(block_info[4])
    br_data += b_data[cur_pos:cur_pos + rom_index]
    br_data += (rom_index).to_bytes(1, byteorder='little')
    cur_pos += rom_index + 1

    # Inject ROM binary data
    for i in range(rom_len):
        rom_offset = get_romb_offset(rom_slt + i, rom_split, block_bases,
                                     roms_file)
        if rom_offset > cur_pos:
            if rom_offset + 16384 <= len(b_data):
                br_data += b_data[cur_pos:rom_offset]
                b_changed = True
            else:
                LOGGER.error('Flash image too small for: %s', rom_name)
                b_changed = False
                break

        br_data += rom_data[i * 16384:(i + 1) * 16384]
        cur_pos = rom_offset + 16384

    if b_changed:
        br_data += b_data[cur_pos:]
    else:
        br_data = b_data

    return br_data, b_changed


def inject_biossettings(b_data,
                        video_mode=-1,
                        keyboard_layout=-1,
                        boot_timer=-1,
                        default_core=-1,
                        default_rom=-1,
                        d_rom_addr=28736):
    """
    Alter SPI flash BIOS or RPv2 settings
    :param b_data: Binary data to modify
    :param video_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyboard_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :param boot_timer: 0 (No timer), 1, 2 (2x), 3 (4x), 4 (8x)
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :return: Altered SPI flash data, alter state and error strings array
    """
    b_changed = False
    br_data = b_data
    arr_err = []

    # 28736 Default ROM: 00-xx
    if default_rom > -1:
        br_data = br_data[:d_rom_addr] + struct.pack(
            '<B', default_rom) + br_data[d_rom_addr + 1:]
        b_changed = True

    # 28737 Default Core: 01-xx
    if default_core > -1:
        br_data = br_data[:28737] + struct.pack('<B',
                                                default_core) + br_data[28738:]
        b_changed = True

    # 28738 0-4 Boot Timer
    if boot_timer > -1:
        if boot_timer > 4:
            str_err = f'Wrong Boot Timer: {boot_timer}'
            LOGGER.error(str_err)
            arr_err.append(str_err)
        else:
            br_data = br_data[:28738] + struct.pack(
                '<B', boot_timer) + br_data[28739:]
            b_changed = True

    # 28746 0-3 Keyboard Layout: Auto-ES-EN-ZX
    if keyboard_layout > -1:
        if keyboard_layout > 3:
            str_err = f'Wrong Keyboard Layout: {keyboard_layout}'
            LOGGER.error(str_err)
            arr_err.append(str_err)
        else:
            br_data = br_data[:28746] + struct.pack(
                '<B', keyboard_layout) + br_data[28747:]
            b_changed = True

    # 28749 0-2 Video: PAL-NTSC-VGA
    if video_mode > -1:
        if video_mode > 3:
            str_err = f'Wrong Video Mode: {video_mode}'
            LOGGER.error(str_err)
            arr_err.append(str_err)
        else:
            br_data = br_data[:28749] + struct.pack(
                '<B', video_mode) + br_data[28750:]
            b_changed = True

    return br_data, b_changed, arr_err


# SPI/ROM file generic functions


def get_version(str_in_file, block_info, hash_dict):
    """
    Obtain version string in block in file using dictionary of hashes
    :param str_in_file: Path to file
    :param block_info: List with block offset and block length
    :param hash_dict: Dictionary with hashes for different blocks
    :return: List with version string and hash string
    """
    f_size = os.stat(str_in_file).st_size
    str_version = ''
    str_hash = ''

    i_start = int(block_info[0])
    i_len = int(block_info[1])
    if f_size >= i_start + i_len:
        with open(str_in_file, "rb") as in_zxd:
            in_zxd.seek(i_start)
            bin_data = in_zxd.read(i_len)
            str_hash = hashlib.sha256(bin_data).hexdigest()
            del bin_data

        str_version = get_data_version(str_hash, hash_dict)
    else:
        LOGGER.debug('File too small to check version')

    return str_version, str_hash


def get_data_version(str_hash, hash_dict):
    """
    Obtain version string from hash
    :param str_hash: Hash string to check
    :param hash_dict: Dictionary with hashes for different blocks
    :return: List with version string and hash string
    """
    str_version = 'Unknown'

    if 'versions' in hash_dict:
        hash_dict = hash_dict['versions']

    for hash_elem in hash_dict:
        if str_hash == hash_dict[hash_elem]:
            str_version = hash_elem
            break

    return str_version


def get_peek(str_in_file, block_offset):
    """
    Get value of one byte in binary file
    :param str_in_file: Path to file
    :param block_offset: Offset in file to read
    :return: Number with the obtained value
    """
    with open(str_in_file, "rb") as in_zxd:
        in_zxd.seek(block_offset)
        bin_data = in_zxd.read(1)

    return struct.unpack('<B', bin_data)[0]


def validate_and_export_bin(str_in_file,
                            block_info,
                            str_out_bin,
                            b_force=False,
                            str_magic=None):
    """
    Extract data block to file, optionally vallidating the header
    :param str_in_file: Path to file
    :param block_info: List with block offset and block length
    :param str_out_bin: Path to bin file to create
    :param str_magic: String with the bytes to match
    """
    f_size = os.stat(str_in_file).st_size
    bin_data = None
    i_start = int(block_info[0])
    i_len = int(block_info[1])

    if f_size >= i_start + i_len:
        with open(str_in_file, "rb") as in_zxdata:
            in_zxdata.seek(i_start)
            bin_data = in_zxdata.read(i_len)

        if str_magic:
            if not validate_bin(bin_data, str_magic):
                LOGGER.error('Invalid data')
                return

        export_bindata(bin_data, str_out_bin, b_force)
    else:
        LOGGER.debug('File too small to export')


def export_bin(str_in_file, block_info, str_out_bin, b_force=False):
    """
    Extract data block to file
    :param str_in_file: Path to file
    :param block_info: List with block offset and block length
    :param str_out_bin: Path to bin file to create
    """
    with open(str_in_file, "rb") as in_zxdata:
        in_zxdata.seek(block_info[0])
        bin_data = in_zxdata.read(block_info[1])

    export_bindata(bin_data, str_out_bin, b_force)


# Generic File Functions


def validate_file(str_in_file, str_magic):
    """
    Try to detect ZX... file type from first bytes
    :param str_in_file: Path to file
    :param str_magic: String with the bytes to match
    :return: True if bytes match, False in other case
    """
    magic_bin = unhexlify(str_magic)
    if str_magic:
        try:
            with open(str_in_file, "rb") as bin_file:
                bin_data = bin_file.read(len(magic_bin))
                b_validate = validate_bin(bin_data, str_magic)
        except FileNotFoundError:
            b_validate = False

        return b_validate
    else:
        return False


def validate_bin(bin_data, str_magic):
    """
    Try to detect ZX data type from first bytes
    :param bin_data: binary data of file
    :param str_magic: String with the bytes to match
    :return: True if bytes match, False in other case
    """
    magic_bin = unhexlify(str_magic)
    if magic_bin:
        if magic_bin == bin_data[:len(magic_bin)]:
            return True
        else:
            return False
    else:
        return False


def get_file_hash(str_in_file):
    """
    Get file sha26 hash
    :param str_in_file: Path to file
    :return: String with hash data
    """
    sha256_hash = hashlib.sha256()
    with open(str_in_file, "rb") as f_data:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f_data.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def export_bindata(bin_data, str_out_bin, b_force=False):
    """
    Extract binary data to file
    :param bin_data: Binary data
    :param str_out_bin: Path to bin file to create
    """
    if b_force or check_overwrite(str_out_bin):
        with open(str_out_bin, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print(f'{str_out_bin} created OK.')


def check_overwrite(str_file):
    """
    Check if file exists. If so, ask permission to overwrite
    :param str_file: Path to file
    :return: Bool, if True, permission granted to overwrite
    """
    b_writefile = True
    if os.path.isfile(str_file):
        str_name = os.path.basename(str_file)
        b_ask = True
        while b_ask:
            chk_overwrite = input(f'{str_name} exists. Overwrite? (Y/N): ')
            if chk_overwrite.upper() == 'N' or chk_overwrite == '':
                b_writefile = False
                b_ask = False
            if chk_overwrite.upper() == 'Y':
                b_ask = False

    return b_writefile


if __name__ == "__main__":
    main()
