#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
# pylint: disable=too-many-lines
"""
Copyright (c) 2020-2021, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause
"""

import os
import sys
import pathlib
from shutil import copy
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

import zx123_tool as zx123

MY_DIRPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_DIRPATH)


def main():
    """Main Routine"""

    app = App()
    app.mainloop()


class App(tk.Tk):
    """Main GUI"""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__()

        if sys.platform == 'win32':
            # Windows config
            str_icon_path = os.path.join(MY_DIRPATH, 'ZX123 Tool.ico')
            self.iconbitmap(str_icon_path)
        elif sys.platform == 'darwin':
            # MacOS Open File Events
            self.createcommand("::tk::mac::OpenDocument", self.open_file)
        else:
            # Other
            pass

        self.load_json()
        self.zxfilepath = ''

        # Menu
        self.build_menubar()

        # Main Window
        self.title('ZX123 Tool')
        self.resizable(False, False)

        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill='both')
        self.blocks_frame = ttk.Frame(self.main_frame, padding=10)
        self.blocks_frame.pack()
        self.cores_frame = ttk.Frame(self.main_frame, padding=10)
        self.cores_frame.pack()
        self.roms_frame = ttk.Frame(self.main_frame, padding=10)
        self.roms_frame.pack()

        self.image_label = self.create_labels()
        self.create_entries()
        self.core_table, self.rom_table = self.create_tables()
        self.create_buttons()

        self.tk.eval(f'tk::PlaceWindow {self._w} center')
        self.update_idletasks()
        self.bind_keys()

        # Load files from command line args
        if len(sys.argv) > 1:
            self.open_file(sys.argv[1:])

    def load_json(self):
        """Initialize JSON Database"""
        json_dir = MY_DIRPATH
        app_resdir = ''
        if sys.platform == 'darwin':
            json_dir = os.path.join(os.environ.get('HOME'), 'Library',
                                    'Application Support', 'ZX123 Tool')
            app_resdir = os.path.abspath(
                os.path.join(MY_DIRPATH, '..', 'Resources'))

        if not os.path.isdir(json_dir):
            print('Initializing Resources...')
            pathlib.Path(json_dir).mkdir(parents=True, exist_ok=True)
            copy(os.path.join(app_resdir, 'zx123_hash.json'), json_dir)
            for str_ext in ['ZX1', 'ZX2', 'ZXD']:
                copy(os.path.join(app_resdir, f'FLASH16_empty.{str_ext}.zip'),
                     json_dir)

        fulldict_hash = zx123.load_json_bd(base_dir=json_dir)
        if os.path.isdir(app_resdir):
            tmp_hash = zx123.load_json_bd(base_dir=app_resdir)
            if 'version' in tmp_hash:
                old_version = '20211201.001'
                my_version = tmp_hash['version']
                if 'version' in fulldict_hash:
                    old_version = fulldict_hash['version']
                if old_version < my_version:
                    print('Updating database file...')
                    copy(os.path.join(app_resdir, 'zx123_hash.json'), json_dir)

        self.fulldict_hash = zx123.load_json_bd(base_dir=json_dir)

    def build_menubar(self):
        """Add Menu Bar"""

        if sys.platform == 'win32':
            # Windows Menu Bar
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="New Image File...",
                                 accelerator="Ctrl+n")
            filemenu.add_command(label="Open File...",
                                 command=self.open_file,
                                 accelerator="Ctrl+O")
            filemenu.add_command(label="Close Image File",
                                 accelerator="Ctrl+w",
                                 command=self.close_image)
            filemenu.add_separator()
            filemenu.add_command(label="Get Info", accelerator="Ctrl+i")
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.destroy)
            self.filemenu = filemenu

            editmenu = tk.Menu(menubar, tearoff=0)
            editmenu.add_command(
                label="Cut",
                accelerator="Ctrl+X",
                command=lambda: self.focus_get().event_generate('<<Cut>>'))
            editmenu.add_command(
                label="Copy",
                accelerator="Ctrl+C",
                command=lambda: self.focus_get().event_generate('<<Copy>>'))
            editmenu.add_command(
                label="Paste",
                accelerator="Ctrl+V",
                command=lambda: self.focus_get().event_generate('<<Paste>>'))

            menubar.add_cascade(label="File", menu=self.filemenu)
            menubar.add_cascade(label="Edit", menu=editmenu)
            self.menubar = menubar
            self.config(menu=menubar)
        elif sys.platform == 'darwin':
            # MacOS Menu Bar
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="New Image File...",
                                 accelerator="Command+n")
            filemenu.add_command(label="Open File...",
                                 command=self.open_file,
                                 accelerator="Command+o")
            filemenu.add_command(label="Close Image File",
                                 accelerator="Command+w",
                                 command=self.close_image)
            filemenu.add_separator()
            filemenu.add_command(label="Get Info", accelerator="Command+i")
            self.filemenu = filemenu

            editmenu = tk.Menu(menubar, tearoff=0)
            editmenu.add_command(
                label="Cut",
                accelerator="Command+X",
                command=lambda: self.focus_get().event_generate('<<Cut>>'))
            editmenu.add_command(
                label="Copy",
                accelerator="Command+C",
                command=lambda: self.focus_get().event_generate('<<Copy>>'))
            editmenu.add_command(
                label="Paste",
                accelerator="Command+V",
                command=lambda: self.focus_get().event_generate('<<Paste>>'))

            menubar.add_cascade(label="File", menu=self.filemenu)
            menubar.add_cascade(label="Edit", menu=editmenu)
            self.menubar = menubar
            self.config(menu=self.menubar)
        else:
            # Generic Menu Bar for other platforms
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="New Image File...")
            filemenu.add_command(label="Open File...", command=self.open_file)
            filemenu.add_command(label="Close Image File",
                                 command=self.close_image)
            filemenu.add_separator()
            filemenu.add_command(label="Get Info")

            editmenu = tk.Menu(menubar, tearoff=0)
            editmenu.add_command(
                label="Cut",
                accelerator="Ctrl+X",
                command=lambda: self.focus_get().event_generate('<<Cut>>'))
            editmenu.add_command(
                label="Copy",
                accelerator="Ctrl+C",
                command=lambda: self.focus_get().event_generate('<<Copy>>'))
            editmenu.add_command(
                label="Paste",
                accelerator="Ctrl+V",
                command=lambda: self.focus_get().event_generate('<<Paste>>'))

            menubar.add_cascade(label="File", menu=self.filemenu)
            menubar.add_cascade(label="Edit", menu=editmenu)
            self.menubar = menubar
            self.config(menu=self.menubar)

        self.filemenu.entryconfig(0, state='disabled')
        self.filemenu.entryconfig(2, state='disabled')
        self.filemenu.entryconfig(4, state='disabled')

    def bind_keys(self):
        """Bind Menu Keys"""
        if sys.platform == 'win32':
            self.bind_all("<Control-o>", lambda event: self.open_file())
            self.bind_all("<Control-w>", lambda event: self.close_image())
        elif sys.platform == 'darwin':
            self.bind_all("<Command-o>", lambda event: self.open_file())
            self.bind_all("<Command-w>", lambda event: self.close_image())
            self.bind_all("<Command-q>", lambda event: self.destroy())
        else:
            # Not Implemented
            pass

    def unbind_keys(self):
        """Bind Menu Keys"""
        if sys.platform == 'win32':
            self.unbind_all("<Control-o>")
            self.unbind_all("<Control-w>")
        elif sys.platform == 'darwin':
            self.unbind_all("<Command-o>")
            self.unbind_all("<Command-w>")
            self.unbind_all("<Command-q>")
        else:
            # Not Implemented
            pass

    def create_labels(self):
        "Create Main Window Labels"

        image_label = ttk.Label(self.blocks_frame, text='No Image File')
        image_label.grid(column=0, row=0, columnspan=7, sticky='n')

        if 'version' in self.fulldict_hash:
            version_label = ttk.Label(
                self.blocks_frame,
                font=("TkDefaultFont", 9),
                text=f'Database: {self.fulldict_hash["version"]}')
            version_label.grid(column=7, row=0, columnspan=8, sticky='ne')

        bios_label = ttk.Label(self.blocks_frame, text='BIOS:', padding=10)
        bios_label.grid(column=0, row=1, sticky='e')

        esxdos_label = ttk.Label(self.blocks_frame, text='esxdos:', padding=10)
        esxdos_label.grid(column=4, row=1, sticky='e')

        spectrum_label = ttk.Label(self.blocks_frame,
                                   text='ZX Spectrum Core:',
                                   padding=10)
        spectrum_label.grid(column=0, row=2, sticky='e')

        cores_label = ttk.Label(self.cores_frame, text='Cores')
        cores_label.grid(column=0, row=0, sticky='w')

        core_label = ttk.Label(self.cores_frame,
                               text='Default Core:',
                               padding=10,
                               width=12)
        core_label.grid(column=3, row=1, sticky='e')

        boot_label = ttk.Label(self.cores_frame,
                               text='Boot Timer:',
                               padding=10,
                               width=12)
        boot_label.grid(column=3, row=2, sticky='e')

        keyboard_label = ttk.Label(self.cores_frame,
                                   text='Keyboard Layout:',
                                   padding=10,
                                   width=12)
        keyboard_label.grid(column=3, row=3, sticky='e')

        video_label = ttk.Label(self.cores_frame,
                                text='Video Mode:',
                                padding=10,
                                width=12)
        video_label.grid(column=3, row=4, sticky='e')

        rom_label = ttk.Label(self.cores_frame,
                              text='Default ROM:',
                              padding=10,
                              width=12)
        rom_label.grid(column=3, row=8, sticky='e')

        roms_label = ttk.Label(self.roms_frame, text='ROMs')
        roms_label.grid(column=0, row=0, sticky='w')

        return image_label

    def create_entries(self):
        """Create Main Window Input Fields"""

        self.bios = tk.StringVar()
        bios_entry = ttk.Entry(self.blocks_frame,
                               width=10,
                               state='disabled',
                               textvariable=self.bios)
        bios_entry.grid(column=1, row=1, sticky='w')

        self.esxdos = tk.StringVar()
        esxdos_entry = ttk.Entry(self.blocks_frame,
                                 width=5,
                                 state='disabled',
                                 textvariable=self.esxdos)
        esxdos_entry.grid(column=5, row=1, sticky='w')

        self.spectrum = tk.StringVar()
        spectrum_entry = ttk.Entry(self.blocks_frame,
                                   state='disabled',
                                   textvariable=self.spectrum)
        spectrum_entry.grid(column=1, row=2, columnspan=5, sticky='we')
        self.spectrum_entry = spectrum_entry

        self.default_core = tk.StringVar()
        core_spin_box = ttk.Spinbox(self.cores_frame,
                                    from_=2,
                                    to=39,
                                    wrap=False,
                                    width=4,
                                    state='disabled',
                                    textvariable=self.default_core)
        core_spin_box.grid(column=4, row=1, sticky='e')

        self.default_timer = tk.StringVar()
        timer_spin_box = ttk.Spinbox(self.cores_frame,
                                     from_=0,
                                     to=3,
                                     wrap=False,
                                     width=4,
                                     state='disabled',
                                     textvariable=self.default_timer)
        timer_spin_box.grid(column=4, row=2, sticky='e')

        self.default_keyboard = tk.StringVar()
        keyboard_spin_box = ttk.Spinbox(self.cores_frame,
                                        from_=0,
                                        to=3,
                                        wrap=False,
                                        width=4,
                                        state='disabled',
                                        textvariable=self.default_keyboard)
        keyboard_spin_box.grid(column=4, row=3, sticky='e')

        self.default_video = tk.StringVar()
        video_spin_box = ttk.Spinbox(self.cores_frame,
                                     from_=0,
                                     to=2,
                                     wrap=False,
                                     width=4,
                                     state='disabled',
                                     textvariable=self.default_video)
        video_spin_box.grid(column=4, row=4, sticky='e')

        self.default_rom = tk.StringVar()
        rom_spin_box = ttk.Spinbox(self.cores_frame,
                                   from_=0,
                                   to=2,
                                   wrap=False,
                                   width=4,
                                   state='disabled',
                                   textvariable=self.default_rom)
        rom_spin_box.grid(column=4, row=8, sticky='e')

    def create_tables(self):
        """Create Main Window Tables"""
        style = ttk.Style()
        style.configure("Treeview.Cell", borderwidth=1)

        core_table = ttk.Treeview(self.cores_frame, height=15)
        core_table.grid(column=0, row=1, columnspan=3, rowspan=8, sticky='nsw')
        core_table['columns'] = ('id', 'name', 'core', 'version')
        core_table.column("#0", width=0, stretch=tk.NO)
        core_table.heading("#0", text="", anchor=tk.CENTER)
        col_sizes = [30, 240, 200, 250]
        for index, col_name in enumerate(core_table['columns']):
            core_table.column(col_name, anchor=tk.W, width=col_sizes[index])
            core_table.heading(col_name,
                               text=col_name.upper(),
                               anchor=tk.CENTER)
        core_table.bind('<<TreeviewSelect>>', self.coretable_selected)

        core_scrollbar = ttk.Scrollbar(self.cores_frame,
                                       orient=tk.VERTICAL,
                                       command=core_table.yview)
        core_table.configure(yscroll=core_scrollbar.set)
        core_scrollbar.grid(column=2, row=1, rowspan=8, sticky='nse')

        rom_table = ttk.Treeview(self.roms_frame, height=15)
        rom_table.grid(column=0, row=1, columnspan=4, sticky='nsew')
        rom_table['columns'] = ('id', 'slot', 'flags', 'crc', 'name', 'size',
                                'version')
        rom_table.column("#0", width=0, stretch=tk.NO)
        rom_table.heading("#0", text="", anchor=tk.CENTER)
        col_sizes = [30, 30, 80, 155, 280, 40, 300]
        for index, col_name in enumerate(rom_table['columns']):
            rom_table.column(col_name, anchor=tk.W, width=col_sizes[index])
            rom_table.heading(col_name,
                              text=col_name.upper(),
                              anchor=tk.CENTER)
        rom_table.bind('<<TreeviewSelect>>', self.romtable_selected)

        rom_scrollbar = ttk.Scrollbar(self.roms_frame,
                                      orient=tk.VERTICAL,
                                      command=rom_table.yview)
        rom_table.configure(yscroll=rom_scrollbar.set)
        rom_scrollbar.grid(column=3, row=1, sticky='nse')

        return core_table, rom_table

    def create_buttons(self):
        """Create Main Window buttons"""
        bios_import_button = ttk.Button(self.blocks_frame,
                                        text='Import BIOS',
                                        state='disabled',
                                        command=self.bios_import)
        bios_import_button.grid(column=2, row=1, sticky='we')
        self.bios_import_button = bios_import_button

        bios_export_button = ttk.Button(self.blocks_frame,
                                        text='Export BIOS',
                                        state='disabled',
                                        command=self.bios_export)
        bios_export_button.grid(column=3, row=1, sticky='we')
        self.bios_export_button = bios_export_button

        esxdos_import_button = ttk.Button(self.blocks_frame,
                                          text='Import esxdos',
                                          state='disabled',
                                          command=self.esxdos_import)
        esxdos_import_button.grid(column=6, row=1, sticky='we')
        self.esxdos_import_button = esxdos_import_button

        esxdos_export_button = ttk.Button(self.blocks_frame,
                                          text='Export esxdos',
                                          width=13,
                                          state='disabled',
                                          command=self.esxdos_export)
        esxdos_export_button.grid(column=7, row=1, sticky='we')
        self.esxdos_export_button = esxdos_export_button

        spectrum_import_button = ttk.Button(self.blocks_frame,
                                            text='Import Spectrum',
                                            state='disabled',
                                            command=self.spectrum_import)
        spectrum_import_button.grid(column=6, row=2, sticky='we')
        self.spectrum_import_button = spectrum_import_button

        spectrum_export_button = ttk.Button(self.blocks_frame,
                                            text='Export Spectrum',
                                            state='disabled',
                                            command=self.spectrum_export)
        spectrum_export_button.grid(column=7, row=2, columnspan=2, sticky='we')
        self.spectrum_export_button = spectrum_export_button

        core_import_button = ttk.Button(self.cores_frame,
                                        text='Import Core',
                                        state='disabled',
                                        width=17,
                                        command=self.core_import)
        core_import_button.grid(column=3, row=5, columnspan=2, sticky='e')
        self.core_import_button = core_import_button

        core_export_button = ttk.Button(self.cores_frame,
                                        text='Export Core',
                                        state='disabled',
                                        width=17,
                                        command=self.core_export)
        core_export_button.grid(column=3, row=6, columnspan=2, sticky='e')
        self.core_export_button = core_export_button

        #rename_core_button = ttk.Button(self.cores_frame,
        #                                text='Rename Core',
        #                                state='disabled',
        #                                width=17)
        #rename_core_button.grid(column=3, row=7, columnspan=2, sticky='e')
        #self.rename_core_button = rename_core_button

        rom_import_button = ttk.Button(self.roms_frame,
                                       text='Import ROM',
                                       state='disabled',
                                       width=17,
                                       command=self.rom_import)
        rom_import_button.grid(column=0, row=2, sticky='we', pady=10)
        self.rom_import_button = rom_import_button

        rom_export_button = ttk.Button(self.roms_frame,
                                       text='Export ROM',
                                       state='disabled',
                                       width=17,
                                       command=self.rom_export)
        rom_export_button.grid(column=1, row=2, sticky='we', padx=10, pady=10)
        self.rom_export_button = rom_export_button

        #rom_rename_button = ttk.Button(self.roms_frame,
        #                               text='Rename ROM',
        #                               state='disabled',
        #                               width=17)
        #rom_rename_button.grid(column=2, row=2, sticky='w', pady=10)
        #self.rom_rename_button = rom_rename_button

        rompack_button = ttk.Button(self.roms_frame,
                                    text='Import ROMPack...',
                                    state='disabled',
                                    width=17,
                                    command=self.rompack_import)
        rompack_button.grid(column=3, row=2, sticky='we', pady=10)
        self.rompack_button = rompack_button

    def close_image(self):
        """Empty all fields of Main Window"""

        self.zxfilepath = ''

        self.filemenu.entryconfig(2, state='disabled')

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

        self.bios_import_button.state(["disabled"])
        self.bios_export_button.state(["disabled"])
        self.esxdos_import_button.state(["disabled"])
        self.esxdos_export_button.state(["disabled"])
        self.spectrum_import_button.state(["disabled"])
        self.spectrum_export_button.state(["disabled"])
        self.core_import_button.state(["disabled"])
        self.core_export_button.state(["disabled"])
        self.rom_import_button.state(["disabled"])
        self.rom_export_button.state(["disabled"])
        self.rompack_button.state(["disabled"])

    def open_file(self, *args):
        """Open only one file"""

        # Disable File Menu
        self.menubar.entryconfig(0, state='disabled')

        if args:
            str_file = args[0]
        else:
            filetypes = [("ZX1, ZX2, ZXD or ROM files", ".zx1 .zx2 .zxd .rom")]
            str_file = fd.askopenfilename(parent=self,
                                          title='Select a file to open',
                                          filetypes=filetypes)

        if isinstance(str_file, str):  # To avoid MacOS quarantine events
            str_filename = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype = zx123.detect_file(
                str_file, self.fulldict_hash)

            if filetype == 'FlashImage':
                self.close_image()
                self.zxfilepath = str_file
                self.zxextension = str_extension

                dict_flash = zx123.list_zxdata(str_file, dict_hash, False)
                dict_roms = zx123.list_romsdata(str_file, self.fulldict_hash,
                                                str_extension, False)
                str_filename = f'{str_filename} ({dict_flash["description"]})'

                self.filemenu.entryconfig(2, state='normal')

                self.image_label.config(text=str_filename)
                self.populate_blocks(dict_flash['blocks'])
                self.populate_defaults(dict_flash['defaults'])
                self.populate_cores(dict_flash['cores'])
                self.populate_roms(dict_roms)

                self.bios_import_button.state(["!disabled"])
                self.bios_export_button.state(["!disabled"])
                self.esxdos_import_button.state(["!disabled"])
                self.esxdos_export_button.state(["!disabled"])
                self.spectrum_import_button.state(["!disabled"])
                self.spectrum_export_button.state(["!disabled"])
                self.core_import_button.state(["!disabled"])
                self.rom_import_button.state(["!disabled"])
                self.rompack_button.state(["!disabled"])
            elif filetype == 'ROMPack v2':
                print('ROMPack V2')
                messagebox.showinfo("ROMPackv2", str_filename, parent=self)
            else:
                if str_file:
                    dict_file = zx123.find_zxfile(str_file, self.fulldict_hash,
                                                  str_extension, False, True)
                    if 'kind' in dict_file:
                        self.unbind_keys()
                        InfoWindow(self, str_filename, dict_file)
                        self.focus_force()
                        self.bind_keys()
                    else:
                        str_error = 'ERROR\nUnknown file\nFormat Unknown'
                        str_error += ' or uncataloged content.'
                        messagebox.showerror('Error', str_error, parent=self)

        # Enable File Menu
        self.menubar.entryconfig(0, state='normal')

    def populate_blocks(self, dict_blocks):
        """Populate Blocks Data in Main Window"""

        if 'BIOS' in dict_blocks:
            self.bios.set(dict_blocks['BIOS'][0])
        if 'esxdos' in dict_blocks:
            self.esxdos.set(dict_blocks['esxdos'][0])
        if 'Spectrum' in dict_blocks:
            self.spectrum.set(dict_blocks['Spectrum'][0])

    def populate_defaults(self, dict_defaults):
        """Populate Defaults Data in Main Window"""

        self.default_core.set(dict_defaults['default_core'])
        self.default_timer.set(dict_defaults['boot_timer'])
        self.default_keyboard.set(dict_defaults['keyb_layout'])
        self.default_video.set(dict_defaults['video_mode'])
        self.default_rom.set(dict_defaults['default_rom'])

    def populate_cores(self, dict_cores):
        """Populate Cores Data in Main Window"""
        for index in dict_cores:
            self.core_table.insert(parent='',
                                   index='end',
                                   iid=index,
                                   text='',
                                   values=[index] +
                                   list(dict_cores[index])[:3])

    def populate_roms(self, dict_roms):
        """Populate ROMs Data in Main Window"""
        for index in dict_roms:
            self.rom_table.insert(parent='',
                                  index='end',
                                  iid=index,
                                  text='',
                                  values=[index] + list(dict_roms[index])[:6])

    def process_selected(self, treeview, button, str_text):
        """Configure buttons on selections"""

        t_selection = treeview.selection()
        if t_selection:
            button.state(["!disabled"])
        else:
            button.state(["disabled"])  # Disable the button.
        if len(t_selection) > 1:
            button['text'] = f'Export {str_text}s'
        else:
            button['text'] = f'Export {str_text}'

    def coretable_selected(self, event):  # pylint: disable=unused-argument
        """Configure buttons depending on selected cores"""
        self.process_selected(self.core_table, self.core_export_button, 'Core')

    def romtable_selected(self, event):  # pylint: disable=unused-argument
        """Configure buttons depending on selected ROMs"""
        self.process_selected(self.rom_table, self.rom_export_button, 'ROM')

    def block_import(self, str_block):
        """Generic block import method"""

        self.menubar.entryconfig(0, state='disabled')

        filetypes = [(f'{str_block} files', f'.{self.zxextension}')]
        str_file = fd.askopenfilename(parent=self,
                                      title=f'Open {str_block} file',
                                      filetypes=filetypes)

        if str_file:
            zx123.inject_zxfiles(self.zxfilepath, [f'{str_block},{str_file}'],
                                 self.zxfilepath,
                                 self.fulldict_hash,
                                 self.zxextension,
                                 b_force=True)
            self.open_file(self.zxfilepath)

        self.menubar.entryconfig(0, state='normal')

    def block_export(self, str_block):
        """Generic block export method"""

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
        """Proxy for BIOS import action"""
        self.block_import('BIOS')

    def bios_export(self):
        """Proxy for BIOS export action"""
        self.block_export('BIOS')

    def esxdos_import(self):
        """Proxy for esxdos import action"""
        self.block_import('esxdos')

    def esxdos_export(self):
        """Proxy for esxdos export action"""
        self.block_export('esxdos')

    def spectrum_import(self):
        """Proxy for Spectrum Core import action"""
        self.block_import('Spectrum')

    def spectrum_export(self):
        """Proxy for Spectrum Core export action"""
        self.block_export('spectrum')

    def multi_export(self, str_name, treeview, b_is_core=False):
        """Generic cores or ROMs export method"""
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
                                         self.zxextension, True, b_is_core)

        self.menubar.entryconfig(0, state='normal')

    def multi_import(self, str_name, treeview, b_core=False):
        """Generic core or ROM import"""

        self.menubar.entryconfig(0, state='disabled')

        str_extension = "ROM"
        if b_core:
            str_extension = self.zxextension
        filetypes = [(f'{self.zxextension} {str_name} files',
                      f'.{str_extension}')]
        str_file = fd.askopenfilename(parent=self,
                                      title=f'Open a {str_name} file',
                                      filetypes=filetypes)
        if str_file:
            t_selection = treeview.selection()
            itm_indx = 99
            str_title = f'Add {str_name}'
            str_message = f'Do you want to add a new {str_name}?'
            if t_selection:
                itm_indx = int(t_selection[0])
                str_title = f'Replace {str_name}'
                str_message = f'Do you want to replace {str_name} {itm_indx}?'
            response = messagebox.askyesno(parent=self,
                                           icon='question',
                                           title=str_title,
                                           message=str_message)

            if response:
                str_dialog_name = f'{str_name}'
                if itm_indx < 99:
                    str_dialog_name += f' {itm_indx}'
                self.unbind_keys()
                dialog = NewEntryDialog(self, str_dialog_name, b_core)
                self.focus_force()
                self.bind_keys()
                slot_name = dialog.result_name
                slot_param = f'{str_name},{itm_indx},{slot_name},{str_file}'
                if not b_core:
                    slot_number = treeview.item(itm_indx)['values'][1]
                    slot_extra = dialog.extra
                    slot_param = f'{str_name},{slot_number},{slot_extra}'
                    slot_param += f',{slot_name},{str_file}'
                if slot_name:
                    zx123.inject_zxfiles(self.zxfilepath, [slot_param],
                                         self.zxfilepath,
                                         self.fulldict_hash,
                                         self.zxextension,
                                         b_force=True)
                    self.open_file(self.zxfilepath)

        self.menubar.entryconfig(0, state='normal')

    def core_import(self):
        """Proxy for secondary Core import action"""
        self.multi_import('Core', self.core_table, True)

    def core_export(self):
        """Proxy for secondary Core export action"""
        self.multi_export('Core', self.core_table, True)

    def rom_import(self):
        """Proxy for ROM import action"""
        self.multi_import('ROM', self.rom_table, False)

    def rom_export(self):
        """Proxy for ROM export action"""
        self.multi_export('ROM', self.rom_table, False)

    def rompack_import(self):
        """"ROMPack v1 imort action"""
        self.menubar.entryconfig(0, state='disabled')

        filetypes = [("ROMPack v1 files", ".zx1")]
        str_file = fd.askopenfilename(parent=self,
                                      title='Open ROMPack v1 file',
                                      filetypes=filetypes)

        if str_file:
            zx123.inject_zxfiles(self.zxfilepath, [f'ROMS,{str_file}'],
                                 self.zxfilepath,
                                 self.fulldict_hash,
                                 self.zxextension,
                                 b_force=True)
            self.open_file(self.zxfilepath)

        self.menubar.entryconfig(0, state='normal')


