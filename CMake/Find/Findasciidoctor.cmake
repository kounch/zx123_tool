# Copyright (c) 2022-2023 kounch
# SPDX-License-Identifier: BSD-2-Clause

find_program(ASCIIDOCTOR_BINARY NAMES asciidoctor
	HINTS ${ASCIIDOCTOR_BINARY_PATH})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(asciidoctor DEFAULT_MSG
                                  ASCIIDOCTOR_BINARY)

mark_as_advanced(ASCIIDOCTOR_BINARY)

set(ASCIIDOCTOR_BINARIES ${ASCIIDOCTOR_BINARY})

if(NOT ASCIIDOCTOR_FOUND)
	MESSAGE(FATAL_ERROR "asciidoctor not found")
endif()
