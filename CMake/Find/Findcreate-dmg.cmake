# Copyright (c) 2022 kounch
# SPDX-License-Identifier: BSD-2-Clause

find_program(CREATE-DMG_BINARY NAMES create-dmg
	HINTS ${CREATE-DMG_BINARY_PATH})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(create-dmg DEFAULT_MSG
								  CREATE-DMG_BINARY)

mark_as_advanced(CREATE-DMG_BINARY)

set(CREATE-DMG_BINARY ${CREATE-DMG_BINARY})

if(NOT CREATE-DMG_FOUND)
	MESSAGE(FATAL_ERROR "create-dmg not found")
endif()
