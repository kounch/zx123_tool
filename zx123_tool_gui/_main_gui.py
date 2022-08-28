#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
"""
Copyright (c) 2021-2022, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

Main Window Class Creation Methods
"""
import sys
import tkinter as tk
from tkinter import ttk
import webbrowser


def build_menubar(self):
    """Add Menu Bar"""

    help_url = 'https://kounch.github.io/zx123_tool/manual.html'

    str_accl = 'Ctrl+'
    if sys.platform == 'win32':
        # Windows Menu Bar
        str_accl = 'Ctrl+'
    elif sys.platform == 'darwin':
        # MacOS Menu Bar
        str_accl = 'Command+'

    menubar = tk.Menu(self)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label='New Image File…',
                         command=self.new_image,
                         accelerator=f'{str_accl}n')
    filemenu.add_command(label='Open File…',
                         command=self.open_file,
                         accelerator=f'{str_accl}O')
    filemenu.add_command(label='Close File', accelerator=f'{str_accl}w')
    filemenu.add_separator()

    filemenu.add_command(label='Erase Image File…', command=self.erase_image)
    filemenu.add_command(label='Expand Image File…', command=self.expand_image)
    updatemenu = tk.Menu(menubar, tearoff=0)
    updatemenu.add_command(label='Update All (Standard)…',
                           command=lambda: self.update_image('all'))
    updatemenu.add_command(
        label='Update All (ZXUnCore)…',
        command=lambda: self.update_image('all', get_1core=True))
    updatemenu.add_command(
        label='Update All (2MB)…',
        command=lambda: self.update_image('all', get_2mb=True))
    updatemenu.add_separator()
    updatemenu.add_command(label='Update BIOS…',
                           command=lambda: self.update_image('BIOS'))
    updatemenu.add_command(label='Update Spectrum…',
                           command=lambda: self.update_image('Spectrum'))
    updatemenu.add_command(label='Update Cores (Standard)…',
                           command=lambda: self.update_image('Cores'))
    updatemenu.add_command(
        label='Update Cores (ZXUnCore)…',
        command=lambda: self.update_image('Cores', get_1core=True))
    updatemenu.add_command(
        label='Update Cores (2MB)…',
        command=lambda: self.update_image('Cores', get_1core=True))
    self.updatemenu = updatemenu
    filemenu.add_cascade(label='Update Image File', menu=updatemenu)

    filemenu.add_separator()
    filemenu.add_command(label='Get Core Info',
                         command=self.show_core_info,
                         accelerator=f'{str_accl}i')
    filemenu.add_command(label='Rename Core…',
                         command=self.core_rename,
                         accelerator=f'{str_accl}r')
    filemenu.add_command(label='Convert Core…', command=self.convert_core)

    if sys.platform != 'darwin':
        filemenu.add_separator()
        filemenu.add_command(label='Preferences…', command=self.open_prefs)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.destroy)
    self.filemenu = filemenu

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(
        label='Cut',
        accelerator=f'{str_accl}X',
        command=lambda: self.focus_get().event_generate('<<Cut>>'))
    editmenu.add_command(
        label='Copy',
        accelerator=f'{str_accl}C',
        command=lambda: self.focus_get().event_generate('<<Copy>>'))
    editmenu.add_command(
        label='Paste',
        accelerator=f'{str_accl}V',
        command=lambda: self.focus_get().event_generate('<<Paste>>'))

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label='ZX123 Tool Help',
                         command=lambda: webbrowser.open(help_url))
    helpmenu.add_separator()
    helpmenu.add_command(
        label='ZX-Uno Forum',
        command=lambda: webbrowser.open('https://www.zxuno.com/forum/'))
    helpmenu.add_command(label='ZXDOS and ZXDOS+ Forum',
                         command=lambda: webbrowser.open(
                             'https://www.forofpga.es/viewforum.php?f=4'))
    helpmenu.add_separator()
    helpmenu.add_command(label='ZXUNO+ and ZXDOS+ Manuals',
                         command=lambda: webbrowser.open(
                             'https://github.com/zxdos/zxuno/tree/master/doc'))
    helpmenu.add_command(
        label='ZXUno4All Manuals',
        command=lambda: webbrowser.open(
            'https://github.com/spark2k06/ZXUno4ALL/tree/main/doc'))
    helpmenu.add_separator()
    helpmenu.add_command(label='Check for App updates…',
                         command=lambda: self.check_updates(confirm=True))

    menubar.add_cascade(label='File', menu=self.filemenu)
    menubar.add_cascade(label='Edit', menu=editmenu)
    menubar.add_cascade(label='Help', menu=helpmenu)
    self.menubar = menubar
    self.config(menu=menubar)

    core_menu = tk.Menu(self, tearoff=0)
    core_menu.add_command(label="Show Info", command=self.show_core_info)
    core_menu.add_command(label="Rename", command=self.core_rename)
    self.core_menu = core_menu

    rom_menu = tk.Menu(self, tearoff=0)
    rom_menu.add_command(label="Rename", command=self.rom_rename)
    self.rom_menu = rom_menu

    json_menu = tk.Menu(self, tearoff=0)
    json_menu.add_command(label="Update Database", command=self.update_json)
    json_menu.add_separator()
    json_menu.add_command(label="Show statistics")
    self.json_menu = json_menu

    if sys.platform == 'darwin':
        #self.createcommand('tk::mac::ShowPreferences', showPreferences)
        self.createcommand('::tk::mac::ShowHelp',
                           lambda: webbrowser.open(help_url))

    self.filemenu.entryconfig(2, state='disabled')
    self.filemenu.entryconfig(4, state='disabled')
    self.filemenu.entryconfig(5, state='disabled')
    self.filemenu.entryconfig(6, state='disabled')
    self.filemenu.entryconfig(8, state='disabled')
    self.filemenu.entryconfig(9, state='disabled')
    self.core_menu.entryconfig(0, state='disabled')
    self.core_menu.entryconfig(1, state='disabled')
    self.rom_menu.entryconfig(0, state='disabled')
    self.json_menu.entryconfig(2, state='disabled')


