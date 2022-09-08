# Copyright (c) 2022 kounch
# SPDX-License-Identifier: BSD-2-Clause

find_program(NUITKA_BINARY NAMES nuitka3
	HINTS ${NUITKA_BINARY_PATH})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(nuitka DEFAULT_MSG
                                  NUITKA_BINARY)

mark_as_advanced(NUITKA_BINARY)

set(NUITKA_BINARIES ${NUITKA_BINARY})

if(NOT NUITKA_FOUND)
	MESSAGE(FATAL_ERROR "NUITKA not found")
endif()
