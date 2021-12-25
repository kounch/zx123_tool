#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
# pylint: disable=import-outside-toplevel
"""
Copyright (c) 2021, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

Center tk window Copyright (c) 2019 Jarik Marwede SPDX-License-Identifier: MIT

Extra Window Classes for new entries and info display
"""

import sys
import tkinter as tk
from tkinter import ttk


class NewEntryDialog:
    """Custom Window to Add Core or ROM info"""
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

    def __init__(self, parent, str_name, b_core=False, b_alt=False):
        self.parent = parent

        self.result_name = ''
        self.extra = ''
        self.b_rom = not b_core

        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.resizable(False, False)
        self.top.title(f'New {str_name} Entry')
        self.top.bind('<Return>', self.do_ok)

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
        self.name_entry.bind('<Return>', self.do_ok)
        self.name_entry.bind('<Escape>', self.do_cancel)
        self.name_entry.pack(side='right')
        self.name_entry.focus_set()

        if self.b_rom:
            extra_label = ttk.Label(extra_frame, text='ROM Settings:')
            extra_label.grid(column=0, row=1, sticky='w')
            self.extra_vars = []
            if b_alt:
                self.dict_rom_params['*'] = 'Rooted ROM'
            for index, key in enumerate(self.dict_rom_params):
                str_check = f'({key}) {self.dict_rom_params[key]}'
                self.extra_vars.append(tk.IntVar())
                check_1 = ttk.Checkbutton(extra_frame,
                                          text=str_check,
                                          variable=self.extra_vars[index],
                                          onvalue=1,
                                          offvalue=0)
                check_1.grid(column=index % 2,
                             row=int(index / 2) + 2,
                             sticky='w')

        ok_button = ttk.Button(bottom_frame,
                               text='OK',
                               default='active',
                               command=self.do_ok)
        ok_button.pack(fill='x', side='right')
        cancel_button = ttk.Button(bottom_frame,
                                   text='Cancel',
                                   command=self.do_cancel)
        cancel_button.pack(fill='x', side='right', padx=10)

        center_on_parent(parent, self.top)
        self.top.wait_window()

    def do_ok(self, *_):
        """Process OK Button"""
        self.result_name = self.name_entry.get()
        if self.b_rom:
            for index, key in enumerate(self.dict_rom_params):
                if self.extra_vars[index].get():
                    self.extra += key
        self.top.destroy()
        self.parent.focus_force()

    def do_cancel(self, *_):
        """Process Cancel Button"""
        self.top.destroy()
        self.parent.focus_force()


class InfoWindow:
    """Custom Window to Show Core or ROM info"""
    def __init__(self, parent, str_name, dict_data):
        self.parent = parent

        self.top = tk.Toplevel(parent)
        self.top.resizable(False, False)
        self.top.title('Information')
        self.top.protocol("WM_DELETE_WINDOW", self.do_close)
        self.top.bind("<FocusIn>", self.bind_keys)

        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill='both')

        name_frame = ttk.Frame(main_frame, padding=2)
        name_frame.pack(fill='x')
        name_label = ttk.Label(name_frame, text=f'Item: {str_name}')
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

        center_on_parent(parent, self.top)

    def do_close(self, *_):
        """Process OK Button"""
        self.top.destroy()

    def bind_keys(self, *_):
        """Bind Menu Keys"""
        str_bind = 'Control-'
        if sys.platform == 'win32':
            str_bind = 'Control-'
        elif sys.platform == 'darwin':
            str_bind = 'Command-'

        self.top.bind_all(f'<{str_bind}w>', lambda event: self.do_close())
        self.parent.filemenu.entryconfig(2,
                                         state='normal',
                                         label='Close Info Window',
                                         command=self.do_close)


class ROMPWindow:
    """Custom Window to Show ROMPack Contents"""
    from ._main_gui import create_rom_table
    from ._main_gui import populate_roms

    def __init__(self, parent, str_name, str_kind, dict_roms, default_rom):
        self.parent = parent

        self.top = tk.Toplevel(parent)
        self.top.resizable(False, False)
        self.top.title('ROMPack Contents')
        self.top.protocol("WM_DELETE_WINDOW", self.do_close)
        self.top.bind("<FocusIn>", self.bind_keys)

        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill='both')

        name_frame = ttk.Frame(main_frame, padding=2)
        name_frame.pack(fill='x')
        name_label = ttk.Label(name_frame, text=f'File: {str_name}')
        name_label.pack(side='left')
        kind_label = ttk.Label(name_frame, text=f'Kind: {str_kind}')
        kind_label.pack(side='right')

        self.roms_frame = ttk.Frame(main_frame, padding=5)
        self.roms_frame.pack()
        rom_label = ttk.Label(self.roms_frame,
                              text=f'Default ROM: {default_rom}')
        rom_label.grid(column=0, row=0, columnspan=4, pady=5)
        self.rom_table = self.create_rom_table(height=26)
        self.rom_table.configure(selectmode='none')
        self.populate_roms(dict_roms)

        center_on_parent(parent, self.top)

    def bind_keys(self, *_):
        """Bind Menu Keys"""
        str_bind = 'Control-'
        if sys.platform == 'win32':
            str_bind = 'Control-'
        elif sys.platform == 'darwin':
            str_bind = 'Command-'

        self.top.bind_all(f'<{str_bind}w>', lambda event: self.do_close())
        self.parent.filemenu.entryconfig(2,
                                         state='normal',
                                         label='Close ROMPack Window',
                                         command=self.do_close)

    def romtable_selected(self, *_):
        """Unused"""
        print('Selected ROMPack Treeview')

    def do_close(self, *_):
        """Close window"""
        self.top.destroy()