def bind_keys(self, *_):
    """Bind Menu Keys"""

    str_bind = 'Control-'
    if sys.platform == 'win32':
        str_bind = 'Control-'
    elif sys.platform == 'darwin':
        str_bind = 'Command-'

    self.bind_all(f'<{str_bind}n>', lambda event: self.new_image())
    self.bind_all(f'<{str_bind}o>', lambda event: self.open_file())
    self.bind_all(f'<{str_bind}i>', lambda event: self.show_core_info())
    self.bind_all(f'<{str_bind}r>', lambda event: self.core_rename())

    if self.zxfilepath:
        self.filemenu.entryconfig(2,
                                  state='normal',
                                  label='Close file',
                                  command=self.full_close_image)
        self.bind_all(f'<{str_bind}w>', lambda event: self.full_close_image())
    else:
        self.filemenu.entryconfig(2,
                                  state='disabled',
                                  label='Close file',
                                  command=None)
        self.unbind_all(f'<{str_bind}w>')


def core_menu_popup(self, event):
    """Contextual Menu Handling for core table"""
    try:
        self.core_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        self.core_menu.grab_release()


def rom_menu_popup(self, event):
    """Contextual Menu Handling for ROM table"""
    try:
        self.rom_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        self.rom_menu.grab_release()


def json_menu_popup(self, event):
    """Contextual Menu Handling for JSON Version Label"""
    try:
        self.json_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        self.json_menu.grab_release()


