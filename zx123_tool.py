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

__MY_VERSION__ = '1.0'

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
        fulldict_hash = json.load(jsonHandle)

    str_file = arg_data['input_file']
    str_outdir = arg_data['output_dir']
    if not str_outdir:
        str_outdir = os.path.dirname(str_file)
    str_extension = os.path.splitext(str_file)[1]
    str_extension = str_extension[1:].upper()

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

    if not dict_hash:
        LOGGER.error('Unknown file extension: .{0}'.format(str_extension))
        sys.exit(2)

    if validate_file(str_file, dict_hash['parts']['header'][3]):
        if arg_data['list']:
            list_zxdata(str_file, dict_hash, arg_data['show_hashes'])
            if arg_data['roms']:
                list_romsdata(str_file, fulldict_hash, str_extension,
                              arg_data['show_hashes'])

        for x_item in arg_data['extract']:
            extractfrom_zxdata(str_file, x_item, fulldict_hash, str_outdir,
                               str_extension, arg_data['force'],
                               not arg_data['roms'])

        if arg_data['inject']:
            if str_extension in ['ZX1', 'ZX2', 'ZXD']:
                output_file = arg_data['output_file']
                if not output_file:
                    output_file = str_file
                inject_zxfiles(str_file, arg_data['inject'], output_file,
                               fulldict_hash, str_extension,
                               arg_data['video_mode'],
                               arg_data['keyboard_layout'],
                               arg_data['default_core'],
                               arg_data['default_rom'], arg_data['force'])
            else:
                LOGGER.error(
                    'Not a valid filetype: .{0}'.format(str_extension))
        elif arg_data['output_file']:
            savefrom_zxdata(str_file, dict_hash, arg_data['output_file'],
                            arg_data['n_cores'], arg_data['video_mode'],
                            arg_data['keyboard_layout'],
                            arg_data['default_core'], arg_data['default_rom'],
                            arg_data['force'])
    else:
        find_zxfile(str_file, fulldict_hash, str_extension,
                    arg_data['show_hashes'])

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
    values['roms'] = False
    values['show_hashes'] = False
    values['extract'] = []
    values['n_cores'] = -1
    values['inject'] = []
    values['video_mode'] = -1
    values['keyboard_layout'] = -1
    values['default_core'] = -1
    values['default_rom'] = -1

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
                        action='store',
                        dest='n_cores',
                        help='Number of cores to store on output file')
    parser.add_argument('-a',
                        '--add',
                        required=False,
                        action='append',
                        dest='inject',
                        help='Item to inject')
    parser.add_argument('-c',
                        '--default_core',
                        required=False,
                        action='store',
                        dest='default_core',
                        help='Default core number: 1 and up')
    parser.add_argument('-z',
                        '--default_rom',
                        required=False,
                        action='store',
                        dest='default_rom',
                        help='Default Spectrum ROM index: 0 and up')
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

    if arguments.parse_roms:
        values['roms'] = arguments.parse_roms

    if arguments.show_hashes:
        values['show_hashes'] = arguments.show_hashes

    if arguments.extract:
        values['extract'] = arguments.extract.split(',')

    if arguments.n_cores:
        values['n_cores'] = int(arguments.n_cores)

    if arguments.inject:
        values['inject'] = arguments.inject

    if arguments.default_core:
        values['default_core'] = int(arguments.default_core) - 1

    if arguments.default_rom:
        values['default_rom'] = int(arguments.default_rom)

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

    default_rom = get_peek(str_in_file, 28736)
    print('\tDefault ROM -> {0:02}'.format(default_rom))

    default_core = get_peek(str_in_file, 28737) + 1
    print('\tDefault Core -> {0:02}'.format(default_core))

    keyb_layout = get_peek(str_in_file, 28746)
    print('\tKeyboard Layout -> {0}'.format(keyb_layout))

    video_mode = get_peek(str_in_file, 28749)
    print('\tVideo Mode -> {0}'.format(video_mode))


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
    :param roms_file: If True, add extra offset as in ROM.ZX1 file
    :return: True if there are ROMs to list
    """
    LOGGER.debug('Listing ROMs of file: {0}'.format(str_in_file))
    str_name = os.path.basename(str_in_file)
    roms_list = get_rom_list(str_in_file, hash_dict[in_file_ext]['parts'])

    if roms_list:
        if roms_file:
            print('ZX1 ROMs File')
            default_rom = get_peek(str_in_file, 0x1040)
            print('\tDefault ROM -> {0:02}'.format(default_rom))

        print('\nZX Spectrum ROMs:')
        for rom in roms_list:
            rom_name = rom[2]
            block_version, block_hash, block_data = get_rom(
                str_in_file, rom[1], rom[3], hash_dict, in_file_ext, roms_file)
            str_rominfo = ' {0:02d} (Slot {1:02d}) {2:>10} ({3:>16}) '.format(
                rom[0], rom[1], rom[4], rom[5])
            str_rominfo += '"{0}" {1}K -> {2}'.format(rom_name, rom[3] * 16,
                                                      block_version)
            print(str_rominfo)

            if (show_hashes):
                print(block_hash)

        return True
    else:
        return False


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
    :param hash_dict: Dictionary with hashes for different blocks
    :param str_extension: Extension for Core files
    :param b_force: Force overwriting file
    :param cores: If True, export Core, if False, export ROM
    """
    hash_dict = fullhash_dict[str_extension]

    block_list = ['BIOS', 'esxdos', 'Spectrum']
    for block_name in block_list:
        if extract_item.upper() == block_name.upper():
            print('Extracting {0}...'.format(block_name))
            block_info = hash_dict['parts'][block_name]
            str_bin = hash_dict['parts'][block_name][2]
            str_bin = os.path.join(str_dir, str_bin)
            export_bin(str_in_file, block_info, str_bin, b_force)
            break

    if cores:
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
                splitcore_index = hash_dict['parts']['cores_dir'][4]
                core_bases = hash_dict['parts']['core_base']
                block_data = get_core_blockdata(core_number, splitcore_index,
                                                core_bases)
                str_bin = 'CORE{0:02d}_{1}_v{2}.{3}'.format(
                    core_number + 2, block_name.replace(' ', '_'),
                    block_version, str_extension)
                str_bin = os.path.join(str_dir, str_bin)
                export_bin(str_in_file, block_data, str_bin, b_force)
            else:
                LOGGER.error('Invalid core number: {0}'.format(core_number))
    else:
        if extract_item.isdigit():
            rom_number = int(extract_item)
            rom_list = get_rom_list(str_in_file, hash_dict['parts'])
            if rom_number > -1 and rom_number < len(rom_list):
                print('Extracting ZX Spectrum ROM {0}...'.format(rom_number))
                for rom in rom_list:
                    if rom[0] == rom_number:
                        rom_version, rom_hash, rom_data = get_rom(
                            str_in_file, rom[1], rom[3], fullhash_dict,
                            str_extension)
                        rom_name = rom[2]
                        if rom_version != 'Unknown':
                            rom_name = rom_version
                        str_bin = '{0:02d}_{1}.rom'.format(rom[0], rom_name)
                        str_bin = os.path.join(str_dir, str_bin)
                        export_bindata(rom_data, str_bin, b_force)
                        break
            else:
                LOGGER.error('Invalid ROM index: {0}'.format(rom_number))

    if extract_item.upper() == 'ROMS':
        default_rom = get_peek(str_in_file, 28736).to_bytes(1, 'little')
        rom_dict_parts = fullhash_dict['ROM']['parts']
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

            rom_version, rom_hash, rom_data = get_rom(str_in_file, rom_slt,
                                                      rom_item[3],
                                                      fullhash_dict,
                                                      str_extension)

            roms_data = inject_rom_tobin(roms_data, blk_info, blk_bases,
                                         rom_index, rom_slt, rom_name,
                                         rom_params, rom_data, rom_crc, True)

        str_bin = 'ROMS.ZX1'
        str_bin = os.path.join(str_dir, str_bin)
        export_bindata(roms_data, str_bin, b_force)


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

    str_version = get_data_version(str_hash, hash_dict)

    return str_version, str_hash


