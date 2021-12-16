#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not modify previous lines. See PEP 8, PEP 263.
"""
Copyright (c) 2021, kounch
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

Extra Window Classes for new entries and info display
"""

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

    def __init__(self, parent, str_name, b_core=False):
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
                               text='OK',
                               default='active',
                               command=self.do_ok)
        ok_button.pack(fill='x', side='right')
        cancel_button = ttk.Button(bottom_frame,
                                   text='Cancel',
                                   command=self.do_cancel)
        cancel_button.pack(fill='x', side='right', padx=10)

        self.top.tk.eval(f'tk::PlaceWindow {self.top._w} center')
        self.top.wait_window()

    def do_ok(self, *_):
        """Process OK Button"""
        self.result_name = self.name_entry.get()
        if self.b_rom:
            for index, key in enumerate(self.dict_rom_params):
                if self.extra_vars[index].get():
                    self.extra += key
        self.top.destroy()

    def do_cancel(self, *_):
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
        self.top.bind('<Return>', self.do_ok)

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

        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill='x')
        ok_button = ttk.Button(button_frame,
                               text='OK',
                               default='active',
                               command=self.do_ok)
        ok_button.pack()

        self.top.tk.eval(f'tk::PlaceWindow {self.top._w} center')
        self.top.wait_window()

    def do_ok(self, *_):
        """Process OK Button"""
        self.top.destroy()