def create_labels(self):
    """
    Create Main Window Labels
    :return: reference to image_label
    """

    image_label = ttk.Label(self.blocks_frame, text='No Image File')
    image_label.grid(column=0, row=0, columnspan=7, sticky='n')

    version_label = None
    if 'version' in self.fulldict_hash:
        version_label = ttk.Label(
            self.blocks_frame,
            font=('TkDefaultFont', 9),
            text=f'Database: {self.fulldict_hash["version"]}')
        version_label.grid(column=7, row=0, columnspan=8, sticky='ne')
        version_label.bind('<Shift-Button-2>', self.json_menu_popup)
        version_label.bind('<Shift-Button-3>', self.json_menu_popup)

    bios_label = ttk.Label(self.blocks_frame, text='BIOS:', padding=5)
    bios_label.grid(column=0, row=1, sticky='e')

    esxdos_label = ttk.Label(self.blocks_frame, text='esxdos:', padding=5)
    esxdos_label.grid(column=4, row=1, sticky='e')

    spectrum_label = ttk.Label(self.blocks_frame,
                               text='ZX Spectrum Core:',
                               padding=5)
    spectrum_label.grid(column=0, row=2, sticky='e')

    cores_label = ttk.Label(self.cores_frame, text='Cores')
    cores_label.grid(column=0, row=0, sticky='w')

    core_label = ttk.Label(self.cores_frame, text='Default Core:', padding=5)
    core_label.grid(column=3, row=1, sticky='e')

    boot_label = ttk.Label(self.cores_frame, text='Boot Timer:', padding=5)
    boot_label.grid(column=3, row=2, sticky='e')

    keyboard_label = ttk.Label(self.cores_frame,
                               text='Keyboard Layout:',
                               padding=5)
    keyboard_label.grid(column=3, row=3, sticky='e')

    video_label = ttk.Label(
        self.cores_frame,
        text='Video Mode:',
        padding=5,
    )
    video_label.grid(column=3, row=4, sticky='e')

    rom_label = ttk.Label(self.cores_frame, text='Default ROM:', padding=5)
    rom_label.grid(column=3, row=5, sticky='e')

    roms_label = ttk.Label(self.roms_frame, text='ROMs')
    roms_label.grid(column=0, row=0, sticky='w')

    return image_label, version_label


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
    core_spinbox = ttk.Spinbox(self.cores_frame,
                               from_=1,
                               to=1,
                               wrap=False,
                               width=4,
                               state='disabled',
                               command=self.changed_core_spinbox,
                               textvariable=self.default_core)
    core_spinbox.grid(column=4, row=1, sticky='e')
    core_spinbox.bind('<Return>', self.set_default_core)
    core_spinbox.bind('<FocusOut>', self.set_default_core)
    self.core_spinbox = core_spinbox

    self.default_timer = tk.StringVar()
    timer_spinbox = ttk.Spinbox(self.cores_frame,
                                from_=0,
                                to=4,
                                wrap=False,
                                width=4,
                                state='disabled',
                                command=self.changed_timer_spinbox,
                                textvariable=self.default_timer)
    timer_spinbox.grid(column=4, row=2, sticky='e')
    timer_spinbox.bind('<Return>', self.set_default_timer)
    timer_spinbox.bind('<FocusOut>', self.set_default_timer)
    self.timer_spinbox = timer_spinbox

    self.default_keyboard = tk.StringVar()
    keyboard_spinbox = ttk.Spinbox(self.cores_frame,
                                   from_=0,
                                   to=3,
                                   wrap=False,
                                   width=4,
                                   state='disabled',
                                   command=self.changed_keyboard_spinbox,
                                   textvariable=self.default_keyboard)
    keyboard_spinbox.grid(column=4, row=3, sticky='e')
    keyboard_spinbox.bind('<Return>', self.set_default_keyboard)
    keyboard_spinbox.bind('<FocusOut>', self.set_default_keyboard)
    self.keyboard_spinbox = keyboard_spinbox

    self.default_video = tk.StringVar()
    video_spinbox = ttk.Spinbox(self.cores_frame,
                                from_=0,
                                to=2,
                                wrap=False,
                                width=4,
                                state='disabled',
                                command=self.changed_video_spinbox,
                                textvariable=self.default_video)
    video_spinbox.grid(column=4, row=4, sticky='e')
    video_spinbox.bind('<Return>', self.set_default_video)
    video_spinbox.bind('<FocusOut>', self.set_default_video)
    self.video_spinbox = video_spinbox

    self.default_rom = tk.StringVar()
    rom_spinbox = ttk.Spinbox(self.cores_frame,
                              from_=0,
                              to=0,
                              wrap=False,
                              width=4,
                              state='disabled',
                              command=self.changed_rom_spinbox,
                              textvariable=self.default_rom)
    rom_spinbox.grid(column=4, row=5, sticky='e')
    rom_spinbox.bind('<Return>', self.set_default_rom)
    rom_spinbox.bind('<FocusOut>', self.set_default_rom)
    self.rom_spinbox = rom_spinbox