class NewEntryDialog:
    """Custom Window to Enter Core or ROM info"""
    dict_rom_params = {
        'i': 'Keyboard issue 3 enabled (instead of issue 2)',
        'c': 'Disable memory contention',
        'd': 'Enable DivMMC',
        'n': 'Enable NMI DivMMC (esxdos Menu)',
        'p': 'Use Pentagon Timings',
        't': 'Use 128K timings',
        's': 'Disable DivMMC and ZXMMC ports',
        'm': 'Enable Timex Horizontal MMU',
        'h': 'Disable ROM high bit (1FFD bit 2)',
        'l': 'Disable ROM low bit (7FFD bit 4)',
        '1': 'Disable 1FFD port (+2A/3 paging)',
        '7': 'Disable 7FFD port (128K paging)',
        '2': 'Disable TurboSound (secondary AY chip)',
        'a': 'Disable AY chip',
        'r': 'Disable Radastanian mode',
        'x': 'Disable Timex mode',
        'u': 'Disable ULAPlus'
    }

    def __init__(self, parent, str_name, b_core=False):
        self.result_name = ''
        self.extra = ''
        self.b_rom = not b_core

        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)

        self.top.title(f'New {str_name} Entry')
        self.top.bind("<Return>", self.do_ok)

        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill='both')

        top_frame = ttk.Frame(main_frame, padding=10)
        top_frame.pack()
        extra_frame = ttk.Frame(main_frame, padding=10)
        extra_frame.pack(fill='x')
        bottom_frame = ttk.Frame(main_frame, padding=10)
        bottom_frame.pack(fill='x')

        name_label = ttk.Label(top_frame, text=f'{str_name} Name:')
        name_label.pack(side='left')

        self.name_entry = ttk.Entry(top_frame, width='32')
        self.name_entry.bind("<Return>", self.do_ok)
        self.name_entry.bind("<Escape>", self.do_cancel)
        self.name_entry.pack(side='right')
        self.name_entry.focus_set()

        if self.b_rom:
            extra_label = ttk.Label(extra_frame, text='ROM Settings:')
            extra_label.grid(column=0, row=1, sticky='w')
            self.extra_vars = []
            for index, key in enumerate(self.dict_rom_params):
                self.extra_vars.append(tk.IntVar())
                check_1 = ttk.Checkbutton(extra_frame,
                                          text=self.dict_rom_params[key],
                                          variable=self.extra_vars[index],
                                          onvalue=1,
                                          offvalue=0)
                check_1.grid(column=index % 2,
                             row=int(index / 2) + 2,
                             sticky='w')

        ok_button = ttk.Button(bottom_frame,
                               text="OK",
                               default="active",
                               command=self.do_ok)
        ok_button.pack(fill='x', side='right')
        cancel_button = ttk.Button(bottom_frame,
                                   text="Cancel",
                                   command=self.do_cancel)
        cancel_button.pack(fill='x', side='right', padx=10)

        self.top.tk.eval(f'tk::PlaceWindow {self.top._w} center')
        self.top.wait_window()

    def do_ok(self, event=None):  # pylint: disable=unused-argument
        """Process OK Button"""
        self.result_name = self.name_entry.get()
        if self.b_rom:
            for index, key in enumerate(self.dict_rom_params):
                if self.extra_vars[index].get():
                    self.extra += key
        self.top.destroy()

    def do_cancel(self, event=None):  # pylint: disable=unused-argument
        """Process Cancel Button"""
        self.top.destroy()


