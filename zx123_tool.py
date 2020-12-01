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

__MY_VERSION__ = '0.5'

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
        fulldict_hash = json.load(jsonHandle)

    str_file = arg_data['input_file']
    str_outdir = arg_data['output_dir']
    if not str_outdir:
        str_outdir = os.path.dirname(str_file)
    str_extension = os.path.splitext(str_file)[1]
    str_extension = str_extension[1:].upper()
    if str_extension in fulldict_hash:
        dict_hash = fulldict_hash[str_extension]
    else:
        LOGGER.error('Unknown file extension {0}'.format(str_extension))
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
    values['roms'] = False
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


def list_romsdata(str_in_file, hash_dict, in_file_ext, show_hashes):
    """
    List ZX Spectrum ROMs of file
    :param str_in_file: Path to file
    :param hash_dict: Dictionary
    :param in_file_ext: File key in dictionary (e.g. ZXD)
    :param show_hashes: If True, print also block hashes
    """
    LOGGER.debug('Listing ROMs of file: {0}'.format(str_in_file))
    str_name = os.path.basename(str_in_file)
    roms_list = get_rom_list(str_in_file, hash_dict[in_file_ext]['parts'])

    if roms_list:
        print('\nZX Spectrum ROMs:')
        for rom in roms_list:
            rom_name = rom[2]
            block_version, block_hash, block_offset = get_rom_version(
                str_in_file, rom[1], rom[3], hash_dict, in_file_ext)
            str_rominfo = ' {0:02d} (Slot {1:02d}) {2:>10} ({3:>16}) '.format(
                rom[0], rom[1], rom[4], rom[5])
            str_rominfo += '"{0}" {1}K -> {2}'.format(rom_name, rom[3] * 16,
                                                      block_version)
            print(str_rominfo)

            if (show_hashes):
                print(block_hash)


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
        if extract_item.lower() == block_name.lower():
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
                core_offset = core_base + core_number * core_len
                block_info = [core_offset, core_len]
                str_bin = 'CORE{0:02d}_{1}_v{2}.{3}'.format(
                    core_number + 2, block_name.replace(' ', '_'),
                    block_version, str_extension)
                str_bin = os.path.join(str_dir, str_bin)
                export_bin(str_in_file, block_info, str_bin, b_force)
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
                        rom_slot = rom[1]
                        rom_name = rom[2]
                        rom_blocks = rom[3]

                        rom_split = hash_dict['parts']['roms_dir'][5]
                        block_bases = hash_dict['parts']['roms_data']
                        rom_data = get_rom_bin(str_in_file, rom_slot,
                                               rom_blocks, rom_split,
                                               block_bases)
                        rom_version, rom_hash = get_romdata_version(
                            rom_data, fullhash_dict['ROM'])
                        if rom_version != 'Unknown':
                            rom_name = rom_version
                        str_bin = '{0:02d}_{1}.rom'.format(rom[0], rom_name)
                        str_bin = os.path.join(str_dir, str_bin)
                        export_bindata(rom_data, str_bin, b_force)
                        break
            else:
                LOGGER.error('Invalid ROM index: {0}'.format(rom_number))


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


def get_rom_version(str_in_file, rom_slot, rom_blocks, dict_full, in_file_ext):
    """
    Obtain name and version from ROM block in file
    :param str_in_file: Path to file
    :param rom_pos: ROM base address in file
    :param rom_pos: ROM slot number
    :param rom_blocks: Size of ROM in 16384 bytes blocks
    :param dict_cores: Dictionary with hashes and info for cores
    :return: List with version string, hash string and offset
    """

    rom_split = dict_full[in_file_ext]['parts']['roms_dir'][5]
    block_bases = dict_full[in_file_ext]['parts']['roms_data']
    rom_data = get_rom_bin(str_in_file, rom_slot, rom_blocks, rom_split,
                           block_bases)

    block_version, block_hash = get_romdata_version(rom_data, dict_full['ROM'])

    return block_version, block_hash, rom_slot


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
            if roms_use[i] != 0xff:
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
                    roms_list.append([
                        i, rom_slot,
                        rom_name.decode('utf-8'), rom_size, rom_flags, rom_crc
                    ])
            else:
                break

    return roms_list


def get_rom_bin(str_in_file, rom_slot, rom_blocks, rom_split, rom_bases):
    """
    Extract ROM data blocks to memory
    :param str_in_file: Path to file
    :param rom_slot: Slot number
    :param rom_blocks: Size of ROM in 16384 bytes blocks
    :param rom_split: Slot number where rom binary data is split in two
    :param rom_bases: Offsets for ROM binary data
    :return: Binary data of ROM
    """

    rom_data = b''
    for rom_block in range(rom_slot, rom_slot + rom_blocks):
        if rom_block < rom_split:
            rom_base = rom_bases[0]
            rom_offset = rom_base + rom_block * 16384
        else:
            rom_base = rom_bases[4]
            rom_offset = rom_base + (rom_block - rom_split) * 16384

        with open(str_in_file, "rb") as in_zxrom:
            in_zxrom.seek(rom_offset)
            rom_data += in_zxrom.read(16384)

    return rom_data


def bit_to_flag(b_input, str_flags):
    """
    Analyze byte and select string chars depending on bits
    :param mybyte: Byte to analyze
    :param mystr: String with chars to use
    :return: String with chars according to bit state
    """
    str_result = ''
    for i in range(8):
        if b_input << i & 128:
            if str_flags[i] != ' ':
                str_result += str_flags[i]
    return str_result


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

    for block_id in ['BIOS', 'Spectrum']:
        if not found and block_id in hash_dict['parts']:
            if validate_file(
                    str_in_file, hash_dict['parts'][block_id][3]) and os.stat(
                    str_in_file).st_size == hash_dict['parts'][block_id][1]:
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
