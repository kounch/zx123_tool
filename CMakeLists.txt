# Copyright (c) 2022 kounch
# SPDX-License-Identifier: BSD-2-Clause

cmake_minimum_required(VERSION 3.24)
project("ZX123 Tool")

set(BASENAME ${PROJECT_NAME})
set(OUTPUT_DIR ${CMAKE_BINARY_DIR})

execute_process(
    COMMAND python3 zx123_tool.py --version
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    OUTPUT_VARIABLE VERSIONSTR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )
if (VERSIONSTR)
    string(REGEX MATCH "zx123_tool.py (.*)" _ ${VERSIONSTR})
    set(VERSION ${CMAKE_MATCH_1})
else()
    message(FATAL_ERROR "Cannot determine ZX123 Tool version")
endif()


list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/CMake/Find")

find_package(nuitka)

if (WIN32)
    SET_TARGET_PROPERTIES(zx213gui
    PROPERTIES
    OUTPUT_NAME "ZX123 Tool.exe"
    )
elseif (APPLE)
    set(APP_NAME "ZX123 Tool.app")
    set(ARCH_TO_BUILD "arm64" )
    set(APP_CONTENT "${PROJECT_SOURCE_DIR}/MacOS")
    set(APP_RESOURCES "${APP_CONTENT}/Resources")

    find_package(asciidoctor)
    find_package(asciidoctor-pdf)
endif()

add_custom_target(zx213gui ALL
    DEPENDS ${OUTPUT_DIR}/docs
    )

function(MAKE_PDF PDF_LANG)
    if(PDF_LANG STREQUAL "es")
        set(PDF_NAME "Manual de ZX123 Tool.pdf")
    else()
        set(PDF_NAME "ZX123 Tool Manual.pdf")
    endif()

    add_custom_target("pdfdocs_${PDF_LANG}" ALL
        DEPENDS ${OUTPUT_DIR}/${PDF_NAME}
    )
    add_custom_command(OUTPUT ${OUTPUT_DIR}/${PDF_NAME}
        DEPENDS ${PROJECT_SOURCE_DIR}/locale/${PDF_LANG}/index.adoc
        COMMAND ${ASCIIDOCTOR_PDF_BINARY} -a pdf-stylesdir=${PROJECT_SOURCE_DIR}/locale -a pdf-style=style.yml -o ${PDF_DIR}/${PDF_NAME} ${PROJECT_SOURCE_DIR}/locale/${PDF_LANG}/index.adoc
        COMMENT "Generating ${PDF_LANG} Docs"
    )
endfunction()   

if(ASCIIDOCTOR-PDF_FOUND)
    message("Prepare docs build")
    set(PDF_DIR "${OUTPUT_DIR}/docs")
    file(MAKE_DIRECTORY ${PDF_DIR})

    make_pdf("es")
    make_pdf("en")

    add_custom_target(extra_docs ALL
        DEPENDS ${OUTPUT_DIR}/docs
    )
    set(EXTRA_DOCS
        ${PROJECT_SOURCE_DIR}/LICENSE
        ${PROJECT_SOURCE_DIR}/README.md
    )
    foreach(file_i ${EXTRA_DOCS})
        add_custom_command(TARGET extra_docs
            COMMAND ${CMAKE_COMMAND} ARGS -E copy ${file_i} ${OUTPUT_DIR}/docs
        )
    endforeach(file_i)
endif()

function(BUILD_MAC ARCH_TO_BUILD)
    set(MAC_BUILD_DIR "${OUTPUT_DIR}/mac_${ARCH_TO_BUILD}")
    file(MAKE_DIRECTORY ${MAC_BUILD_DIR})

    add_custom_target("zx213gui_mac_${ARCH_TO_BUILD}" ALL
        DEPENDS ${MAC_BUILD_DIR}/${APP_NAME}
        )
    add_custom_command(OUTPUT ${MAC_BUILD_DIR}/${APP_NAME}
        DEPENDS ${PROJECT_SOURCE_DIR}/${BASENAME}.py
        COMMAND ${NUITKA_BINARY} ${PROJECT_SOURCE_DIR}/${BASENAME}.py --output-dir=${MAC_BUILD_DIR} --standalone --lto=yes --enable-plugin=tk-inter --macos-target-arch=${ARCH_TO_BUILD} --macos-disable-console --macos-create-app-bundle --macos-app-icon=${APP_RESOURCES}/${BASENAME}.icns --macos-signed-app-name="zx123_tool.kounch.github.io" --macos-app-version=${VERSION} --quiet
        COMMENT "Building ${ARCH_TO_BUILD} Binary"
        )

    set(EXTRA_CONTENT
        ${PROJECT_SOURCE_DIR}/zx123_hash.json
        ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZX1.zip
        ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZX2.zip
        ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZXD.zip
        ${PROJECT_SOURCE_DIR}/ROMS_255_Empty.ZX1.zip
        )
    foreach(file_i ${EXTRA_CONTENT})
        add_custom_command(TARGET "zx213gui_mac_${ARCH_TO_BUILD}" POST_BUILD
            COMMAND ${CMAKE_COMMAND} ARGS -E copy ${file_i} ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        )
    endforeach(file_i)

    add_custom_command(TARGET "zx213gui_mac_${ARCH_TO_BUILD}" POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${APP_RESOURCES} ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        COMMAND ${CMAKE_COMMAND} -E copy ${APP_CONTENT}/Info.plist ${MAC_BUILD_DIR}/${APP_NAME}/Contents
        COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/zx123_hash.json ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        COMMAND sed -i '' "s/VERSION_STRING/${VERSION}/" ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Info.plist
        COMMAND install_name_tool -change '/Library/Frameworks/Python.framework/Versions/3.10/Python' '@executable_path/Python' ${MAC_BUILD_DIR}/${APP_NAME}/Contents/MacOS/${PROJECT_NAME}
        )
endfunction()

if(NUITKA_FOUND)
    message("Prepare binary build")

    build_mac("arm64")
    build_mac("x86_64")
endif()