def get_data_version(str_hash, hash_dict):
    """
    Obtain version string from hash
    :param str_hash: Hash string to check
    :param hash_dict: Dictionary with hashes for different blocks
    :return: List with version string and hash string
    """
    str_version = 'Unknown'
    for hash_elem in hash_dict:
        if str_hash == hash_dict[hash_elem]:
            str_version = hash_elem
            break

    return str_version


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
    max_cores = splitcore_index = block_info[4]

    if len(block_info) > 5:
        max_cores += block_info[5]

    if core_index > max_cores:
        LOGGER.error('Invalid core index: {}'.format(core_index))

    core_bases = dict_parts['core_base']

    block_name = block_version = 'Unknown'
    block_hash = ''
    for core_name in dict_cores:
        block_data = get_core_blockdata(core_index, splitcore_index,
                                        core_bases)
        block_version, block_hash = get_version(str_in_file, block_data,
                                                dict_cores[core_name])
        if block_version != 'Unknown':
            block_name = core_name
            break

    return block_name, block_version, block_hash


def get_core_blockdata(core_index, splitcore_index, core_bases):
    """
    Get Core Offset and Length
    :param core_index: Index of the Core
    :param splitcore_index: Index of last core before split
    :param core_bases: Array with base offset and offset after split
    :return: Array with core offset and core length
    """

    core_base = core_bases[0]
    core_len = core_bases[1]

    core_split = 0
    if len(core_bases) > 4:
        core_split = core_bases[4]

    core_offset = core_base + core_index * core_len
    if core_split and core_index > splitcore_index:
        core_offset = core_split + (core_index - splitcore_index -
                                    1) * core_len

    return [core_offset, core_len]


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

    rom_split = dict_full[in_file_ext]['parts']['roms_dir'][5]
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
    max_cores = block_info[4]
    if len(block_info) > 5:
        max_cores += block_info[5]

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


