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
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

import zx123_tool as zx123

MY_DIRPATH = os.path.dirname(sys.argv[0])
MY_DIRPATH = os.path.abspath(MY_DIRPATH)


def main():
    """Principal"""
    app = App()
    app.mainloop()


class App(tk.Tk):
    """Main GUI"""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__()

        # Initialize JSON Database
        self.fulldict_hash = zx123.load_json_bd()
        self.zxfilepath = ''

        # MacOS Open File Events
        self.createcommand("::tk::mac::OpenDocument", self.load_file)

        # MacOS Menu Bar
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image File...",
                             command=self.load_file,
                             accelerator="Command+o")
        self.bind_all("<Command-o>", lambda event: self.load_file())
        filemenu.add_command(label="Close Image File",
                             command=self.clear_image)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        # Main Window
        self.title('ZX123 Tool')
        self.resizable(False, False)

        self.blocks_frame = ttk.Frame(self, padding=10)
        self.cores_frame = ttk.Frame(self, padding=10)
        self.roms_frame = ttk.Frame(self, padding=10)

        self.image_label = self.create_labels()
        self.create_entries()
        self.core_table, self.rom_table = self.create_tables()
        self.create_buttons()

        self.blocks_frame.grid(column=0, row=1, sticky='nsew')
        self.cores_frame.grid(column=0, row=2, sticky='nsew')
        self.roms_frame.grid(column=0, row=3, sticky='nsew')

        self.update()

        # Load files from command line args
        if len(sys.argv) > 1:
            self.load_file(sys.argv[1:])

    def create_labels(self):
        "Create Main Window Labels"

        image_label = ttk.Label(self.blocks_frame, text='No Image File')
        image_label.grid(row=0, column=0, columnspan=6, sticky='n')

        bios_label = ttk.Label(self.blocks_frame, text='BIOS:', padding=10)
        bios_label.grid(row=1, column=0, sticky='e')

        esxdos_label = ttk.Label(self.blocks_frame, text='esxdos:', padding=10)
        esxdos_label.grid(row=1, column=4, sticky='e')

        spectrum_label = ttk.Label(self.blocks_frame,
                                   text='ZX Spectrum Core:',
                                   padding=10)
        spectrum_label.grid(row=2, column=0, sticky='e')

        cores_label = ttk.Label(self.cores_frame, text='Cores')
        cores_label.grid(row=0, column=0, sticky='w')

        core_label = ttk.Label(self.cores_frame,
                               text='Default Core:',
                               padding=10,
                               width=12)
        core_label.grid(row=1, column=3, sticky='e')

        boot_label = ttk.Label(self.cores_frame,
                               text='Boot Timer:',
                               padding=10,
                               width=12)
        boot_label.grid(row=2, column=3, sticky='e')

        keyboard_label = ttk.Label(self.cores_frame,
                                   text='Keyboard Layout:',
                                   padding=10,
                                   width=12)
        keyboard_label.grid(row=3, column=3, sticky='e')

        video_label = ttk.Label(self.cores_frame,
                                text='Video Mode:',
                                padding=10,
                                width=12)
        video_label.grid(row=4, column=3, sticky='e')

        rom_label = ttk.Label(self.cores_frame,
                              text='Default ROM:',
                              padding=10,
                              width=12)
        rom_label.grid(row=8, column=3, sticky='e')

        roms_label = ttk.Label(self.roms_frame, text='ROMs')
        roms_label.grid(row=0, column=0, sticky='w')

        return image_label

    def create_entries(self):
        """Create Main Window Input Fields"""

        self.bios = tk.StringVar()
        bios_entry = ttk.Entry(self.blocks_frame,
                               width=10,
                               state='disabled',
                               textvariable=self.bios)
        bios_entry.grid(row=1, column=1, sticky='w')

        self.esxdos = tk.StringVar()
        esxdos_entry = ttk.Entry(self.blocks_frame,
                                 width=8,
                                 state='disabled',
                                 textvariable=self.esxdos)
        esxdos_entry.grid(row=1, column=5, sticky='w')

        self.spectrum = tk.StringVar()
        spectrum_entry = ttk.Entry(self.blocks_frame,
                                   state='disabled',
                                   textvariable=self.spectrum)
        spectrum_entry.grid(row=2, column=1, columnspan=5, sticky='we')
        self.spectrum_entry = spectrum_entry

        self.default_core = tk.StringVar()
        core_spin_box = ttk.Spinbox(self.cores_frame,
                                    from_=2,
                                    to=39,
                                    wrap=False,
                                    width=4,
                                    state='disabled',
                                    textvariable=self.default_core)
        core_spin_box.grid(row=1, column=4, sticky='e')

        self.default_timer = tk.StringVar()
        timer_spin_box = ttk.Spinbox(self.cores_frame,
                                     from_=0,
                                     to=3,
                                     wrap=False,
                                     width=4,
                                     state='disabled',
                                     textvariable=self.default_timer)
        timer_spin_box.grid(row=2, column=4, sticky='e')

        self.default_keyboard = tk.StringVar()
        keyboard_spin_box = ttk.Spinbox(self.cores_frame,
                                        from_=0,
                                        to=3,
                                        wrap=False,
                                        width=4,
                                        state='disabled',
                                        textvariable=self.default_keyboard)
        keyboard_spin_box.grid(row=3, column=4, sticky='e')

        self.default_video = tk.StringVar()
        video_spin_box = ttk.Spinbox(self.cores_frame,
                                     from_=0,
                                     to=2,
                                     wrap=False,
                                     width=4,
                                     state='disabled',
                                     textvariable=self.default_video)
        video_spin_box.grid(row=4, column=4, sticky='e')

        self.default_rom = tk.StringVar()
        rom_spin_box = ttk.Spinbox(self.cores_frame,
                                   from_=0,
                                   to=2,
                                   wrap=False,
                                   width=4,
                                   state='disabled',
                                   textvariable=self.default_rom)
        rom_spin_box.grid(row=8, column=4, sticky='e')

    def create_tables(self):
        """Create Main Window Tables"""
        style = ttk.Style()
        style.configure("Treeview.Cell", borderwidth=1)

        core_table = ttk.Treeview(self.cores_frame, height=15)
        core_table.grid(row=1, column=0, rowspan=8, columnspan=3, sticky='nsw')
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
        core_scrollbar.grid(row=1, column=2, rowspan=8, sticky='nse')

        rom_table = ttk.Treeview(self.roms_frame, height=15)
        rom_table.grid(row=1, column=0, columnspan=4, sticky='nsew')
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
        rom_scrollbar.grid(row=1, column=3, sticky='nse')

        return core_table, rom_table

    def create_buttons(self):
        """Create Main Window buttons"""
        bios_import_button = ttk.Button(self.blocks_frame,
                                        text='Import BIOS',
                                        state='disabled',
                                        command=self.bios_import)
        bios_import_button.grid(row=1, column=2, sticky='we')
        self.bios_import_button = bios_import_button

        bios_export_button = ttk.Button(self.blocks_frame,
                                        text='Export BIOS',
                                        state='disabled',
                                        command=self.bios_export)
        bios_export_button.grid(row=1, column=3, sticky='we')
        self.bios_export_button = bios_export_button

        esxdos_import_button = ttk.Button(self.blocks_frame,
                                          text='Import esxdos',
                                          state='disabled',
                                          command=self.esxdos_import)
        esxdos_import_button.grid(row=1, column=6, sticky='we')
        self.esxdos_import_button = esxdos_import_button

        esxdos_export_button = ttk.Button(self.blocks_frame,
                                          text='Export esxdos',
                                          width=13,
                                          state='disabled',
                                          command=self.esxdos_export)
        esxdos_export_button.grid(row=1, column=7, sticky='we')
        self.esxdos_export_button = esxdos_export_button

        spectrum_import_button = ttk.Button(self.blocks_frame,
                                            text='Import Spectrum',
                                            state='disabled',
                                            command=self.spectrum_import)
        spectrum_import_button.grid(row=2, column=6, sticky='we')
        self.spectrum_import_button = spectrum_import_button

        spectrum_export_button = ttk.Button(self.blocks_frame,
                                            text='Export Spectrum',
                                            state='disabled',
                                            command=self.spectrum_export)
        spectrum_export_button.grid(row=2, column=7, columnspan=2, sticky='we')
        self.spectrum_export_button = spectrum_export_button

        core_import_button = ttk.Button(self.cores_frame,
                                        text='Import Core',
                                        state='disabled',
                                        width=17,
                                        command=self.core_import)
        core_import_button.grid(row=5, column=3, columnspan=2, sticky='e')
        self.core_import_button = core_import_button

        core_export_button = ttk.Button(self.cores_frame,
                                        text='Export Core',
                                        state='disabled',
                                        width=17,
                                        command=self.core_export)
        core_export_button.grid(row=6, column=3, columnspan=2, sticky='e')
        self.core_export_button = core_export_button

        rename_core_button = ttk.Button(self.cores_frame,
                                        text='Rename Core',
                                        state='disabled',
                                        width=17,
                                        command=self.load_file)
        rename_core_button.grid(row=7, column=3, columnspan=2, sticky='e')
        self.rename_core_button = rename_core_button

        rom_import_button = ttk.Button(self.roms_frame,
                                       text='Import ROM',
                                       state='disabled',
                                       command=self.rom_import)
        rom_import_button.grid(row=3, column=0, sticky='w', pady=10)
        self.rom_import_button = rom_import_button

        rom_export_button = ttk.Button(self.roms_frame,
                                       text='Export ROM',
                                       state='disabled',
                                       command=self.rom_export)
        rom_export_button.grid(row=3, column=1, sticky='w', pady=10)
        self.rom_export_button = rom_export_button

        rompack_button = ttk.Button(self.roms_frame,
                                    text='Import ROMPack...',
                                    state='disabled',
                                    command=self.rompack_import)
        rompack_button.grid(row=3, column=2, sticky='sw', pady=10)
        self.rompack_button = rompack_button

        clear_button = ttk.Button(self.roms_frame,
                                  text='Close Image File',
                                  command=self.clear_image)
        clear_button.grid(row=3, column=3, sticky='se', pady=10)

    def clear_image(self):
        """Empty all fields of Main Window"""

        self.zxfilepath = ''
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

    def load_file(self, *args):
        """Open only first file"""
        if args:
            str_file = args[0]
        else:
            filetypes = [("ZX1, ZX2 or ZXD files", ".zx1 .zx2 .zxd")]
            str_file = fd.askopenfilename(parent=self,
                                          title='Open a ZX1, ZX2, ZXD file',
                                          filetypes=filetypes)

        if str_file:
            str_filename = os.path.split(str_file)[1]
            str_extension, dict_hash, filetype = zx123.detect_file(
                str_file, self.fulldict_hash)

            if filetype == 'FlashImage':
                self.clear_image()
                self.zxfilepath = str_file
                self.zxextension = str_extension

                dict_flash = zx123.list_zxdata(str_file, dict_hash, False)
                dict_roms = zx123.list_romsdata(str_file, self.fulldict_hash,
                                                str_extension, False)
                str_filename = f'{str_filename} ({dict_flash["description"]})'
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
                #self.core_import_button.state(["!disabled"])
                self.rompack_button.state(["!disabled"])
            elif filetype == 'ROMPack v2':
                print('ROMPack V2')
                messagebox.showinfo("ROMPackv2", str_filename, parent=self)
            else:
                print('Undetermined')
                messagebox.showinfo("Another File", str_filename, parent=self)

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

    def coretable_selected(self, event):  # pylint: disable=unused-argument
        """Configure buttons depending on selected cores"""
        t_selection = self.core_table.selection()
        if t_selection:
            self.core_export_button.state(["!disabled"])
        else:
            self.core_export_button.state(["disabled"])  # Disable the button.
        if len(t_selection) > 1:
            self.core_export_button['text'] = 'Export Cores'
        else:
            self.core_export_button['text'] = 'Export Core'

    def romtable_selected(self, event):  # pylint: disable=unused-argument
        """Configure buttons depending on selected ROMs"""
        t_selection = self.rom_table.selection()
        if t_selection:
            self.rom_export_button.state(["!disabled"])
        else:
            self.rom_export_button.state(["disabled"])  # Disable the button.
        if len(t_selection) > 1:
            self.rom_export_button['text'] = 'Export ROMs'
        else:
            self.rom_export_button['text'] = 'Export ROM'

    def block_import(self, str_block):
        """Generic block import method"""
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
            self.load_file(self.zxfilepath)

    def block_export(self, str_block):
        """Generic block export method"""
        str_directory = os.path.dirname(self.zxfilepath)
        str_directory = fd.askdirectory(
            parent=self,
            initialdir=str_directory,
            title=f'Select {str_block} Export Path')
        if str_directory:
            zx123.extractfrom_zxdata(self.zxfilepath, str_block,
                                     self.fulldict_hash, str_directory,
                                     self.zxextension, True)

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

    def core_export(self):
        """Proxy for secondary Core export action"""
        self.multi_export('Core', self.core_table, True)

    def core_import(self):
        """Core import action"""
        filetypes = [("ZX1, ZX2 or ZXD files", ".zx1 .zx2 .zxd")]
        str_file = fd.askopenfilename(parent=self,
                                      title='Open a ZX1, ZX2, ZXD file',
                                      filetypes=filetypes)

        if str_file:
            messagebox.showinfo("Core", f"Import {str_file}", parent=self)

    def rom_import(self):
        """ROM import action"""
        messagebox.showinfo("ROM",
                            "Import ROM (Not implemented)",
                            parent=self)

    def rom_export(self):
        """Proxy for ROM export action"""
        self.multi_export('ROM', self.rom_table, False)

    def rompack_import(self):
        """"ROMPack v1 imort action"""
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
            self.load_file(self.zxfilepath)


if __name__ == "__main__":
    main()