def create_core_table(self):
    """
    Create Main Window Tables
    :return: References to core_table and rom_table
    """
    style = ttk.Style()
    style.configure('Treeview.Cell', borderwidth=1)

    core_table = ttk.Treeview(self.cores_frame, height=11)
    core_table.grid(column=0, row=1, columnspan=3, rowspan=8, sticky='nsw')
    core_table['columns'] = ('id', 'name', 'core', 'version')
    core_table.column('#0', width=0, stretch=tk.NO)
    core_table.heading('#0', text='', anchor=tk.CENTER)
    col_sizes = [30, 240, 200, 250]
    for index, col_name in enumerate(core_table['columns']):
        core_table.column(col_name, anchor=tk.W, width=col_sizes[index])
        core_table.heading(col_name, text=col_name.upper(), anchor=tk.CENTER)
    core_table.bind('<<TreeviewSelect>>', self.coretable_selected)
    core_table.bind('<Button-2>', self.core_menu_popup)
    core_table.bind('<Button-3>', self.core_menu_popup)

    core_scrollbar = ttk.Scrollbar(self.cores_frame,
                                   orient=tk.VERTICAL,
                                   command=core_table.yview)
    core_table.configure(yscroll=core_scrollbar.set)
    core_scrollbar.grid(column=2, row=1, rowspan=8, sticky='nse')

    return core_table


def create_rom_table(self, height=11):
    """
    Create ROMs Table
    :return: Reference to rom_table
    """
    rom_table = ttk.Treeview(self.roms_frame, height=height)
    rom_table.grid(column=0, row=1, columnspan=4, sticky='nswe')
    rom_table['columns'] = ('id', 'slot', 'flags', 'crc', 'name', 'size',
                            'version')
    rom_table.column('#0', width=0, stretch=tk.NO)
    rom_table.heading('#0', text='', anchor=tk.CENTER)
    col_sizes = [30, 30, 80, 155, 280, 40, 300]
    for index, col_name in enumerate(rom_table['columns']):
        rom_table.column(col_name, anchor=tk.W, width=col_sizes[index])
        rom_table.heading(col_name, text=col_name.upper(), anchor=tk.CENTER)
    rom_table.bind('<<TreeviewSelect>>', self.romtable_selected)
    rom_table.bind('<Button-2>', self.rom_menu_popup)
    rom_table.bind('<Button-3>', self.rom_menu_popup)

    rom_scrollbar = ttk.Scrollbar(self.roms_frame,
                                  orient=tk.VERTICAL,
                                  command=rom_table.yview)
    rom_table.configure(yscroll=rom_scrollbar.set)
    rom_scrollbar.grid(column=3, row=1, sticky='nse')

    return rom_table


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
                                      state='disabled',
                                      command=self.esxdos_export)
    esxdos_export_button.grid(column=7, row=1, columnspan=2, sticky='we')
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
                                    text='Add New Core',
                                    state='disabled',
                                    command=self.core_import)
    core_import_button.grid(column=3,
                            row=7,
                            columnspan=2,
                            sticky='we',
                            padx=10)
    self.core_import_button = core_import_button

    core_export_button = ttk.Button(self.cores_frame,
                                    text='Export Core',
                                    state='disabled',
                                    command=self.core_export)
    core_export_button.grid(column=3,
                            row=8,
                            columnspan=2,
                            sticky='we',
                            padx=10)
    self.core_export_button = core_export_button

    rom_import_button = ttk.Button(self.roms_frame,
                                   text='Add New ROM',
                                   state='disabled')
    rom_import_button.grid(column=0, row=2, sticky='we', padx=5, pady=10)
    rom_import_button.bind("<Button-1>", self.rom_import_n)
    rom_import_button.bind("<Shift-Button-1>", self.rom_import_y)
    self.rom_import_button = rom_import_button

    rom_export_button = ttk.Button(self.roms_frame,
                                   text='Export ROM',
                                   state='disabled',
                                   command=self.rom_export)
    rom_export_button.grid(column=1, row=2, sticky='we', padx=5, pady=10)
    self.rom_export_button = rom_export_button

    rompack_import_button = ttk.Button(self.roms_frame,
                                       text='Import ROMPack...',
                                       state='disabled',
                                       command=self.rompack_import)
    rompack_import_button.grid(column=2, row=2, sticky='we', padx=5, pady=10)
    self.rompack_import_button = rompack_import_button

    rompack_export_button = ttk.Button(self.roms_frame,
                                       text='Export ROMPack...',
                                       state='disabled',
                                       command=self.rompack_export)
    rompack_export_button.grid(column=3, row=2, sticky='we', padx=5, pady=10)
    self.rompack_export_button = rompack_export_button