def get_rom_list(str_in_file, dict_parts):
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
        with open(str_in_file, "rb") as in_zxdata:
            in_zxdata.seek(block_info[4])
            roms_use = in_zxdata.read(block_info[5] + block_info[6])

        for i in range(0, len(roms_use)):
            if roms_use[i] == i:
                with open(str_in_file, "rb") as in_zxdata:
                    in_zxdata.seek(block_info[0] + i * 64)
                    rom_data = in_zxdata.read(64)
                    rom_slot = rom_data[0]
                    rom_size = rom_data[1]
                    rom_flags = bit_to_flag(rom_data[2] ^ 0b00110000,
                                            '* icdnpt')
                    rom_flags += bit_to_flag(rom_data[3] ^ 0b00000000,
                                             'smhl172a')
                    rom_flags += bit_to_flag(rom_data[4] ^ 0b00000000,
                                             '     rxu')
                    rom_crc = ''
                    for j in range(0, 16):
                        byte = rom_data[8 + j]
                        if byte:
                            rom_crc += '{0:02X}'.format(byte)
                    rom_name = rom_data[32:]
                    try:
                        roms_list.append([
                            i, rom_slot,
                            rom_name.decode('utf-8'), rom_size, rom_flags,
                            rom_crc
                        ])
                    except UnicodeDecodeError:
                        LOGGER.debug('Not a ROM entry or corrupted ROM name')
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
        rom_base = rom_bases[0]
        rom_offset = rom_base + rom_slot * 16384
    else:
        rom_base = rom_bases[4]
        rom_offset = rom_base + (rom_slot - rom_split) * 16384

    if roms_file:
        rom_offset += 1

    return rom_offset


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

    str_result = ''
    i_result = 0
    for i in range(8):
        if str_flags[7 - i] in str_input:
            i_result += 1 << i

    i_result ^= i_mask
    b_result = (i_result).to_bytes(1, 'little')
    return b_result


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

    export_bindata(bin_data, str_out_bin, b_force)


