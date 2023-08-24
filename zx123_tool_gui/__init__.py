#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
# pylint: disable=import-outside-toplevel
"""
Copyright (c) 2021-2023, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

ZX123 Tool GUI Classes
    Creation Methods defined in ._main_gui
    Extra Windows defined in ._extra_gui
"""

from __future__ import annotations
from typing import Any, Optional
import os
import sys
import json
from shutil import copy
import ssl
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import zx123_tool as zx123
from ._extra_gui import NewEntryDialog, InfoWindow, ROMPWindow
from ._extra_gui import ProgressWindow, PrefWindow
if sys.version_info.major == 3:
    import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=protected-access

MY_BASEPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_BASEPATH)
JSON_DIR = APP_RESDIR = MY_DIRPATH


class App(tk.Tk):
    """Main GUI"""

    from ._main_gui import build_menubar
    from ._main_gui import bind_keys
    from ._main_gui import core_menu_popup
    from ._main_gui import rom_menu_popup
    from ._main_gui import json_menu_popup
    from ._main_gui import create_labels
    from ._main_gui import create_entries
    from ._main_gui import create_core_table, create_rom_table
    from ._main_gui import create_buttons
    from ._main_gui import populate_cores, populate_roms
    from ._main_gui import changed_bios_spinbox
    from ._main_gui import changed_core_spinbox
    from ._main_gui import changed_timer_spinbox
    from ._main_gui import changed_keyboard_spinbox
    from ._main_gui import changed_video_spinbox
    from ._main_gui import changed_rom_spinbox
    from ._main_gui import process_selected
    from ._main_gui import coretable_selected
    from ._main_gui import romtable_selected

    def __init__(self: Any):
        super().__init__()

        self.pref_window = None
        if sys.platform == 'win32':
            # Windows config
            str_icon_path: str = os.path.join(MY_DIRPATH, 'ZX123 Tool.ico')
            self.iconbitmap(str_icon_path)
        elif sys.platform == 'darwin':
            # MacOS Open File Events
            self.createcommand('::tk::mac::OpenDocument', self.open_files)
            self.createcommand('::tk::mac::ShowPreferences', self.open_prefs)
            self.createcommand('::tk::mac::Quit', self.do_close)
        else:
            # Other
            pass

        if sys.version_info < (3, 8, 0):
            str_error: str = 'ERROR\n'
            str_error += 'This software requires at least Python version 3.8'
            messagebox.showerror('Error', str_error, parent=self)
            self.destroy()
            return

        self.dict_prefs: dict[str, bool | tuple[int, int]] = {}
        self.fulldict_hash: dict[str, Any] = {}
        self.zxfilepath: str = ''
        self.zxextension: str = ''
        self.zxsize: int = 0
        self.old_core: int = 0
        self.old_timer: int = 0
        self.old_keyboard: int = 0
        self.old_video: int = 0
        self.old_rom: int = 0

        self.load_json()
        self.load_prefs()

        # Main Window
        self.title('ZX123 Tool')
        self.protocol("WM_DELETE_WINDOW", self.do_close)
        self.resizable(False, False)

        self.main_frame = ttk.Frame(self, padding=5)
        self.main_frame.pack(fill='both')
        self.blocks_frame = ttk.Frame(self.main_frame, padding=5)
        self.blocks_frame.pack()
        self.cores_frame = ttk.Frame(self.main_frame, padding=5)
        self.cores_frame.pack()
        self.roms_frame = ttk.Frame(self.main_frame, padding=5)
        self.roms_frame.pack()

        self.image_label, self.version_label = self.create_labels()
        self.create_entries()
        self.core_table = self.create_core_table()
        self.rom_table = self.create_rom_table()
        self.create_buttons()

        # Menu
        self.build_menubar()
        self.bind("<FocusIn>", self.bind_keys)

        # Update JSON on startup
        if self.dict_prefs.get('update_json', False):
            self.update_json()

        # Check for updates on startup
        if self.dict_prefs.get('check_updates', False):
            self.check_updates()

        self.update_idletasks()
        if self.dict_prefs.get('remember_pos', False):
            height, width = self.winfo_height(), self.winfo_width()
            x_pos, y_pos = self.dict_prefs.get(
                'mainwindow', (self.winfo_x(), self.winfo_y()))
            self.geometry(f'{width}x{height}+{x_pos}+{y_pos}')
        else:
            self.tk.eval(f'tk::PlaceWindow {self._w} center')

        # Load files from command line args
        if len(sys.argv) > 1:
            self.open_file(sys.argv[1:])

    def do_close(self: Any, *_: Any):
        """Destroy Event"""
        self.dict_prefs['mainwindow'] = (self.winfo_x(), self.winfo_y())
        self.save_prefs()
        self.destroy()

    def check_updates(self: Any, confirm: bool = False):
        """Gets the latest release version from GitHub"""
        print("Checking for updates...")
        result: Any = urllib.request.urlopen(
            'https://github.com/kounch/zx123_tool/releases/latest')
        new_version: str = result.url.split('/')[-1]
        old_version: str = zx123.__MY_VERSION__
        if new_version > old_version:
            str_msg: str = f'There\'s a new version ({new_version}) of'
            str_msg += ' ZX123 Tool available to download.'
            messagebox.showinfo('Update available', str_msg, parent=self)
        elif confirm:
            str_msg = 'This is the latest version of ZX123 Tool.'
            messagebox.showinfo('No update available', str_msg, parent=self)

    def load_prefs(self: Any, restore: bool = False):
        """Load preferences from file if found, or set default settings"""
        dict_prefs: dict[str, bool | tuple[int, int]] = {
            'update_json': False,
            'check_updates': False,
            'ask_insert': False,
            'ask_replace': True,
            'import_unknown': False,
            'import_allroms': False,
            'remember_pos': False
        }
        str_prefs: str = os.path.join(JSON_DIR, 'zx123_prefs.json')

        if restore:
            self.dict_prefs = dict_prefs
            self.save_prefs()
        else:
            if os.path.isfile(str_prefs):
                with open(str_prefs, 'r', encoding='utf-8') as prefs_handle:
                    dict_load = json.load(prefs_handle)
                for key in dict_load:
                    dict_prefs[key] = dict_load[key]

        self.dict_prefs = dict_prefs

    def save_prefs(self: Any):
        """Save preferences to file"""
        str_prefs: str = os.path.join(JSON_DIR, 'zx123_prefs.json')
        with open(str_prefs, 'w', encoding='utf-8') as prefs_handle:
            json.dump(self.dict_prefs, prefs_handle)

    def open_prefs(self: Any):
        """Show or set focus to preferences window"""
        if self.pref_window:
            self.pref_window.top.focus_force()
        else:
            self.pref_window = PrefWindow(self)

    def load_json(self: Any):
        """Initialize JSON Database"""

        fulldict_hash: dict[str, Any] = zx123.load_json_bd(base_dir=JSON_DIR)
        if os.path.isdir(APP_RESDIR):
            tmp_hash: dict[str, Any] = zx123.load_json_bd(base_dir=APP_RESDIR)
            if 'version' in tmp_hash:
                old_version: str = '20211201.001'
                my_version: str = tmp_hash['version']
                if 'version' in fulldict_hash:
                    old_version = fulldict_hash['version']
                if old_version < my_version:
                    print('Updating database file...')
                    copy(os.path.join(APP_RESDIR, 'zx123_hash.json'), JSON_DIR)

        fulldict_hash = zx123.load_json_bd(base_dir=JSON_DIR)
        self.fulldict_hash = fulldict_hash

    def update_json(self: Any):
        """Update JSON Database and show in GUI"""
        fulldict_hash: dict[str, Any] = zx123.load_json_bd(base_dir=JSON_DIR,
                                                           str_update='json')
        if 'version' in fulldict_hash:
            str_text: str = f'Database: {fulldict_hash["version"]}'
            self.version_label.config(text=str_text)

        self.fulldict_hash = fulldict_hash

    def new_image(self: Any):
        """Create a new image file from one of the included templates"""
        filetypes: list[tuple[str, str]] = [('ZX1 Flash Image', '.zx1'),
                                            ('ZXDOS Flash Image', '.zx2'),
                                            ('ZXDOS+ Flash Image', '.zxd'),
                                            ('ZXTRES Flash Image', '.zx3')]
        str_file: str = fd.asksaveasfilename(parent=self,
                                             title='New file to create',
                                             filetypes=filetypes)
        if str_file:
            _, str_err = zx123.unzip_image(JSON_DIR, str_file,
                                           self.fulldict_hash, True)
            if str_err:
                str_error: str = 'ERROR\nCannot create new image file.\n'
                str_error += f'{str_err}\n'
                messagebox.showerror('Error', str_error, parent=self)
            else:
                self.open_file(str_file)

    def erase_image(self: Any):
        """Wipes a Flash Image File, removing all cores and ROMs"""
        str_filename: str = os.path.split(self.zxfilepath)[1]

        str_title: str = f'Erase {str_filename}'
        str_message: str = f'Do you really want to erase {str_filename}?'
        response: bool = messagebox.askyesno(parent=self,
                                             icon='question',
                                             title=str_title,
                                             message=str_message)
        if response:
            zx123.wipe_zxdata(self.zxfilepath,
                              self.zxfilepath,
                              self.fulldict_hash[self.zxkind],
                              b_force=True)
            self.open_file(self.zxfilepath)

    def expand_image(self: Any):
        """Expands a ZXD 16MB flash image to 32MB"""
        str_filename: str = os.path.split(self.zxfilepath)[1]
        str_outdir: str = os.path.split(self.zxfilepath)[0]

        str_title: str = f'Erase {str_filename}'
        str_message: str = f'Do you really want to expand {str_filename}?'
        response: bool = messagebox.askyesno(parent=self,
                                             icon='question',
                                             title=str_title,
                                             message=str_message)
        if response:
            print(f'Expand {self.zxfilepath}')
            img_len: int = 33554432
            zx123.expand_image(self.zxfilepath, self.zxfilepath, img_len, True)
            zx123.update_image(self.zxfilepath, self.zxfilepath,
                               self.fulldict_hash, self.zxextension,
                               str_outdir, 'special', False, True, False,
                               False)
            self.open_file(self.zxfilepath)

    def truncate_image(self: Any):
        """Truncates a flash image to the minimum (latest core)"""
        str_filename: str = os.path.split(self.zxfilepath)[1]

        str_title: str = f'Truncate {str_filename}'
        str_message: str = f'Do you really want to truncate {str_filename}?'
        response: bool = messagebox.askyesno(parent=self,
                                             icon='question',
                                             title=str_title,
                                             message=str_message)
        if response:
            str_outfile: str = ''
            filetypes: list[tuple[str, str]] = [(f'{self.zxextension} file',
                                                 f'.{self.zxextension}')]
            str_outfile = fd.asksaveasfilename(parent=self,
                                                    title='New file to create',
                                                    filetypes=filetypes)
            if str_outfile:
                print(f'Truncate {self.zxfilepath}')
                zx123.truncate_image(self.zxfilepath, str_outfile,
                                     self.fulldict_hash[self.zxkind], True)

            self.open_file(self.zxfilepath)

    def full_close_image(self: Any):
        """Restore button text and empty all fields of Main Window """
        self.core_import_button['text'] = 'Add New Core'
        self.core_export_button['text'] = 'Export Core'
        self.rom_import_button['text'] = 'Add New ROM'
        self.rom_export_button['text'] = 'Export ROM'
        self.close_image()

    def close_image(self: Any):
        """Empty all fields of Main Window"""

        self.zxfilepath: str = ''

        self.filemenu.entryconfig(2, state='disabled', label='Close file')
        self.filemenu.entryconfig(4, state='disabled')
        self.filemenu.entryconfig(5, state='disabled')
        self.filemenu.entryconfig(6, state='disabled')
        self.filemenu.entryconfig(7, state='disabled')
        self.filemenu.entryconfig(9, state='disabled', label='Show info')
        self.filemenu.entryconfig(10, state='disabled', label='Rename')
        self.core_menu.entryconfig(0, state='disabled', label='Show info')
        self.core_menu.entryconfig(1, state='disabled', label='Rename')
        self.rom_menu.entryconfig(0, state='disabled', label='Rename')

        self.image_label.config(text='No Image')
        self.bios.set('')
        self.esxdos.set('')
        self.spectrum.set('')
        self.default_core.set('')
        self.default_timer.set('')
        self.default_keyboard.set('')
        self.default_video.set('')
        self.default_rom.set('')
        self.core_table.delete(*self.core_table.get_children())
        self.rom_table.delete(*self.rom_table.get_children())

        self.bios_import_button.state(['disabled'])
        self.bios_export_button.state(['disabled'])
        self.esxdos_import_button.state(['disabled'])
        self.esxdos_export_button.state(['disabled'])
        self.spectrum_import_button.state(['disabled'])
        self.spectrum_export_button.state(['disabled'])
        self.core_import_button.state(['disabled'])
        self.core_export_button.state(['disabled'])
        self.rom_import_button.state(['disabled'])
        self.rom_export_button.state(['disabled'])
        self.rompack_import_button.state(['disabled'])
        self.rompack_export_button.state(['disabled'])
        self.core_spinbox.state(['disabled'])
        self.timer_spinbox.state(['disabled'])
        self.keyboard_spinbox.state(['disabled'])
        self.video_spinbox.state(['disabled'])
        self.rom_spinbox.state(['disabled'])

    def update_image(self: Any,
                     str_update: str,
                     get_1core: bool = False,
                     get_2mb: bool = False):
        """
        Tries to update BIOS and or Core(s) of image file
        :param str_update: Description of the update ("all", "bios", etc.)
        :param get_1core: Use "1core" entries of JSON
        :param get_2mb: Use "2m" entries of JSON
        """
        str_title: str = f'Update {str_update}'
        str_message: str = f'Are you sure that you want to update {str_update}?'
        response: bool = messagebox.askyesno(parent=self,
                                             icon='question',
                                             title=str_title,
                                             message=str_message)
        if response:
            w_progress: Any = ProgressWindow(self, f'Update {str_update}')
            w_progress.show()
            str_outdir: str = os.path.split(self.zxfilepath)[0]
            zx123.update_image(self.zxfilepath, self.zxfilepath,
                               self.fulldict_hash, self.zxextension,
                               str_outdir, str_update, False, True, get_1core,
                               get_2mb, w_progress)
            self.open_file(self.zxfilepath)
            w_progress.close()

    def open_files(self: Any, *args: list[Any]):
        """Open several files"""
        for arg in args:
            if isinstance(arg, str):
                self.open_file(arg)

    def open_file(self: Any, *args: list[Any]):
        """
        Open the first file received. If there's no file, ask for it
        :param args: Array of file paths. Only the first element is analyzed
        """

        # Disable File Menu
        self.menubar.entryconfig(0, state='disabled')

        if args:
            str_file: Any = args[0]
        else:
            filetypes: list[tuple[str,
                                  str]] = [('ZX1, ZX2, ZXD, ZX3 or ROM files',
                                            '.zx1 .zx2 .zxd .zx3 .rom .bin')]
            str_file = fd.askopenfilename(parent=self,
                                          title='Select a file to open',
                                          filetypes=filetypes)

        if isinstance(str_file, str):  # To avoid MacOS quarantine events
            str_filename: str = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype, str_kind = zx123.detect_file(
                str_file, self.fulldict_hash)

            if filetype == 'FlashImage':
                self.full_close_image()
                self.zxfilepath = str_file
                self.zxextension = str_extension
                self.zxkind = str_kind
                self.zxsize = os.stat(str_file).st_size

                dict_flash: dict[str, Any] = zx123.list_zxdata(
                    str_file, dict_hash, False)
                dict_roms, _ = zx123.list_romsdata(str_file,
                                                   self.fulldict_hash,
                                                   str_kind, False)
                str_filename = f'{str_filename} ({dict_flash["description"]})'
                str_filename += f' {int(self.zxsize / 1048576)}MB'

                self.filemenu.entryconfig(2,
                                          state='normal',
                                          label='Close image file')
                self.filemenu.entryconfig(4, state='normal')
                if self.zxsize < 33554432 and self.zxextension == 'ZXD':
                    self.filemenu.entryconfig(5, state='normal')

                if self.zxextension == 'ZX1':
                    str_update: str = 'normal'
                else:
                    str_update = 'disabled'
                self.updatemenu.entryconfig(1, state=str_update)
                self.updatemenu.entryconfig(2, state=str_update)
                self.updatemenu.entryconfig(7, state=str_update)
                self.updatemenu.entryconfig(8, state=str_update)
                self.filemenu.entryconfig(6, state='normal')
                self.filemenu.entryconfig(7, state='normal')

                self.image_label.config(text=str_filename)
                self.populate_blocks(dict_flash['blocks'])
                self.populate_defaults(dict_flash['defaults'])
                self.populate_cores(dict_flash['cores'])
                self.populate_roms(dict_roms)

                self.bios_import_button.state(['!disabled'])
                self.bios_export_button.state(['!disabled'])
                self.esxdos_import_button.state(['!disabled'])
                self.esxdos_export_button.state(['!disabled'])
                self.spectrum_import_button.state(['!disabled'])
                self.spectrum_export_button.state(['!disabled'])
                self.core_import_button.state(['!disabled'])
                self.rom_import_button.state(['!disabled'])

                core_number = len(self.core_table.get_children())
                self.core_spinbox.config(from_=1)
                self.core_spinbox.config(to=core_number + 1)
                self.core_spinbox.state(['!disabled'])
                self.timer_spinbox.state(['!disabled'])
                self.keyboard_spinbox.state(['!disabled'])
                self.video_spinbox.state(['!disabled'])
                rom_number: int = len(self.rom_table.get_children())
                self.rom_spinbox.config(from_=0)
                self.rom_spinbox.config(to=rom_number - 1)
                self.rom_spinbox.state(['!disabled'])

                self.rompack_import_button.state(['!disabled'])
                if rom_number:
                    self.rompack_export_button.state(['!disabled'])
            elif filetype == 'ROMPack v2':
                dict_roms, default_rom = zx123.list_romsdata(
                    str_file, self.fulldict_hash, 'RPv2', False, True)
                ROMPWindow(self, str_filename, filetype, dict_roms,
                           default_rom)
            else:
                if str_file:
                    dict_file = zx123.find_zxfile(str_file, self.fulldict_hash,
                                                  str_extension, str_kind,
                                                  False, True)
                    filetype: str = dict_file.get('kind', 'Unknown')
                    if filetype == 'ROMPack':
                        dict_roms, default_rom = zx123.list_romsdata(
                            str_file, self.fulldict_hash, 'ROMS', False, True)
                        ROMPWindow(self, str_filename, filetype, dict_roms,
                                   default_rom)
                    elif filetype != 'Unknown':
                        str_desc = self.fulldict_hash[str_kind]['description']
                        dict_file['kind'] = f'{str_desc} {dict_file["kind"]}'
                        InfoWindow(self, str_filename, dict_file)
                    else:
                        str_error: str = 'ERROR\nUnknown file\nFormat Unknown'
                        str_error += ' or uncataloged content.'
                        messagebox.showerror('Error', str_error, parent=self)

        # Enable File Menu
        self.menubar.entryconfig(0, state='normal')

    def convert_core(self: Any):
        """Converts between main (spectrum) and secondary core, and back"""
        filetypes: list[tuple[str, str]] = [('ZX1, ZX2, ZXD or ZX3 file',
                                             '.zx1 .zx2 .zxd .zx3')]
        str_file: str = fd.askopenfilename(parent=self,
                                           title='Select a file to open',
                                           filetypes=filetypes)

        if str_file:
            str_filename: str = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype, str_kind = zx123.detect_file(
                str_file, self.fulldict_hash)
            if filetype == 'Unknown':
                dict_file: dict[str, Any] = zx123.find_zxfile(
                    str_file, self.fulldict_hash, str_kind, False, True)
                filetype: str = dict_file.get('kind', 'Unknown')

            str_outfile = ''
            if filetype in ['Core', 'Spectrum']:
                filetypes: list[tuple[str, str]] = [(f'{str_extension} file',
                                                     f'.{str_extension}')]
                str_outfile: str = fd.asksaveasfilename(
                    parent=self,
                    title='New file to create',
                    filetypes=filetypes)
                if str_outfile:
                    str_error: str = zx123.convert_core(
                        str_file, dict_hash, str_outfile, True)
                    if str_error:
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        str_msg = f'{filetype} {str_filename} converted OK'
                        messagebox.showinfo('Converted', str_msg, parent=self)
            else:
                str_error = 'Wrong file type detected.\n'
                str_error += '"{filetype}" instead of core, cannot convert.'
                messagebox.showerror('Error', str_error, parent=self)

    def populate_blocks(self: Any, dict_blocks: dict[str, Any]):
        """
        Populate Blocks Data Entries texts in Main Window
        :param dict_blocks: Array with different blocks data
        """

        if 'BIOS' in dict_blocks:
            self.bios.set(dict_blocks['BIOS'][0])
        if 'esxdos' in dict_blocks:
            self.esxdos.set(dict_blocks['esxdos'][0])
        if 'Spectrum' in dict_blocks:
            self.spectrum.set(dict_blocks['Spectrum'][0])

    def populate_defaults(self: Any, dict_defaults: dict[str, Any]):
        """
        Populate Defaults Data texts in Main Window and old_... properties
        :param dict_defaults: Dictionary with values for defaults
        """

        self.old_core = dict_defaults['default_core']
        self.default_core.set(self.old_core)
        self.old_timer = dict_defaults['boot_timer']
        self.default_timer.set(self.old_timer)
        self.old_keyboard = dict_defaults['keyb_layout']
        self.default_keyboard.set(self.old_keyboard)
        self.old_video = dict_defaults['video_mode']
        self.default_video.set(self.old_video)
        self.old_rom = dict_defaults['default_rom']
        self.default_rom.set(self.old_rom)

    def show_core_info(self: Any):
        """Show extra details for current selection in core table"""
        t_selection: Any = self.core_table.selection()
        if len(t_selection) == 1:
            arr_selection: list[Any] = self.core_table.item(
                t_selection)['values']
            str_name: str = f'{arr_selection[1]} ({arr_selection[2]})'
            dict_core: dict[str,
                            Any] = self.fulldict_hash[self.zxkind]['Cores']
            dict_core: dict[str, Any] = dict_core[arr_selection[2]]

            dict_res: dict[str, str | dict[str, Any]] = {}
            str_desc = self.fulldict_hash[self.zxkind]['description']
            dict_res['kind'] = f'{str_desc} Core'
            dict_res['version'] = arr_selection[3]
            dict_res['detail'] = dict_core.get('features', {})

            InfoWindow(self, str_name, dict_res)

    def validate_file(self: Any, str_file: str,
                      arr_format: list[str]) -> tuple[bool, str]:
        """
        Checks if a file matches the selected format list
        :param str_file: File to analyze
        :arr_format: List of formats considered valid (e.g. ['ROMPack'])
        :return: True if valid
        """
        str_extension, _, filetype, str_kind = zx123.detect_file(
            str_file, self.fulldict_hash)
        dict_file: dict[str,
                        Any] = zx123.find_zxfile(str_file, self.fulldict_hash,
                                                 str_extension, str_kind,
                                                 False, True)
        kind: str = dict_file.get('kind', 'Unknown')
        if filetype == 'Unknown':
            filetype = kind

        if not self.dict_prefs.get('import_unknown', False):
            filetype = kind
        elif filetype == 'Unknown' and 'CorePart' in arr_format:
            filetype = 'CorePart'

        if self.dict_prefs.get('import_allroms', False):
            if filetype == 'Unknown':
                i_file_size: int = os.stat(str_file).st_size
                d_parts: dict[str, Any] = self.fulldict_hash['ROM']['parts']
                for block_id in [
                        '16K Spectrum ROM', '32K Spectrum ROM',
                        '64K Spectrum ROM', '128K Spectrum ROM'
                ]:
                    if block_id in d_parts:
                        if i_file_size == int(d_parts[block_id][1]):
                            filetype = block_id
                            break

        is_valid: bool = filetype in arr_format
        if not 'ROM' in filetype and is_valid and str_kind:
            if str_kind != self.zxkind:
                is_valid = False
                filetype = f'{str_kind} {filetype}'
        return is_valid, filetype

    def set_default_bios(self: Any, bios_value: tk.StringVar, old_val: int,
                         min_val: int, max_val: int, str_val: str) -> int:
        """
        Changes BIOS settings of flash image if the value is different
        :param bios_value: Variable associated to spinbox content
        :param old_val: Previous value to check against
        :param min_val: Minimum valid value
        :param max_val: Maximum valid value
        :param str_val: Param name according to 'video', 'keyboard', etc.
        :return: The final value evaluated, either the old or the new
        """
        self.changed_bios_spinbox(bios_value, min_val, max_val)
        str_new_val: str = bios_value.get()
        if str_new_val.isnumeric():
            new_val = int(str_new_val) - min_val
            if new_val != old_val:
                arr_str_val: list[str] = [
                    'video', 'keyboard', 'timer', 'core', 'rom'
                ]
                arr_val: list[int] = [-1, -1, -1, -1, -1]
                for elem in enumerate(arr_str_val):
                    if str_val == elem[1]:
                        arr_val[elem[0]] = new_val

                zx123.inject_zxfiles(self.zxfilepath, [], self.zxfilepath,
                                     self.fulldict_hash, self.zxextension,
                                     arr_val[0], arr_val[1], arr_val[2],
                                     arr_val[3], arr_val[4], True)
                return new_val

        return old_val

    def set_default_core(self: Any, *_: Any):
        """Proxy to set_default_bios for default Core set action"""
        self.old_core = self.set_default_bios(
            self.default_core, self.old_core, 1,
            len(self.core_table.get_children()) + 1, 'core')

    def set_default_timer(self: Any, *_: Any):
        """Proxy to set_default_bios for default timer set action"""
        self.old_timer = self.set_default_bios(self.default_timer,
                                               self.old_timer, 0, 4, 'timer')

    def set_default_keyboard(self: Any, *_: Any):
        """Proxy to set_default_bios for default keyboard set action"""
        self.old_keyboard = self.set_default_bios(self.default_keyboard,
                                                  self.old_keyboard, 0, 3,
                                                  'keyboard')

    def set_default_video(self: Any, *_: Any):
        """Proxy to set_default_bios for default video set action"""
        self.old_video = self.set_default_bios(self.default_video,
                                               self.old_video, 0, 2, 'video')

    def set_default_rom(self: Any, *_: Any):
        """Proxy to set_default_bios for default ROM set action"""
        self.old_rom = self.set_default_bios(
            self.default_rom, self.old_rom, 0,
            len(self.rom_table.get_children()) - 1, 'rom')

    def block_import(self: Any,
                     str_block: str,
                     extra_exts: Optional[list[str]] = None):
        """
        Generic block import to SPI flash image file
        :param str_block: Name of the kind of block (e.g. 'BIOS')
        """

        self.menubar.entryconfig(0, state='disabled')

        str_exts: str = f'.{self.zxextension}'
        if extra_exts:
            try:
                for str_ext in extra_exts:
                    str_exts += f' .{str_ext}'
            except TypeError:
                print(f'Wrong type for {extra_exts}')

        filetypes: list[tuple[str, str]] = [(f'{str_block} files', str_exts)]
        str_file: str = fd.askopenfilename(parent=self,
                                           title=f'Open {str_block} file',
                                           filetypes=filetypes)

        if str_file:
            b_block_ok, filetype = self.validate_file(str_file, [str_block])
            if b_block_ok:
                response: bool = True
                if self.dict_prefs.get('ask_replace', True):
                    str_title: str = f'Replace {str_block}'
                    str_message: str = f'Do you want to replace {str_block}?'
                    response: bool = messagebox.askyesno(parent=self,
                                                         icon='question',
                                                         title=str_title,
                                                         message=str_message)
                if response:
                    _, arr_err = zx123.inject_zxfiles(
                        self.zxfilepath, [f'{str_block},{str_file}'],
                        self.zxfilepath,
                        self.fulldict_hash,
                        self.zxkind,
                        b_force=True)
                    if arr_err:
                        str_error: str = f'ERROR\nCannot insert {str_block}.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                str_error = f'ERROR\nFile Format not valid.\n{filetype}'
                str_error += f' detected, and it should be a {str_block}.'
                messagebox.showerror('Error', str_error, parent=self)

        self.menubar.entryconfig(0, state='normal')

    def block_export(self: Any, str_block: str):
        """
        Generic block export from SPI flash image file
        :param str_block: Name of the kind of block (e.g. 'BIOS')
        """

        self.menubar.entryconfig(0, state='disabled')

        str_directory: str = os.path.dirname(self.zxfilepath)
        str_directory = fd.askdirectory(
            parent=self,
            initialdir=str_directory,
            title=f'Select {str_block} Export Path')
        if str_directory:
            zx123.extractfrom_zxdata(self.zxfilepath, str_block,
                                     self.fulldict_hash, str_directory,
                                     self.zxextension, self.zxkind, True,
                                     False)

        self.menubar.entryconfig(0, state='normal')

    def bios_import(self: Any):
        """Proxy to block_import for BIOS import action"""
        self.block_import('BIOS')

    def bios_export(self: Any):
        """Proxy to block_import for BIOS export action"""
        self.block_export('BIOS')

    def esxdos_import(self: Any):
        """Proxy to block_import for esxdos import action"""
        self.block_import('esxdos', extra_exts=['bin'])

    def esxdos_export(self: Any):
        """Proxy to block_import for esxdos export action"""
        self.block_export('esxdos')

    def spectrum_import(self: Any):
        """Proxy to block_import for Spectrum Core import action"""
        self.block_import('Spectrum')

    def spectrum_export(self: Any):
        """Proxy to block_import for Spectrum Core export action"""
        self.block_export('spectrum')

    def multi_import(self: Any,
                     str_name: str,
                     treeview: ttk.Treeview,
                     b_core: bool = False,
                     b_alt: bool = False,
                     b_rename: bool = False):
        """
        Generic core or ROM import to SPI flash Image
        :param str_name: Text to compose dialogs
        :param treeview: Reference to the table with (maybe) a selection
        :param b_core: If True, the selection is a Core, or else a ROM
        :param b_rename: If True, only renaming. Do not ask for a file
        """

        self.menubar.entryconfig(0, state='disabled')

        str_extension: str = 'ROM'
        arr_format: list[str] = [
            '16K Spectrum ROM', '32K Spectrum ROM', '64K Spectrum ROM',
            '128K Spectrum ROM'
        ]
        if b_core:
            str_extension = self.zxextension
            arr_format = ['Core', 'CorePart']
        filetypes: list[tuple[str, str]] = [
            (f'{self.zxextension} {str_name} files', f'.{str_extension}')
        ]
        str_file: str = ''
        if not b_rename:
            str_file = fd.askopenfilename(parent=self,
                                          title=f'Open a {str_name} file',
                                          filetypes=filetypes)

        filetype: str = ''
        if str_file:
            b_block_ok, filetype = self.validate_file(str_file, arr_format)
            if not b_block_ok:
                str_file = ''
                str_error: str = f'ERROR\nFile Format not valid.\n{filetype}'
                str_kind: str = ''
                if self.zxkind:
                    str_kind = f'{self.zxkind} '
                str_error += f' detected, and it should be a {str_kind}{str_name}.'
                messagebox.showerror('Error', str_error, parent=self)

        if b_rename or str_file:
            itm_indx: int = 99
            t_selection: Any = treeview.selection()
            response: bool = True
            if t_selection:
                itm_indx = int(t_selection[0])
                response = True
                if not b_rename and self.dict_prefs.get('ask_replace', True):
                    str_title: str = f'Replace {str_name}'
                    str_message: str = f'Do you want to replace {str_name} {itm_indx}?'
                    response = messagebox.askyesno(parent=self,
                                                   icon='question',
                                                   title=str_title,
                                                   message=str_message)
            else:
                if not b_rename:
                    if self.dict_prefs.get('ask_insert', False):
                        str_title = f'Insert {str_name}'
                        str_message = f'Do you want to insert a new {str_name}?'
                        response = messagebox.askyesno(parent=self,
                                                       icon='question',
                                                       title=str_title,
                                                       message=str_message)
                else:
                    response = False
            if response:
                slot_name: str  = ''
                if filetype != 'CorePart':
                    str_dialog_name: str = f'{str_name}'
                    if itm_indx < 99:
                        str_dialog_name += f' {itm_indx}'
                    dialog: NewEntryDialog = NewEntryDialog(
                        self, str_dialog_name, b_core, b_alt, b_rename)
                    treeview.focus_force()
                    slot_name = dialog.result_name
                else:
                    slot_name = 'DO NOT USE THIS!'
                slot_param: str = f'{str_name},{itm_indx},{slot_name}'
                if str_file:
                    slot_param += f',{str_file}'
                if not b_core:
                    if itm_indx == 99:
                        slot_number: int = 99
                    else:
                        slot_number = int(treeview.item(itm_indx)['values'][1])
                    slot_extra = dialog.extra
                    slot_param = f'{str_name},{slot_number},{slot_extra}'
                    slot_param += f',{slot_name}'
                    if str_file:
                        slot_param += f',{str_file}'
                if slot_name:
                    _, arr_err = zx123.inject_zxfiles(self.zxfilepath,
                                                      [slot_param],
                                                      self.zxfilepath,
                                                      self.fulldict_hash,
                                                      self.zxkind,
                                                      b_force=True)
                    if arr_err:
                        str_error: str = f'ERROR\nCannot insert {str_extension}.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                self.focus_force()

        self.menubar.entryconfig(0, state='normal')

    def multi_export(self: Any,
                     str_name: str,
                     treeview: ttk.Treeview,
                     b_core: bool = False):
        """
        Generic core(s) or ROM(s) export from SPI flash Image
        :param str_name: Text to compose dialogs
        :param treeview: Reference to the table (TreeView) with a selection
        :param b_is_core: If True, the selection are Cores, or else ROMs
        """
        self.menubar.entryconfig(0, state='disabled')

        str_directory: str = os.path.dirname(self.zxfilepath)
        str_directory: str = fd.askdirectory(
            parent=self,
            initialdir=str_directory,
            title=f'Select {str_name} Export Path')
        if str_directory:
            t_selection: Any = treeview.selection()
            for x_item in t_selection:
                zx123.extractfrom_zxdata(self.zxfilepath, x_item,
                                         self.fulldict_hash, str_directory,
                                         self.zxextension, self.zxkind, True,
                                         b_core)

        self.menubar.entryconfig(0, state='normal')

    def core_import(self: Any):
        """Proxy to multi_import for secondary Core import action"""
        self.multi_import('Core', self.core_table, True)

    def core_rename(self: Any):
        """Proxy to multi_import for secondary Core rename action"""
        t_selection: Any = self.core_table.selection()
        if len(t_selection) == 1:
            self.multi_import('Core', self.core_table, True, b_rename=True)

    def core_export(self: Any):
        """Proxy to multi_import for secondary Core export action"""
        self.multi_export('Core', self.core_table, True)

    def rom_import_n(self: Any, *_: Any):
        """Proxy to multi_import for ROM import action"""
        self.multi_import('ROM', self.rom_table, False, False)

    def rom_import_y(self: Any, *_: Any):
        """Proxy to multi_import for ROM import action"""
        self.multi_import('ROM', self.rom_table, False, True)

    def rom_rename(self: Any):
        """Proxy to multi_import for ROM rename action"""
        t_selection: Any = self.rom_table.selection()
        if len(t_selection) == 1:
            self.multi_import('ROM', self.rom_table, False, b_rename=True)

    def rom_export(self: Any):
        """Proxy to multi_import for ROM export action"""
        self.multi_export('ROM', self.rom_table, False)

    def rompack_import(self: Any):
        """"ROMPack v1 import to SPI flash Image"""
        self.menubar.entryconfig(0, state='disabled')

        filetypes: list[tuple[str, str]] = [('ROMPack v1 files', '.zx1')]
        str_file: str = fd.askopenfilename(parent=self,
                                           title='Open ROMPack v1 file',
                                           filetypes=filetypes)

        if str_file:
            b_block_ok, filetype = self.validate_file(
                str_file, ['ROMPack', 'ZX-Uno RomPack'])
            if b_block_ok:
                response: bool = True
                if self.dict_prefs.get('ask_replace', True):
                    str_title: str = 'Replace ROMs'
                    str_message: str = 'Do you really want to replace all ROMs?'
                    response: bool = messagebox.askyesno(parent=self,
                                                         icon='question',
                                                         title=str_title,
                                                         message=str_message)
                if response:
                    _, arr_err = zx123.inject_zxfiles(self.zxfilepath,
                                                      [f'ROMS,{str_file}'],
                                                      self.zxfilepath,
                                                      self.fulldict_hash,
                                                      self.zxkind,
                                                      b_force=True)
                    if arr_err:
                        str_error: str = 'ERROR\nCannot insert ROMPack.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                str_error = f'ERROR\nFile Format not valid.\n{filetype}'
                str_error += ' detected, and it should be a ROMPack.'
                messagebox.showerror('Error', str_error, parent=self)

        self.menubar.entryconfig(0, state='normal')

    def rompack_export(self: Any):
        """Proxy to block_export for ROMPack v1 file"""
        self.block_export('ROMS')
