# Copyright (c) 2022-2023 kounch
# SPDX-License-Identifier: BSD-2-Clause

find_program(ASCIIDOCTOR_PDF_BINARY NAMES asciidoctor-pdf
	HINTS ${ASCIIDOCTOR_PDF_BINARY_PATH})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(asciidoctor-pdf DEFAULT_MSG
                                  ASCIIDOCTOR_PDF_BINARY)

mark_as_advanced(ASCIIDOCTOR_PDF_BINARY)

set(ASCIIDOCTOR_PDF_BINARIES ${ASCIIDOCTOR_PDF_BINARY})

if(NOT ASCIIDOCTOR-PDF_FOUND)
	MESSAGE(FATAL_ERROR "asciidoctor-pdf not found")
endif()
