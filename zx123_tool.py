#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
"""
ZX-Uno, ZXDOS, ZXDOS+, gomaDOS+ Tool for ZXDOS, etc. files.

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
"""

import logging
import sys
import argparse
import os
import json
import hashlib
from binascii import unhexlify
import struct
import six

if six.PY2:
    input = raw_input

__MY_VERSION__ = '0.4'

MAX_CORES = 45

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter(
    '%(asctime)s [%(levelname)-5.5s] - %(name)s: %(message)s')
LOG_STREAM = logging.StreamHandler(sys.stdout)
LOG_STREAM.setFormatter(LOG_FORMAT)
LOGGER.addHandler(LOG_STREAM)


def main():
    """Main routine"""

    LOGGER.debug('Starting up...')
    arg_data = parse_args()

    my_dirpath = os.path.dirname(sys.argv[0])
    my_dirpath = os.path.abspath(my_dirpath)
    str_json = os.path.join(my_dirpath, 'zx123_hash.json')
    if not os.path.isfile(str_json):
        LOGGER.error('Hash database not found: {0}'.format(str_json))
        sys.exit(1)
    with open(str_json, 'r') as jsonHandle:
        LOGGER.debug('Loading dictionary with hashes...')
        dict_hash = json.load(jsonHandle)

    str_file = arg_data['input_file']
    str_outdir = arg_data['output_dir']
    if not str_outdir:
        str_outdir = os.path.dirname(str_file)
    str_extension = os.path.splitext(str_file)[1]
    str_extension = str_extension[1:].upper()
    if str_extension in dict_hash:
        dict_hash = dict_hash[str_extension]
    else:
        LOGGER.error('Unknown file extension {0}'.format(str_extension))
        sys.exit(2)

    if validate_file(str_file, dict_hash['parts']['header'][3]):
        if arg_data['list']:
            list_zxdata(str_file, dict_hash, arg_data['show_hashes'])

        for x_item in arg_data['extract']:
            extractfrom_zxdata(str_file, x_item, dict_hash, str_outdir,
                               str_extension, arg_data['force'])

        if arg_data['output_file']:
            savefrom_zxdata(str_file, dict_hash, arg_data['output_file'],
                            arg_data['n_cores'], arg_data['video_mode'],
                            arg_data['keyboard_layout'], arg_data['force'])
    else:
        find_zxfile(str_file, dict_hash, arg_data['show_hashes'])

    print('')
    LOGGER.debug("Finished.")


def parse_args():
    """
    Parses command line
    :return: Dictionary with different options
    """
    values = {}
    values['input_file'] = ''
    values['output_dir'] = ''
    values['output_file'] = ''
    values['force'] = False
    values['list'] = False
    values['show_hashes'] = False
    values['extract'] = []
    values['n_cores'] = -1
    values['video_mode'] = -1
    values['keyboard_layout'] = -1

    parser = argparse.ArgumentParser(
        description='ZX123 Tool',
        epilog='Analyze and extract data from ZXDOS, etc. files')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s {0}'.format(__MY_VERSION__))
    parser.add_argument('-i',
                        '--input_file',
                        required=True,
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
                        action='store',
                        dest='n_cores',
                        help='Number of cores to store on output file')
    parser.add_argument('-m',
                        '--video_mode',
                        required=False,
                        action='store',
                        dest='video_mode',
                        help='Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)')
    parser.add_argument(
        '-k',
        '--keyboard_layout',
        required=False,
        action='store',
        dest='keyboard_layout',
        help='Keyboard Layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)')

    arguments = parser.parse_args()

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

    if arguments.show_hashes:
        values['show_hashes'] = arguments.show_hashes

    if arguments.extract:
        values['extract'] = arguments.extract.split(',')

    if arguments.n_cores:
        values['n_cores'] = int(arguments.n_cores)

    if arguments.video_mode:
        values['video_mode'] = int(arguments.video_mode)

    if arguments.keyboard_layout:
        values['keyboard_layout'] = int(arguments.keyboard_layout)

    return values