class ProgressWindow:
    """Custom Window to Show Progress"""
    def __init__(self, parent, str_title):
        self.parent = parent

        self.top = tk.Toplevel(parent)
        self.top.withdraw()
        if sys.platform == 'darwin':
            self.top.tk.call("::tk::unsupported::MacWindowStyle", "style",
                             self.top, "sheet", "noTitleBar")
        self.top.transient(parent)
        self.top.deiconify()
        self.top.grab_set()
        self.top.resizable(False, False)
        self.top.title(str_title)

        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill='both')

        progress_frame = ttk.Frame(main_frame, padding=(25, 30))
        progress_frame.pack()
        progress_label = ttk.Label(progress_frame, text='Updating...')
        progress_label.configure(width=60, anchor="center")
        progress_label.grid(column=0, row=0, columnspan=4, sticky='n')
        self.progress_label = progress_label

        center_on_parent(parent, self.top)

    def update(self, str_message):
        """Update the text of progress_label"""
        self.progress_label.config(text=str_message)
        self.progress_label.update()

    def show(self):
        """Show the window"""
        self.top.lift()
        self.top.update()

    def close(self):
        """Close and destroy window"""
        self.top.destroy()
        self.parent.focus_force()


class PrefWindow:
    """Custom Window to Show Preferences"""
    def __init__(self, parent):
        self.parent = parent

        self.top = tk.Toplevel(parent)
        self.top.resizable(False, False)
        self.top.title('ZX123 Tool Preferences')
        self.top.protocol("WM_DELETE_WINDOW", self.do_close)
        self.top.bind("<FocusIn>", self.bind_keys)
        self.top.bind("<FocusOut>", self.save_prefs)

        main_frame = ttk.Frame(self.top, padding=10)
        main_frame.pack(fill='both')

        settings_frame = ttk.Frame(main_frame, padding=10)
        settings_frame.pack(fill='x')

        self.dict_prefs = {
            'update_json': 'Update Database on startup',
            'check_updates': 'Check for App updates on startup',
            'ask_insert': 'Ask for confirmation when inserting',
            'ask_replace': 'Ask for confirmation when replacing',
            'remember_pos': 'Remember window positions'
        }
        self.extra_vars = []
        for index, key in enumerate(self.dict_prefs):
            self.extra_vars.append(tk.IntVar())
            self.extra_vars[index].set(parent.dict_prefs[key])
            check_1 = ttk.Checkbutton(settings_frame,
                                      text=self.dict_prefs[key],
                                      command=self.save_prefs,
                                      variable=self.extra_vars[index],
                                      onvalue=1,
                                      offvalue=0)
            check_1.grid(column=0, row=index, sticky='w', padx=10, pady=2)

        if self.parent.dict_prefs.get('remember_pos', False):
            self.top.update_idletasks()
            height, width = self.top.winfo_height(), self.top.winfo_width()
            x_pos, y_pos = self.parent.dict_prefs.get(
                'prefwindow', (self.top.winfo_x, self.top.winfo_y))
            self.top.geometry(f'{width}x{height}+{x_pos}+{y_pos}')
        else:
            center_on_parent(parent, self.top)

    def bind_keys(self, *_):
        """Bind Menu Keys"""
        str_bind = 'Control-'
        if sys.platform == 'win32':
            str_bind = 'Control-'
        elif sys.platform == 'darwin':
            str_bind = 'Command-'

        self.top.bind_all(f'<{str_bind}w>', lambda event: self.do_close())
        self.parent.filemenu.entryconfig(2,
                                         state='normal',
                                         label='Close Preferences Window',
                                         command=self.do_close)

    def save_prefs(self, *_):
        """Saves Preferences"""
        for index, key in enumerate(self.dict_prefs):
            self.parent.dict_prefs[key] = self.extra_vars[index].get()

        self.parent.dict_prefs['prefwindow'] = (self.top.winfo_x(),
                                                self.top.winfo_y())
        self.parent.save_prefs()

    def do_close(self, *_):
        """Save Preferences and close window"""
        self.save_prefs()
        self.top.destroy()
        self.parent.pref_window = None
        self.parent.focus_force()


def center_on_parent(root, window):
    """
    Center a window on its parent.
    Obtained from Center tk window library
    https://github.com/jarikmarwede/center-tk-window

    MIT License
    Copyright (c) 2019 Jarik Marwede

    :param root: Reference to parent
    :param window: Reference to window to center
    """
    window.update_idletasks()
    height = window.winfo_height()
    width = window.winfo_width()
    parent = root.nametowidget(window.winfo_parent())
    x_coordinate = int(parent.winfo_x() +
                       (parent.winfo_width() / 2 - width / 2))
    y_coordinate = int(parent.winfo_y() +
                       (parent.winfo_height() / 2 - height / 2))

    window.geometry(f'{width}x{height}+{x_coordinate}+{y_coordinate}')
