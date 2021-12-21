#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
# pylint: disable=import-outside-toplevel
"""
Copyright (c) 2021, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

ZX123 Tool GUI Classes
    Creation Methods defined in ._main_gui
    Extra Windows defined in ._extra_gui
"""

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

MY_DIRPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_DIRPATH)
JSON_DIR = APP_RESDIR = MY_DIRPATH


class App(tk.Tk):
    """Main GUI"""

    from ._main_gui import build_menubar
    from ._main_gui import bind_keys
    from ._main_gui import unbind_keys
    from ._main_gui import create_labels
    from ._main_gui import create_entries
    from ._main_gui import create_core_table, create_rom_table
    from ._main_gui import create_buttons
    from ._main_gui import populate_cores, populate_roms

    def __init__(self):

        super().__init__()

        self.pref_window = None
        if sys.platform == 'win32':
            # Windows config
            str_icon_path = os.path.join(MY_DIRPATH, 'ZX123 Tool.ico')
            self.iconbitmap(str_icon_path)
        elif sys.platform == 'darwin':
            # MacOS Open File Events
            self.createcommand('::tk::mac::OpenDocument', self.open_file)
            self.createcommand('::tk::mac::ShowPreferences', self.open_prefs)
        else:
            # Other
            pass

        if sys.version_info < (3, 8, 0):
            str_error = 'ERROR\n'
            str_error += 'This software requires at least Python version 3.8'
            messagebox.showerror('Error', str_error, parent=self)
            self.destroy()
            return

        self.dict_prefs = {}
        self.fulldict_hash = {}
        self.zxfilepath = ''
        self.zxextension = ''
        self.zxsize = 0
        self.old_core = self.old_timer = self.old_keyboard = None
        self.old_video = self.old_rom = None

        self.load_json()
        self.load_prefs()
        self.unbind_keys()

        # Main Window
        self.title('ZX123 Tool')
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

        self.tk.eval(f'tk::PlaceWindow {self._w} center')
        self.update_idletasks()

        # Menu
        self.build_menubar()
        self.bind_keys()

        # Update JSON on startup
        if self.dict_prefs['update_json']:
            self.update_json()

        # Check for updates on startup
        if self.dict_prefs['check_updates']:
            self.check_updates()

        # Load files from command line args
        if len(sys.argv) > 1:
            self.open_file(sys.argv[1:])

    def check_updates(self):
        """Gets the latest release version from GitHub"""
        print("Checking for updates...")
        result = urllib.request.urlopen(
            'https://github.com/kounch/zx123_tool/releases/latest')
        new_version = result.url.split('/')[-1]
        old_version = zx123.__MY_VERSION__
        if new_version > old_version:
            str_msg = f'There\'s a new version ({new_version}) of'
            str_msg += ' ZX123 Tool available to download.'
            messagebox.showinfo('Update available', str_msg, parent=self)

    def load_prefs(self):
        """Load preferences from file if found, or set default settings"""
        dict_prefs = {
            'update_json': False,
            'check_updates': False,
            'ask_insert': False,
            'ask_replace': True
        }
        str_prefs = os.path.join(JSON_DIR, 'zx123_prefs.json')
        if not os.path.isfile(str_prefs):
            print('Prefs not found')
        else:
            with open(str_prefs, 'r', encoding='utf-8') as prefs_handle:
                dict_load = json.load(prefs_handle)
            for key in dict_load:
                dict_prefs[key] = dict_load[key]

        self.dict_prefs = dict_prefs

    def save_prefs(self):
        """Save preferences to file"""
        str_prefs = os.path.join(JSON_DIR, 'zx123_prefs.json')
        with open(str_prefs, 'w', encoding='utf-8') as prefs_handle:
            json.dump(self.dict_prefs, prefs_handle)

    def open_prefs(self):
        """Show or set focus to preferences window"""
        if self.pref_window:
            self.pref_window.top.focus_force()
        else:
            self.pref_window = PrefWindow(self)

    def load_json(self):
        """Initialize JSON Database"""

        fulldict_hash = zx123.load_json_bd(base_dir=JSON_DIR)
        if os.path.isdir(APP_RESDIR):
            tmp_hash = zx123.load_json_bd(base_dir=APP_RESDIR)
            if 'version' in tmp_hash:
                old_version = '20211201.001'
                my_version = tmp_hash['version']
                if 'version' in fulldict_hash:
                    old_version = fulldict_hash['version']
                if old_version < my_version:
                    print('Updating database file...')
                    copy(os.path.join(APP_RESDIR, 'zx123_hash.json'), JSON_DIR)

        fulldict_hash = zx123.load_json_bd(base_dir=JSON_DIR)
        self.fulldict_hash = fulldict_hash

    def core_menu_popup(self, event):
        """Contextual Menu Handling for core table"""
        try:
            self.core_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.core_menu.grab_release()

    def json_menu_popup(self, event):
        """Contextual Menu Handling for JSON Version Label"""
        try:
            self.json_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.json_menu.grab_release()

    def update_json(self):
        """Update JSON Database and show in GUI"""
        fulldict_hash = zx123.load_json_bd(base_dir=JSON_DIR,
                                           str_update='json')
        if 'version' in fulldict_hash:
            str_text = f'Database: {fulldict_hash["version"]}'
            self.version_label.config(text=str_text)

        self.fulldict_hash = fulldict_hash

    def new_image(self):
        """Create a new image file from one of the included templates"""
        filetypes = [('ZX1 Flash Image', '.zx1'),
                     ('ZXDOS Flash Image', '.zx2'),
                     ('ZXDOS+ Flash Image', '.zxd')]
        str_file = fd.asksaveasfilename(parent=self,
                                        title='New file to create',
                                        filetypes=filetypes)
        if str_file:
            _, str_err = zx123.unzip_image(JSON_DIR, str_file,
                                           self.fulldict_hash, True)
            if str_err:
                str_error = 'ERROR\nCannot create new image file.\n'
                str_error += f'{str_err}\n'
                messagebox.showerror('Error', str_error, parent=self)
            else:
                self.open_file(str_file)

    def erase_image(self):
        """Wipes a Flash Image File, removing all cores and ROMs"""
        str_filename = os.path.split(self.zxfilepath)[1]

        str_title = f'Erase {str_filename}'
        str_message = f'Do you really want to erase {str_filename}?'
        response = messagebox.askyesno(parent=self,
                                       icon='question',
                                       title=str_title,
                                       message=str_message)
        if response:
            zx123.wipe_zxdata(self.zxfilepath,
                              self.zxfilepath,
                              self.fulldict_hash[self.zxextension],
                              b_force=True)
            self.open_file(self.zxfilepath)

    def expand_image(self):
        """Expands a ZXD 16MB flash image to 32MB"""
        str_filename = os.path.split(self.zxfilepath)[1]

        str_title = f'Erase {str_filename}'
        str_message = f'Do you really want to expand {str_filename}?'
        response = messagebox.askyesno(parent=self,
                                       icon='question',
                                       title=str_title,
                                       message=str_message)
        if response:
            print(f'Expand {self.zxfilepath}')
            img_len = 33554432
            zx123.expand_image(self.zxfilepath, self.zxfilepath, img_len, True)
            zx123.update_image(self.zxfilepath, self.zxfilepath,
                               self.fulldict_hash, self.zxextension, 'special',
                               False, True, False, False)
            self.open_file(self.zxfilepath)

    def full_close_image(self):
        """Restore button text and empty all fields of Main Window """
        self.core_import_button['text'] = 'Add New Core'
        self.core_export_button['text'] = 'Export Core'
        self.rom_import_button['text'] = 'Add New ROM'
        self.rom_export_button['text'] = 'Export ROM'
        self.close_image()

    def close_image(self):
        """Empty all fields of Main Window"""

        self.zxfilepath = ''

        self.filemenu.entryconfig(2, state='disabled', label='Close file')
        self.filemenu.entryconfig(4, state='disabled')
        self.filemenu.entryconfig(5, state='disabled')
        self.filemenu.entryconfig(6, state='disabled')
        self.filemenu.entryconfig(8, state='disabled', label='Show info')
        self.core_menu.entryconfig(0, state='disabled', label='Show info')

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

    def update_image(self, str_update, get_1core=False, get_2mb=False):
        """
        Tries to update BIOS and or Core(s) of image file
        :param str_update: Description of the udpdate ("all", "bios", etc.)
        :param get_1core: Use "1core" entries of JSON
        :param get_2mb: Use "2m" entries of JSON
        """
        str_title = f'Update {str_update}'
        str_message = f'Are you sure that you want to update {str_update}?'
        response = messagebox.askyesno(parent=self,
                                       icon='question',
                                       title=str_title,
                                       message=str_message)
        if response:
            w_progress = ProgressWindow(self, f'Update {str_update}')
            w_progress.show()
            zx123.update_image(self.zxfilepath, self.zxfilepath,
                               self.fulldict_hash, self.zxextension,
                               str_update, False, True, get_1core, get_2mb,
                               w_progress)
            self.open_file(self.zxfilepath)
            w_progress.close()

    def open_file(self, *args):
        """
        Open the first file received. If there's no file, ask for it
        :param args: Array of file paths. Only the first element is analyzed
        """

        # Disable File Menu
        self.menubar.entryconfig(0, state='disabled')

        if args:
            str_file = args[0]
        else:
            filetypes = [('ZX1, ZX2, ZXD or ROM files',
                          '.zx1 .zx2 .zxd .rom .bin')]
            str_file = fd.askopenfilename(parent=self,
                                          title='Select a file to open',
                                          filetypes=filetypes)

        if isinstance(str_file, str):  # To avoid MacOS quarantine events
            str_filename = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype = zx123.detect_file(
                str_file, self.fulldict_hash)

            if filetype == 'FlashImage':
                self.full_close_image()
                self.zxfilepath = str_file
                self.zxextension = str_extension
                self.zxsize = os.stat(str_file).st_size
                zx123.STR_OUTDIR = os.path.dirname(str_file)

                dict_flash = zx123.list_zxdata(str_file, dict_hash, False)
                dict_roms, _ = zx123.list_romsdata(str_file,
                                                   self.fulldict_hash,
                                                   str_extension, False)
                str_filename = f'{str_filename} ({dict_flash["description"]})'
                str_filename += f' {int(self.zxsize / 1048576)}MB'

                self.filemenu.entryconfig(2,
                                          state='normal',
                                          label='Close image file')
                self.filemenu.entryconfig(4, state='normal')
                if self.zxsize < 33554432 and self.zxextension == 'ZXD':
                    self.filemenu.entryconfig(5, state='normal')

                if self.zxextension == 'ZX1':
                    str_update = 'normal'
                else:
                    str_update = 'disabled'
                self.updatemenu.entryconfig(1, state=str_update)
                self.updatemenu.entryconfig(2, state=str_update)
                self.updatemenu.entryconfig(7, state=str_update)
                self.updatemenu.entryconfig(8, state=str_update)
                self.filemenu.entryconfig(6, state='normal')

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
                rom_number = len(self.rom_table.get_children())
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
                                                  str_extension, False, True)
                    filetype = dict_file.get('kind', 'Unknown')
                    if filetype == 'ROMPack':
                        dict_roms, default_rom = zx123.list_romsdata(
                            str_file, self.fulldict_hash, 'ROMS', False, True)
                        ROMPWindow(self, str_filename, filetype, dict_roms,
                                   default_rom)
                    elif filetype != 'Unknown':
                        InfoWindow(self, str_filename, dict_file)
                    else:
                        str_error = 'ERROR\nUnknown file\nFormat Unknown'
                        str_error += ' or uncataloged content.'
                        messagebox.showerror('Error', str_error, parent=self)

        # Enable File Menu
        self.menubar.entryconfig(0, state='normal')

    def convert_core(self):
        """Converts between main (spectrum) and secondary core, and back"""
        filetypes = [('ZX1, ZX2 or ZXD file', '.zx1 .zx2 .zxd')]
        str_file = fd.askopenfilename(parent=self,
                                      title='Select a file to open',
                                      filetypes=filetypes)

        if str_file:
            str_filename = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype = zx123.detect_file(
                str_file, self.fulldict_hash)
            if filetype == 'Unknown':
                dict_file = zx123.find_zxfile(str_file, self.fulldict_hash,
                                              str_extension, False, True)
                if 'kind' in dict_file:
                    filetype = dict_file['kind']

            str_outfile = ''
            if filetype in ['Core', 'Spectrum']:
                filetypes = [(f'{str_extension} file', f'.{str_extension}')]
                str_outfile = fd.asksaveasfilename(parent=self,
                                                   title='New file to create',
                                                   filetypes=filetypes)
                if str_outfile:
                    str_error = zx123.convert_core(str_file, dict_hash,
                                                   str_outfile, True)
                    if str_error:
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        str_msg = f'{filetype} {str_filename} converted OK'
                        messagebox.showinfo('Converted', str_msg, parent=self)
            else:
                str_error = 'Wrong file type detected.\n'
                str_error += '"{filetype}" instead of core, cannot convert.'
                messagebox.showerror('Error', str_error, parent=self)

    def populate_blocks(self, dict_blocks):
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

    def populate_defaults(self, dict_defaults):
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

    def show_info(self):
        """Show extra details for current selection in core table"""
        t_selection = self.core_table.selection()
        if len(t_selection) == 1:
            arr_selection = self.core_table.item(t_selection)['values']
            str_name = f'{arr_selection[1]} ({arr_selection[2]})'
            dict_core = self.fulldict_hash[self.zxextension]['Cores']
            dict_core = dict_core[arr_selection[2]]

            dict_res = {}
            dict_res['kind'] = 'Core'
            dict_res['version'] = arr_selection[3]
            dict_res['detail'] = dict_core.get('features', {})

            InfoWindow(self, str_name, dict_res)

    def process_selected(self, treeview, import_bttn, export_bttn, str_text):
        """
        Configure buttons according to the selections sent by ..._selected...
        :param treeview: Origin of the selection event
        :param import_bttn: Associated import button
        :param export_bttn: Associated export button
        :param str_text: Associated text to compose the buttons content
        """

        t_selection = treeview.selection()
        if t_selection:
            import_bttn['text'] = f'Replace {str_text} {t_selection[0]}'
            export_bttn.state(['!disabled'])
            if len(t_selection) > 1:
                export_bttn['text'] = f'Export {str_text}s'
            else:
                export_bttn['text'] = f'Export {str_text} {t_selection[0]}'
                str_label = f'Show info for {str_text} {t_selection[0]}'
                self.filemenu.entryconfig(8, state='normal', label=str_label)
                self.core_menu.entryconfig(0, state='normal', label=str_label)
        else:
            import_bttn['text'] = f'Add New {str_text}'
            export_bttn['text'] = f'Export {str_text}'
            export_bttn.state(['disabled'])
            str_label = 'Show info'
            self.filemenu.entryconfig(8, state='disabled', label=str_label)
            self.core_menu.entryconfig(0, state='disabled', label=str_label)

    def coretable_selected(self, *_):
        """
        Configure Cores Data Table buttons depending on selected cores
        """
        self.process_selected(self.core_table, self.core_import_button,
                              self.core_export_button, 'Core')

    def romtable_selected(self, *_):
        """
        Configure ROMs Data Table buttons depending on selected ROMs
        """
        self.process_selected(self.rom_table, self.rom_import_button,
                              self.rom_export_button, 'ROM')

    def validate_file(self, str_file, arr_format):
        """
        Checks if a file matches the selected format list
        :param str_file: File to analyze
        :arr_format: List of formats considered valid (e.g. ['ROMPack'])
        :return: True if valid
        """
        str_extension, _, filetype = zx123.detect_file(str_file,
                                                       self.fulldict_hash)
        if filetype == 'Unknown':
            dict_file = zx123.find_zxfile(str_file, self.fulldict_hash,
                                          str_extension, False, True)
            if 'kind' in dict_file:
                filetype = dict_file['kind']

        return bool(filetype in arr_format), filetype

    def set_default_bios(self, bios_value, old_val, min_val, max_val, str_val):
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
        new_val = bios_value.get()
        if new_val.isnumeric():
            new_val = int(new_val)
            if new_val != old_val:
                arr_val = ['video', 'keyboard', 'timer', 'core', 'rom']
                for elem in enumerate(arr_val):
                    if str_val == elem[1]:
                        arr_val[elem[0]] = new_val
                    else:
                        arr_val[elem[0]] = -1
                zx123.inject_zxfiles(self.zxfilepath, [], self.zxfilepath,
                                     self.fulldict_hash, self.zxextension,
                                     arr_val[0], arr_val[1], arr_val[2],
                                     arr_val[3], arr_val[4], True)
                return new_val

        return old_val

    def set_default_core(self, *_):
        """Proxy to set_default_bios for default Core set action"""
        self.old_core = self.set_default_bios(
            self.default_core, self.old_core, 1,
            len(self.core_table.get_children()) + 1, 'core')

    def set_default_timer(self, *_):
        """Proxy to set_default_bios for default timer set action"""
        self.old_timer = self.set_default_bios(self.default_timer,
                                               self.old_timer, 0, 4, 'timer')

    def set_default_keyboard(self, *_):
        """Proxy to set_default_bios for default keyboard set action"""
        self.old_keyboard = self.set_default_bios(self.default_keyboard,
                                                  self.old_keyboard, 0, 3,
                                                  'keyboard')

    def set_default_video(self, *_):
        """Proxy to set_default_bios for default video set action"""
        self.old_video = self.set_default_bios(self.default_video,
                                               self.old_video, 0, 2, 'video')

    def set_default_rom(self, *_):
        """Proxy to set_default_bios for default ROM set action"""
        self.old_rom = self.set_default_bios(
            self.default_rom, 0, self.old_rom,
            len(self.rom_table.get_children()) - 1, 'rom')

    def changed_bios_spinbox(self, bios_value, min_val, max_val):
        """
        Process default bios setting change event, and enforce limits if needed
        :param bios_value: Variable associated to spinbox content
        :param min_val: Minimum valid value
        :param max_val: Maximum valid value
        """
        new_val = bios_value.get()
        if new_val.isnumeric():
            new_val = int(new_val)
            if new_val < min_val:
                new_val = min_val
            if new_val > max_val:
                new_val = max_val
        else:
            new_val = min_val

        bios_value.set(new_val)

    def changed_core_spinbox(self, *_):
        """Proxy to changed_bios_spinbox for default Core changed action"""
        self.changed_bios_spinbox(self.default_core, 1,
                                  len(self.core_table.get_children()) + 1)

    def changed_timer_spinbox(self, *_):
        """Proxy to changed_bios_spinbox for default timer changed action"""
        self.changed_bios_spinbox(self.default_timer, 0, 4)

    def changed_keyboard_spinbox(self, *_):
        """Proxy to changed_bios_spinbox for default keyboard changed action"""
        self.changed_bios_spinbox(self.default_keyboard, 0, 3)

    def changed_video_spinbox(self, *_):
        """Proxy to changed_bios_spinbox for default video changed action"""
        self.changed_bios_spinbox(self.default_video, 0, 2)

    def changed_rom_spinbox(self, *_):
        """Proxy to changed_bios_spinbox for default ROM changed action"""
        self.changed_bios_spinbox(self.default_rom, 0,
                                  len(self.rom_table.get_children()) - 1)

    def block_import(self, str_block, extra_exts=None):
        """
        Generic block import to SPI flash image file
        :param str_block: Name of the kind of block (e.g. 'BIOS')
        """

        self.menubar.entryconfig(0, state='disabled')

        str_exts = f'.{self.zxextension}'
        try:
            for str_ext in extra_exts:
                str_exts += f' .{str_ext}'
        except TypeError:
            print(f'Wrong type for {extra_exts}')

        filetypes = [(f'{str_block} files', str_exts)]
        str_file = fd.askopenfilename(parent=self,
                                      title=f'Open {str_block} file',
                                      filetypes=filetypes)

        if str_file:
            b_block_ok, filetype = self.validate_file(str_file, [str_block])
            if b_block_ok:
                response = True
                if self.dict_prefs['ask_replace']:
                    str_title = f'Replace {str_block}'
                    str_message = f'Do you want to replace {str_block}?'
                    response = messagebox.askyesno(parent=self,
                                                   icon='question',
                                                   title=str_title,
                                                   message=str_message)
                if response:
                    _, arr_err = zx123.inject_zxfiles(
                        self.zxfilepath, [f'{str_block},{str_file}'],
                        self.zxfilepath,
                        self.fulldict_hash,
                        self.zxextension,
                        b_force=True)
                    if arr_err:
                        str_error = f'ERROR\nCannot insert {str_block}.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                str_error = f'ERROR\nFile Format not valid.\n{filetype}'
                str_error += f' detected, and it should be {str_block}.'
                messagebox.showerror('Error', str_error, parent=self)

        self.menubar.entryconfig(0, state='normal')

    def block_export(self, str_block):
        """
        Generic block export from SPI flash image file
        :param str_block: Name of the kind of block (e.g. 'BIOS')
        """

        self.menubar.entryconfig(0, state='disabled')

        str_directory = os.path.dirname(self.zxfilepath)
        str_directory = fd.askdirectory(
            parent=self,
            initialdir=str_directory,
            title=f'Select {str_block} Export Path')
        if str_directory:
            zx123.extractfrom_zxdata(self.zxfilepath, str_block,
                                     self.fulldict_hash, str_directory,
                                     self.zxextension, True)

        self.menubar.entryconfig(0, state='normal')

    def bios_import(self):
        """Proxy to block_import for BIOS import action"""
        self.block_import('BIOS')

    def bios_export(self):
        """Proxy to block_import for BIOS export action"""
        self.block_export('BIOS')

    def esxdos_import(self):
        """Proxy to block_import for esxdos import action"""
        self.block_import('esxdos', extra_exts=['bin'])

    def esxdos_export(self):
        """Proxy to block_import for esxdos export action"""
        self.block_export('esxdos')

    def spectrum_import(self):
        """Proxy to block_import for Spectrum Core import action"""
        self.block_import('Spectrum')

    def spectrum_export(self):
        """Proxy to block_import for Spectrum Core export action"""
        self.block_export('spectrum')

    def multi_import(self, str_name, treeview, b_core=False, b_alt=False):
        """
        Generic core or ROM import to SPI flash Image
        :param str_name: Text to compose dialogs
        :param treeview: Reference to the table with (maybe) a selection
        :param b_core: If True, the selection is a Core, or else a ROM
        """

        self.menubar.entryconfig(0, state='disabled')

        str_extension = 'ROM'
        arr_format = [
            '16K Spectrum ROM', '32K Spectrum ROM', '64K Spectrum ROM'
        ]
        if b_core:
            str_extension = self.zxextension
            arr_format = [str_name]
        filetypes = [(f'{self.zxextension} {str_name} files',
                      f'.{str_extension}')]
        str_file = fd.askopenfilename(parent=self,
                                      title=f'Open a {str_name} file',
                                      filetypes=filetypes)

        if str_file:
            b_block_ok, filetype = self.validate_file(str_file, arr_format)
            if not b_block_ok:
                str_file = ''
                str_error = f'ERROR\nFile Format not valid.\n{filetype}'
                str_error += f' detected, and it should be {str_name}.'
                messagebox.showerror('Error', str_error, parent=self)

        if str_file:
            itm_indx = 99
            t_selection = treeview.selection()
            response = True
            if t_selection:
                itm_indx = int(t_selection[0])
                response = True
                if self.dict_prefs['ask_replace']:
                    str_title = f'Replace {str_name}'
                    str_message = f'Do you want to replace {str_name} {itm_indx}?'
                    response = messagebox.askyesno(parent=self,
                                                   icon='question',
                                                   title=str_title,
                                                   message=str_message)
            else:
                if self.dict_prefs['ask_insert']:
                    str_title = f'Insert {str_name}'
                    str_message = f'Do you want to insert a new {str_name}?'
                    response = messagebox.askyesno(parent=self,
                                                   icon='question',
                                                   title=str_title,
                                                   message=str_message)
            if response:
                str_dialog_name = f'{str_name}'
                if itm_indx < 99:
                    str_dialog_name += f' {itm_indx}'
                dialog = NewEntryDialog(self, str_dialog_name, b_core, b_alt)
                treeview.focus_force()
                slot_name = dialog.result_name
                slot_param = f'{str_name},{itm_indx},{slot_name},{str_file}'
                if not b_core:
                    if itm_indx == 99:
                        slot_number = 99
                    else:
                        slot_number = treeview.item(itm_indx)['values'][1]
                    slot_extra = dialog.extra
                    slot_param = f'{str_name},{slot_number},{slot_extra}'
                    slot_param += f',{slot_name},{str_file}'
                if slot_name:
                    _, arr_err = zx123.inject_zxfiles(self.zxfilepath,
                                                      [slot_param],
                                                      self.zxfilepath,
                                                      self.fulldict_hash,
                                                      self.zxextension,
                                                      b_force=True)
                    if arr_err:
                        str_error = f'ERROR\nCannot insert {str_extension}.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                self.focus_force()

        self.menubar.entryconfig(0, state='normal')

    def multi_export(self, str_name, treeview, b_core=False):
        """
        Generic core(s) or ROM(s) export from SPI flash Image
        :param str_name: Text to compose dialogs
        :param treeview: Reference to the table (TreeView) with a selection
        :param b_is_core: If True, the selection are Cores, or else ROMs
        """
        self.menubar.entryconfig(0, state='disabled')

        str_directory = os.path.dirname(self.zxfilepath)
        str_directory = fd.askdirectory(parent=self,
                                        initialdir=str_directory,
                                        title=f'Select {str_name} Export Path')
        if str_directory:
            t_selection = treeview.selection()
            for x_item in t_selection:
                zx123.extractfrom_zxdata(self.zxfilepath, x_item,
                                         self.fulldict_hash, str_directory,
                                         self.zxextension, True, b_core)

        self.menubar.entryconfig(0, state='normal')

    def core_import(self):
        """Proxy to multi_import for secondary Core import action"""
        self.multi_import('Core', self.core_table, True)

    def core_export(self):
        """Proxy to multi_import for secondary Core export action"""
        self.multi_export('Core', self.core_table, True)

    def rom_import_n(self, *_):
        """Proxy to multi_import for ROM import action"""
        self.multi_import('ROM', self.rom_table, False, False)

    def rom_import_y(self, *_):
        """Proxy to multi_import for ROM import action"""
        self.multi_import('ROM', self.rom_table, False, True)

    def rom_export(self):
        """Proxy to multi_import for ROM export action"""
        self.multi_export('ROM', self.rom_table, False)

    def rompack_import(self):
        """"ROMPack v1 import to SPI flash Image"""
        self.menubar.entryconfig(0, state='disabled')

        filetypes = [('ROMPack v1 files', '.zx1')]
        str_file = fd.askopenfilename(parent=self,
                                      title='Open ROMPack v1 file',
                                      filetypes=filetypes)

        if str_file:
            b_block_ok, filetype = self.validate_file(str_file, ['ROMPack'])
            if b_block_ok:
                response = True
                if self.dict_prefs['ask_replace']:
                    str_title = 'Replace ROMs'
                    str_message = 'Do you really want to replace all ROMs?'
                    response = messagebox.askyesno(parent=self,
                                                   icon='question',
                                                   title=str_title,
                                                   message=str_message)
                if response:
                    _, arr_err = zx123.inject_zxfiles(self.zxfilepath,
                                                      [f'ROMS,{str_file}'],
                                                      self.zxfilepath,
                                                      self.fulldict_hash,
                                                      self.zxextension,
                                                      b_force=True)
                    if arr_err:
                        str_error = 'ERROR\nCannot insert ROMPack.\n'
                        str_error += '\n'.join(arr_err)
                        messagebox.showerror('Error', str_error, parent=self)
                    else:
                        self.open_file(self.zxfilepath)
            else:
                str_error = f'ERROR\nFile Format not valid.\n{filetype}'
                str_error += ' detected, and it should be ROMPack.'
                messagebox.showerror('Error', str_error, parent=self)

        self.menubar.entryconfig(0, state='normal')

    def rompack_export(self):
        """Proxy to block_export for ROMPack v1 file"""
        self.block_export('ROMS')