def populate_cores(self, dict_cores):
    """
    Populate Cores Data Table (TreeView) in Main Window
    :param dict_cores: Dictionary with cores data
    """
    for index in dict_cores:
        self.core_table.insert(parent='',
                               index='end',
                               iid=index,
                               text='',
                               values=[index] + list(dict_cores[index])[:3])


def populate_roms(self, dict_roms):
    """
    Populate ROMs Data Table (TreeView) in Main Window
    :param dict_roms: Dictionary with ROMs data
    """
    for index in dict_roms:
        self.rom_table.insert(parent='',
                              index='end',
                              iid=index,
                              text='',
                              values=[index] + list(dict_roms[index])[:6])


def changed_bios_spinbox(self, bios_value, min_val, max_val):  # pylint: disable=unused-argument
    """
    Process default bios setting change event, and enforce limits if needed
    :param bios_value: Variable associated to spinbox content
    :param min_val: Minimum valid value
    :param max_val: Maximum valid value
    """
    new_val = bios_value.get()
    if new_val.isnumeric():
        new_val = int(new_val)
        new_val = max(new_val, min_val)
        new_val = min(new_val, max_val)
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


def process_selected(self, treeview, treeview_menu, import_bttn, export_bttn,
                     str_text):
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
            str_label = 'Show info'
            n_entry = 0
            if treeview_menu == self.core_menu:
                self.filemenu.entryconfig(8, state='disabled', label=str_label)
                treeview_menu.entryconfig(n_entry,
                                          state='disabled',
                                          label=str_label)
                n_entry = 1
            str_label = 'Rename'
            if treeview_menu == self.core_menu:
                self.filemenu.entryconfig(9, state='disabled', label=str_label)
            treeview_menu.entryconfig(n_entry,
                                      state='disabled',
                                      label=str_label)
        else:
            export_bttn['text'] = f'Export {str_text} {t_selection[0]}'
            n_entry = 0
            if treeview_menu == self.core_menu:
                str_label = f'Show info for {str_text} {t_selection[0]}'
                self.filemenu.entryconfig(8, state='normal', label=str_label)
                treeview_menu.entryconfig(n_entry,
                                          state='normal',
                                          label=str_label)
                n_entry = 1
            str_label = f'Rename {str_text} {t_selection[0]}'
            if treeview_menu == self.core_menu:
                self.filemenu.entryconfig(9, state='normal', label=str_label)
            treeview_menu.entryconfig(n_entry, state='normal', label=str_label)
    else:
        import_bttn['text'] = f'Add New {str_text}'
        export_bttn['text'] = f'Export {str_text}'
        export_bttn.state(['disabled'])
        str_label = 'Show info'
        n_entry = 0
        if treeview_menu == self.core_menu:
            self.filemenu.entryconfig(8, state='disabled', label=str_label)
            treeview_menu.entryconfig(n_entry,
                                      state='disabled',
                                      label=str_label)
            n_entry = 1
        str_label = 'Rename'
        if treeview_menu == self.core_menu:
            self.filemenu.entryconfig(9, state='disabled', label=str_label)
        treeview_menu.entryconfig(n_entry, state='disabled', label=str_label)


def coretable_selected(self, *_):
    """
    Configure Cores Data Table buttons depending on selected cores
    """
    self.process_selected(self.core_table, self.core_menu,
                          self.core_import_button, self.core_export_button,
                          'Core')


def romtable_selected(self, *_):
    """
    Configure ROMs Data Table buttons depending on selected ROMs
    """
    self.process_selected(self.rom_table, self.rom_menu,
                          self.rom_import_button, self.rom_export_button,
                          'ROM')