def list_zxdata(str_in_file, hash_dict, show_hashes):
    """
    List content of file
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param show_hashes: If True, print also block hashes
    """
    LOGGER.debug('Listing contents of file: {0}'.format(str_in_file))
    str_name = os.path.basename(str_in_file)
    print('\nContents of {0} (possibly {1})\n'.format(
        str_name, hash_dict['description']))
    block_list = ['BIOS', 'esxdos', 'Spectrum']
    for block_name in block_list:
        block_version, block_hash = get_version(str_in_file,
                                                hash_dict['parts'][block_name],
                                                hash_dict[block_name])
        print('{0}: {1}'.format(block_name, block_version))
        if (show_hashes):
            print(block_hash)

    core_list = get_core_list(str_in_file, hash_dict['parts'])
    for index, name in enumerate(core_list):
        block_name, block_version, block_hash = get_core_version(
            str_in_file, index, hash_dict['parts'], hash_dict['Cores'])

        print('Core {0:02d} "{1}" -> {2}: {3}'.format(index + 2, name,
                                                      block_name,
                                                      block_version))
        if (show_hashes):
            print(block_hash)

    print('\nBIOS Defaults:')

    keyb_layout = get_peek(str_in_file, 28746)
    print('\tKeyboard Layout -> {0}'.format(keyb_layout))

    video_mode = get_peek(str_in_file, 28749)
    print('\tVideo Mode -> {0}'.format(video_mode))


def extractfrom_zxdata(str_in_file,
                       extract_item,
                       hash_dict,
                       str_dir,
                       str_extension,
                       b_force=False):
    """
    Parse and extract data block to file
    :param str_in_file: Path to file
    :param extract_item: Block ID string  or Core Number
    :param hash_dict: Dictionary with hashes for different blocks
    :param str_extension: Extension for Core files
    """
    block_list = ['BIOS', 'esxdos', 'Spectrum']
    for block_name in block_list:
        if extract_item.lower() == block_name.lower():
            print('Extracting {0}...'.format(block_name))
            block_info = hash_dict['parts'][block_name]
            str_bin = hash_dict['parts'][block_name][2]
            str_bin = os.path.join(str_dir, str_bin)
            export_bin(str_in_file, block_info, str_bin, b_force)
            break

    core_base = hash_dict['parts']['core_base'][0]
    core_len = hash_dict['parts']['core_base'][1]
    if extract_item.isdigit():
        core_number = int(extract_item)
        core_list = get_core_list(str_in_file, hash_dict['parts'])
        if core_number > 1 and core_number < (len(core_list) + 2):
            print('Extracting Core {0}...'.format(core_number))
            core_number -= 2
            block_name, block_version, block_hash = get_core_version(
                str_in_file, core_number, hash_dict['parts'],
                hash_dict['Cores'])
            core_offset = core_base + core_number * core_len
            block_info = [core_offset, core_len]
            str_bin = 'CORE{0:02d}_{1}_v{2}.{3}'.format(
                core_number + 2, block_name.replace(' ', '_'), block_version,
                str_extension)
            str_bin = os.path.join(str_dir, str_bin)
            export_bin(str_in_file, block_info, str_bin, b_force)
        else:
            LOGGER.error('Invalid core number: {0}'.format(core_number))


def get_version(str_in_file, block_info, hash_dict):
    """
    Obtain version string in block in file using dictionary of hashes
    :param str_in_file: Path to file
    :param block_info: List with block offset and block length
    :param hash_dict: Dictionary with hashes for different blocks
    :return: List with version string and hash string
    """
    with open(str_in_file, "rb") as in_zxd:
        in_zxd.seek(block_info[0])
        bin_data = in_zxd.read(block_info[1])
        str_hash = hashlib.sha256(bin_data).hexdigest()
        del bin_data

    str_version = 'Unknown'
    for hash_elem in hash_dict:
        if str_hash == hash_dict[hash_elem]:
            str_version = hash_elem
            break

    return str_version, str_hash


def get_core_version(str_in_file, core_index, dict_parts, dict_cores):
    """
    Obtain name and version from core block in file
    :param str_in_file: Path to file
    :param core_index: Core Index in file
    :param dict_parts: Dictionary with file blocks info
    :param dict_cores: Dictionary with hashes and info for cores
    :return: List with name string, version string and hash string
    """
    core_base = dict_parts['core_base'][0]
    core_len = dict_parts['core_base'][1]

    core_offset = core_base + core_index * core_len
    block_data = [core_offset, core_len]
    block_name = block_version = 'Unknown'
    block_hash = ''
    for core_name in dict_cores:
        block_version, block_hash = get_version(str_in_file, block_data,
                                                dict_cores[core_name])
        if block_version != 'Unknown':
            block_name = core_name
            break

    return block_name, block_version, block_hash