def export_bindata(bin_data, str_out_bin, b_force=False):
    """
    Extract binary data to file
    :param bin_data: Binary data
    :param str_out_bin: Path to bin file to create
    """
    if b_force or check_overwrite(str_out_bin):
        with open(str_out_bin, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print('{0} created OK.'.format(str_out_bin))


def find_zxfile(str_in_file, fulldict_hash, str_extension, show_hashes):
    """
    Try to guess ZX... file from hash
    :param str_in_file: Path to file
    :param hash_dict: Dictionary with hashes for different blocks
    :param show_hashes: If True, print also found block hashes
    """
    found = False
    hash_dict = fulldict_hash[str_extension]

    str_name = os.path.basename(str_in_file)
    print('\nAnalyzing {0} (possibly {1})...\n '.format(
        str_name, hash_dict['description']))
    str_file_hash = get_file_hash(str_in_file)
    if show_hashes:
        print('{0}'.format(str_file_hash))

    for block_id in [
            '16K Spectrum ROM', '32K Spectrum ROM', '64K Spectrum ROM'
    ]:
        if block_id in hash_dict['parts']:
            if os.stat(str_in_file).st_size == hash_dict['parts'][block_id][1]:
                LOGGER.debug('Looks like {0}'.format(block_id))
                block_version = get_data_version(str_file_hash,
                                                 hash_dict[block_id])
                if block_version != 'Unknown':
                    print('{0} -  Version: {1}'.format(block_id,
                                                       block_version))
                    found = True

    for block_id in ['BIOS', 'Spectrum', 'esxdos']:
        if not found and block_id in hash_dict['parts']:
            if os.stat(str_in_file).st_size == hash_dict['parts'][
                    block_id][1] and validate_file(
                        str_in_file, hash_dict['parts'][block_id][3]):
                LOGGER.debug('Looks like {0}'.format(block_id))
                block_version = get_data_version(str_file_hash,
                                                 hash_dict[block_id])
                if block_version != 'Unknown':
                    print('{0} -  Version: {1}'.format(block_id,
                                                       block_version))
                    found = True

    if not found and 'core_base' in hash_dict['parts']:
        if validate_file(
                str_in_file, hash_dict['parts']['core_base'][3]) and os.stat(
                    str_in_file).st_size == hash_dict['parts']['core_base'][1]:
            LOGGER.debug('Looks like a core')
            for core_item in hash_dict['Cores']:
                block_version = get_data_version(str_file_hash,
                                                 hash_dict['Cores'][core_item])
                if block_version != 'Unknown':
                    print('Core: {0} - Version: {1}'.format(
                        core_item, block_version))
                    found = True
                    break

    if not found and str_extension == 'ZX1':
        found = list_romsdata(str_in_file, fulldict_hash, 'ROM', show_hashes,
                              True)

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
    if magic_bin:
        with open(str_in_file, "rb") as bin_file:
            bin_data = bin_file.read(len(magic_bin))

        if magic_bin == bin_data:
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
    with open(str_in_file, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


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
        str_crc = '{0:04X}'.format(block_crc) + str_crc

    return str_crc


def get_crc16(data: bytearray, offset, length):
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
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def inject_zxfiles(str_spi_file,
                   arr_in_files,
                   str_outfile,
                   fullhash_dict,
                   str_extension,
                   video_mode=-1,
                   keyboard_layout=-1,
                   default_core=-1,
                   default_rom=-1,
                   b_force=False):
    """
    Add binary from one or more binary files to SPI flash file
    :param str_spi_file: Input SPI flash file
    :param arr_in_files: Array with parameters and files to inject
    :param str_outfile: New SPI flash file to create
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param video_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyboard_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :param b_force: Force overwriting file
    """
    hash_dict = fullhash_dict[str_extension]

    LOGGER.debug('Reading Flash...')
    b_len = os.stat(str_spi_file).st_size
    with open(str_spi_file, "rb") as in_zxdata:
        b_data = in_zxdata.read(b_len)

    for str_in_params in arr_in_files:
        b_data = inject_bindata(str_in_params, hash_dict, b_data)
        b_data = inject_coredata(str_in_params, hash_dict, b_data)
        b_data = inject_romdata(str_spi_file, str_in_params, fullhash_dict,
                                str_extension, b_data)
        b_data = inject_romszx1data(str_in_params, fullhash_dict,
                                    str_extension, b_data)

    b_data = inject_biossettings(b_data, video_mode, keyboard_layout,
                                 default_core, default_rom)

    if b_force or check_overwrite(str_outfile):
        with open(str_outfile, "wb") as out_zxdata:
            out_zxdata.write(b_data)
            print('{0} created OK.'.format(str_outfile))


def savefrom_zxdata(str_in_file,
                    hash_dict,
                    str_outfile,
                    n_cores=-1,
                    video_mode=-1,
                    keyboard_layout=-1,
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
    :param default_core: Default boot core (0 and up)
    :param default_rom: :Default boot Spectrum ROM (0 or greater)
    :param b_force: Force overwriting file
    """

    dict_parts = hash_dict['parts']
    block_info = dict_parts['cores_dir']
    max_cores = splitcore_index = block_info[4]

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

    bin_data = inject_biossettings(bin_data, video_mode, keyboard_layout,
                                   default_core, default_rom)

    if n_cores > -1:
        core_offset = 0x7100 + (n_cores * 0x20)
        core_len = (max_cores - n_cores) * 0x20
        bin_data = bin_data[:core_offset] + b'\x00' * core_len + bin_data[
            core_offset + core_len:]

    if b_force or check_overwrite(str_outfile):
        with open(str_outfile, "wb") as out_zxdata:
            out_zxdata.write(bin_data)
            print('{0} created OK.'.format(str_outfile))


def inject_bindata(str_in_params, hash_dict, b_data):
    """
    Add binary from one ROM binary file to SPI flash data
    :param str_in_params: String with one of BIOS, esxdos or Spectrum and,
     separated with ',', file path to the binary file
    :param hash_dict: Dictionary with hashes for different blocks
    :param b_data: SPI flash data
    :return: Altered binary data
    """
    arr_params = str_in_params.split(',')
    br_data = b_data

    for bl_id in ['BIOS', 'esxdos', 'Spectrum']:
        hash_parts = hash_dict['parts'][bl_id]
        if arr_params[0].upper() == bl_id.upper():
            if len(arr_params) != 2:  # Filename
                LOGGER.error('Invalid data: {0}'.format(str_in_params))
            else:
                str_in_file = arr_params[1]
                str_hash = get_file_hash(str_in_file)
                b_offset = hash_parts[0]
                b_len = hash_parts[1]
                b_head = hash_parts[3]
                if validate_file(
                        str_in_file,
                        b_head) and os.stat(str_in_file).st_size == b_len:
                    LOGGER.debug('Looks like {0}'.format(bl_id))
                    bl_version = get_data_version(str_hash, hash_dict[bl_id])
                    print('Adding {0}: {1}...'.format(bl_id, bl_version))

                    with open(str_in_file, "rb") as in_zxdata:
                        in_data = in_zxdata.read(b_len)

                    br_data = b_data[:b_offset] + in_data
                    br_data += b_data[b_offset + b_len:]

    return br_data


def inject_coredata(str_in_params, hash_dict, b_data):
    """
    Add binary from one core binary file to SPI flash data
    :param str_in_params: String with CORE, and, separated with ',': core
     number, core name and file path to the core file
    :param hash_dict: Dictionary with hashes for different blocks
    :param b_data: SPI flash data
    :return: Altered binary data
    """
    dict_parts = hash_dict['parts']

    arr_params = str_in_params.split(',')
    br_data = b_data

    block_info = dict_parts['cores_dir']
    max_cores = splitcore_index = block_info[4]
    if len(block_info) > 5:
        max_cores += block_info[5]
    core_bases = dict_parts['core_base']
    b_len = core_bases[1]
    b_head = core_bases[3]

    bl_data = b_data[block_info[0]:block_info[0] + block_info[1]]
    core_list = get_core_list_bindata(bl_data, dict_parts)

    if arr_params[0].upper() == 'CORE':  # Number, Name, Filename
        if len(arr_params) != 4:
            LOGGER.error('Invalid argument: {0}'.format(str_in_params))
        else:
            core_index = int(arr_params[1]) - 2
            str_name = '{0:<32}'.format(arr_params[2][:32])
            str_in_file = arr_params[3]
            str_hash = get_file_hash(str_in_file)
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

                if core_index - 1 > len(core_list):
                    core_index = len(core_list)

                if core_index < 0 or core_index > max_cores:
                    LOGGER.error('Invalid core index: {}'.format(core_index))
                else:
                    print('Adding core {0}: {1}({2})...'.format(
                        core_index + 2, core_name, block_version))
                    block_data = get_core_blockdata(core_index,
                                                    splitcore_index,
                                                    core_bases)
                    core_index = 0x100 + core_index * 32
                    bl_data = bl_data[:core_index] + bytes(
                        str_name, 'utf-8') + bl_data[core_index + 32:]

                    br_data = b_data[:block_info[0]] + bl_data
                    br_data += b_data[block_info[0] + block_info[1]:]

                    with open(str_in_file, "rb") as in_zxdata:
                        in_data = in_zxdata.read()

                    b_offset, b_len = block_data
                    br_data = br_data[:b_offset] + in_data
                    br_data += b_data[b_offset + b_len:]

    return br_data


def inject_romdata(str_in_file, str_in_params, fullhash_dict, str_extension,
                   b_data):
    """
    Add binary from one Spectrum ROM binary file to SPI flash data
    :param str_in_file: File with SPI flash data
    :param str_in_params: String with ROM, and, separated with ',': ROM slot
     number, ROM params (icdnptsmhl172arxu), ROM name to use and file path to
     the ROM file
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param b_data: SPI flash data obtained from str_in_file
    :return: Altered binary data
    """
    hash_dict = fullhash_dict[str_extension]
    dict_parts = hash_dict['parts']

    arr_params = str_in_params.split(',')
    br_data = b_data

    block_info = dict_parts['roms_dir']
    max_slots = block_info[5]
    max_slots += block_info[6]
    block_bases = dict_parts['roms_data']

    roms_list = get_rom_list(str_in_file, dict_parts)
    slot_use = []
    for rom_entry in roms_list:
        i_slot = rom_entry[1] + 1
        for i in range(1, rom_entry[3]):
            slot_use.append(i_slot)
            i_slot += 1

    if arr_params[0].upper() == 'ROM':  # Slot, Params, Name, Filename
        if len(arr_params) != 5:
            LOGGER.error('Invalid argument: {0}'.format(str_in_params))
        else:
            rom_slt = int(arr_params[1])
            rom_params = arr_params[2]
            str_name = arr_params[3]
            str_in_file = arr_params[4]

            b_len = os.stat(str_in_file).st_size
            if b_len != 0 and b_len % 16384 == 0:
                LOGGER.debug('Looks like a ROM')
                b_len = int(b_len / 16384)

                if rom_slt in slot_use or rom_slt < 0 or rom_slt > max_slots:
                    LOGGER.error('Invalid slot number: {0}'.format(rom_slt))
                    rom_slt = -1

                if rom_slt + b_len >= max_slots:
                    LOGGER.error('Slot number too high ({slot 0})'.format(rom_slt))
                    rom_slt = -1

                rom_index = len(roms_list)
                for rom_entry in roms_list:
                    if rom_slt == rom_entry[1]:
                        rom_index = rom_entry[0]
                        if b_len != rom_entry[3]:
                            LOGGER.error(
                                'Invalid ROM size for slot {0}'.format(
                                    rom_slt))
                            rom_slt = -1
                        break

                if rom_slt > -1:
                    with open(str_in_file, "rb") as in_zxdata:
                        rom_data = in_zxdata.read()

                    r_v = get_romdata_version(rom_data, fullhash_dict['ROM'])
                    print('Injecting ROM {0} ({1})...'.format(rom_slt, r_v[0]))

                    br_data = inject_rom_tobin(b_data, block_info, block_bases,
                                               rom_index, rom_slt, str_name,
                                               rom_params, rom_data)

    return br_data


def inject_romszx1data(str_in_params, fullhash_dict, str_extension, b_data):
    """
    Add ROMs from a Spectrum ROMS.ZX1 binary file to SPI flash data
    :param str_in_file: File with SPI flash data
    :param str_in_params: String with ROMS, and, separated with ',': file path
     to ROMS.ZX1
    :param fullhash_dict: Dictionary with hashes data
    :param str_extension: SPI Flash extension
    :param b_data: SPI flash data obtained from str_in_file
    :return: Altered binary data
    """

    # SPI flash ROMs
    hash_dict = fullhash_dict[str_extension]
    dict_parts = hash_dict['parts']
    block_info = dict_parts['roms_dir']
    max_slots = block_info[5]
    max_slots += block_info[6]
    block_bases = dict_parts['roms_data']

    # Empty ROMs list
    roms_use = b'\xff' * (block_info[5] + block_info[6])

    # ZX1 ROMS
    rom_dict_parts = fullhash_dict['ROM']['parts']
    blk_info = rom_dict_parts['roms_dir']
    rm_split = blk_info[5]
    blk_bases = rom_dict_parts['roms_data']

    arr_params = str_in_params.split(',')
    br_data = b_data

    if arr_params[0].upper() == 'ROMS':  # Filename
        if len(arr_params) != 2:
            LOGGER.error('Invalid argument: {0}'.format(str_in_params))
        else:
            str_name = arr_params[1]
            roms_list = get_rom_list(str_name, rom_dict_parts)

            if roms_list:
                def_rom = get_peek(str_name, 4160)
                # Clear ROMs list in SPI flash (Temp Binary Data)
                br_data = b_data[:block_info[4]] + roms_use
                br_data += b_data[block_info[4] + len(roms_use):]

                print('Injecting ROMs from {0}...'.format(str_name))
                for rom_item in roms_list:
                    rom_index = rom_item[0]
                    rom_slt = rom_item[1]
                    rom_name = rom_item[2]
                    rom_params = rom_item[4]
                    rom_crc = rom_item[5]

                    rom_data = get_rom_bin(str_name, rom_item[1], rom_item[3],
                                           rm_split, blk_bases, True)

                    rom_len = int(len(rom_data) / 16384)
                    if rom_slt + rom_len < max_slots:
                        LOGGER.debug('Injecting ROM {0} ({1})...'.format(
                            rom_slt, rom_name))

                        br_data = inject_rom_tobin(br_data, block_info,
                                                   block_bases, rom_index,
                                                   rom_slt, rom_name,
                                                   rom_params, rom_data,
                                                   rom_crc, False)
                    else:
                        LOGGER.error(
                            'Slot number too high: {0}'.format(rom_slt))

                br_data = inject_biossettings(br_data, default_rom=def_rom)

    return br_data


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
    :return: Altered binary file data
    """
    rom_split = block_info[5]

    rom_name = '{0:<32}'.format(rom_name[:32])
    rom_len = int(len(rom_data) / 16384)
    if not rom_crc:
        rom_crc = get_rom_crc(rom_data)
    rom_entry = new_romentry(rom_slt, rom_name, rom_len, rom_params, rom_crc)

    # Inject ROM entry
    cur_pos = block_info[0] + rom_index * 64
    br_data = b_data[:cur_pos]
    br_data += rom_entry
    cur_pos += 64

    # Inject ROM index
    br_data += b_data[cur_pos:block_info[4]]
    cur_pos = block_info[4]
    br_data += b_data[cur_pos:cur_pos + rom_index]
    br_data += (rom_index).to_bytes(1, byteorder='little')
    cur_pos += rom_index + 1

    # Inject ROM binary data
    for i in range(rom_len):
        rom_offset = get_romb_offset(rom_slt + i, rom_split, block_bases,
                                     roms_file)
        if rom_offset > cur_pos:
            br_data += b_data[cur_pos:rom_offset]
        br_data += rom_data[i * 16384:(i + 1) * 16384]
        cur_pos = rom_offset + 16384

    br_data += b_data[cur_pos:]

    return br_data


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


def inject_biossettings(b_data,
                        video_mode=-1,
                        keyboard_layout=-1,
                        default_core=-1,
                        default_rom=-1):
    """
    Alter SPI flash BIOS settings
    :param b_data: Binary data to modify
    :param video_mode: Video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
    :param keyboard_layout: 0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
    :return: Altered SPI flash data
    """
    br_data = b_data

    # 28736 Default ROM: 00-xx
    if default_rom > -1:
        br_data = br_data[:28736] + struct.pack('<B',
                                                default_rom) + br_data[28737:]

    # 28737 Default Core: 01-xx
    if default_core > -1:
        br_data = br_data[:28737] + struct.pack('<B',
                                                default_core) + br_data[28738:]

    # 28746 0-3 Keyboard Layout: Auto-ES-EN-ZX
    if keyboard_layout > -1:
        br_data = br_data[:28746] + struct.pack(
            '<B', keyboard_layout) + br_data[28747:]

    # 28749 0-2 Video: PAL-NTSC-VGA
    if video_mode > -1:
        br_data = br_data[:28749] + struct.pack('<B',
                                                video_mode) + br_data[28750:]

    return br_data


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