class InfoWindow:
    """Custom Window to Show Core or ROM info"""
    def __init__(self, parent, str_name, dict_data):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)

        self.top.title('Information')
        self.top.bind("<Return>", self.do_ok)

        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill='both')

        name_frame = ttk.Frame(main_frame, padding=2)
        name_frame.pack(fill='x')
        name_label = ttk.Label(name_frame, text=f'File: {str_name}')
        name_label.pack(side='left')

        kind_frame = ttk.Frame(main_frame, padding=2)
        kind_frame.pack(fill='x')
        kind_label = ttk.Label(kind_frame, text=f'Kind: {dict_data["kind"]}')
        kind_label.pack(side='left')

        if dict_data['version']:
            version_frame = ttk.Frame(main_frame, padding=2)
            version_frame.pack(fill='x')
            version_label = ttk.Label(version_frame,
                                      text=f'Version: {dict_data["version"]}')
            version_label.pack(side='left')

        dict_det = dict_data['detail']
        if dict_det:
            detail_frame = ttk.Frame(main_frame, padding=2)
            detail_frame.pack()
            detail_str = f'{dict_data["kind"]} family features:'
            detail_label = ttk.Label(detail_frame, text=detail_str)
            detail_label.grid(column=0, row=0, sticky='w', pady=1)
            for index, key in enumerate(dict_det):
                detail_str = ', '.join(dict_det[key][0])
                if dict_det[key][1]:
                    detail_str += f' ({dict_det[key][1]})'
                detail_label = ttk.Label(detail_frame,
                                         text=f'  - {key}: {detail_str}')
                detail_label.grid(column=0, row=index + 1, sticky='w')

        #hash_frame = ttk.Frame(main_frame, padding=10)
        #hash_frame.pack(fill='x')
        #hash_label = ttk.Label(hash_frame, text=f'Hash: {dict_data["hash"]}')
        #hash_label.pack(side='left')

        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill='x')
        ok_button = ttk.Button(button_frame,
                               text="OK",
                               default="active",
                               command=self.do_ok)
        ok_button.pack()

        self.top.tk.eval(f'tk::PlaceWindow {self.top._w} center')
        self.top.wait_window()

    def do_ok(self, event=None):  # pylint: disable=unused-argument
        """Process OK Button"""
        self.top.destroy()


if __name__ == "__main__":
    main()