def get_core_list(str_in_file, dict_parts):
    """
    Obtain list of core names in file
    :param str_in_file: Path to file
    :param dict_parts: Dictionary with file blocks info
    :return: List of name strings
    """
    block_info = dict_parts['cores_dir']
    with open(str_in_file, "rb") as in_zxdata:
        in_zxdata.seek(block_info[0])
        bin_data = in_zxdata.read(block_info[1])

    name_offset = 0x100
    name_len = 0x20
    name_list = []
    for index in range(MAX_CORES):
        str_name = bin_data[name_offset + index * name_len:name_offset +
                            (index + 1) * name_len]
        if str_name[0:1] == b'\x00':
            break
        else:
            name_list.append(str_name.decode('utf-8'))

    return name_list


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

    if b_force or check_overwrite(str_out_bin):
        with open(str_out_bin, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print('{0} created OK.'.format(str_out_bin))


def find_zxfile(str_in_file, hash_dict, show_hashes):
    """
    Try to guess ZX... file from hash
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param show_hashes: If True, print also found block hashes
    """
    found = False

    str_name = os.path.basename(str_in_file)
    print('\nAnalyzing {0} (possibly {1})...\n '.format(
        str_name, hash_dict['description']))
    str_file_hash = get_file_hash(str_in_file)
    if show_hashes:
        print('{0}'.format(str_file_hash))

    for block_id in ['BIOS', 'Spectrum']:
        if validate_file(
                str_in_file, hash_dict['parts'][block_id][3]) and os.stat(
                    str_in_file).st_size == hash_dict['parts'][block_id][1]:
            LOGGER.debug('Looks like {0}'.format(block_id))
            for block_version in hash_dict[block_id]:
                LOGGER.debug('Checking {0}'.format(block_version))
                if str_file_hash == hash_dict[block_id][block_version]:
                    print('{0} -  Version: {1}'.format(block_id,
                                                       block_version))
                    found = True
                    break

    if not found:
        if validate_file(
                str_in_file, hash_dict['parts']['core_base'][3]) and os.stat(
                    str_in_file).st_size == hash_dict['parts']['core_base'][1]:
            LOGGER.debug('Looks like a core')
            for core_item in hash_dict['Cores']:
                for core_version in hash_dict['Cores'][core_item]:
                    LOGGER.debug('Checking  {0} v{1}'.format(
                        core_item, core_version))
                    if str_file_hash == hash_dict['Cores'][core_item][
                            core_version]:
                        print('Core: {0} - Version: {1}'.format(
                            core_item, core_version))
                        found = True
                        break

    if not found:
        print('Unknown file')


def validate_file(str_in_file, str_magic):
    """
    Try to detect ZX... file type from first bytes
    :param str_in_file: Path to file
    :param str_magic: Bytes to match
    :return: True if bytes match, False in other case
    """
    magic_bin = unhexlify(str_magic)
    with open(str_in_file, "rb") as bin_file:
        bin_data = bin_file.read(len(magic_bin))

    if magic_bin == bin_data:
        return True
    else:
        return False


def get_file_hash(str_in_file):
    """
    Get file sha26 hash
    :param str_in_file: Path to file
    :return: String with hash data
    """
    sha256_hash = hashlib.sha256()
    with open(str_in_file, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def savefrom_zxdata(str_in_file,
                    hash_dict,
                    str_outfile,
                    n_cores=-1,
                    video_mode=-1,
                    keyboard_layout=-1,
                    b_force=False):
    """
    Create new file from SPI flash file
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param str_extension: Extension for Core files
    """

    flash_len = 16777216
    if n_cores > -1:
        flash_len = hash_dict['parts']['core_base'][0]
        flash_len += hash_dict['parts']['core_base'][1] * n_cores

    bin_len = os.stat(str_in_file).st_size
    if bin_len > flash_len:
        bin_len = flash_len

    print('Copying Flash...')
    with open(str_in_file, "rb") as in_zxdata:
        bin_data = in_zxdata.read(bin_len)

    # 28746 0-3 Keyboard Layout: Auto-ES-EN-ZX
    if keyboard_layout > -1:
        bin_data = bin_data[:28746] + struct.pack(
            '<B', keyboard_layout) + bin_data[28747:]

    # 28749 0-2 Video: PAL-NTSC-VGA
    if video_mode > -1:
        bin_data = bin_data[:28749] + struct.pack(
            '<B', video_mode) + bin_data[28750:]

    if n_cores > -1:
        core_offset = 0x7100 + (n_cores * 0x20)
        core_len = (MAX_CORES - n_cores) * 0x20
        bin_data = bin_data[:core_offset] + b'\x00' * core_len + bin_data[
            core_offset + core_len:]

        # 28928
        # 28928 + 32
        # 28928-32767 0x00 (cores_dir + 256: len)

    if b_force or check_overwrite(str_outfile):
        with open(str_outfile, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print('{0} created OK.'.format(str_outfile))


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
        while (b_ask):
            chk_overwrite = input(
                '{0} exists. Overwrite? (Y/N): '.format(str_name))
            if chk_overwrite.upper() == 'N' or chk_overwrite == '':
                b_writefile = False
                b_ask = False
            if chk_overwrite.upper() == 'Y':
                b_ask = False

    return b_writefile


if __name__ == "__main__":
    main()
