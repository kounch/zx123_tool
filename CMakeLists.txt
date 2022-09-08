# Copyright (c) 2022 kounch
# SPDX-License-Identifier: BSD-2-Clause

cmake_minimum_required(VERSION 3.24)
project("ZX123 Tool")

if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR} )
    message(FATAL_ERROR "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there. You may need to remove CMakeCache.txt.")
endif()

list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/CMake/Find")

set(BASENAME ${PROJECT_NAME})
set(OUTPUT_DIR ${CMAKE_BINARY_DIR})

set(EXTRA_DOCS
    LICENSE
    README.md
    )

set(EXTRA_CONTENT
    ${PROJECT_SOURCE_DIR}/zx123_hash.json
    ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZX1.zip
    ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZX2.zip
    ${PROJECT_SOURCE_DIR}/FLASH16_empty.ZXD.zip
    ${PROJECT_SOURCE_DIR}/ROMS_255_Empty.ZX1.zip
    )

# Get Current version
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

# Check module availability
find_package(nuitka)

if (WIN32)
    set(APP_NAME "ZX123 Tool.exe")
elseif (APPLE)
    set(APP_NAME "ZX123 Tool.app")
    set(ARCH_TO_BUILD "arm64" )
    set(APP_CONTENT "${PROJECT_SOURCE_DIR}/MacOS")
    set(APP_RESOURCES "${APP_CONTENT}/Resources")

    # Check asciidoctor availability
    find_package(asciidoctor)
    find_package(asciidoctor-pdf)
    # Check create-dmg availability
    find_package(create-dmg)
endif()

# Function to build PDF files
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
        COMMENT "${PDF_LANG} Docs"
    )
endfunction()   

# Build localized PDFs
if(ASCIIDOCTOR-PDF_FOUND)
    message("Prepare docs build")
    set(PDF_DIR "${OUTPUT_DIR}/docs")
    file(MAKE_DIRECTORY ${PDF_DIR})

    make_pdf("es")
    make_pdf("en")

    add_custom_target(extra_docs ALL
        DEPENDS ${OUTPUT_DIR}/docs
    )
    foreach(file_i ${EXTRA_DOCS})
        add_custom_command(TARGET extra_docs
            COMMAND ${CMAKE_COMMAND} ARGS -E copy ${PROJECT_SOURCE_DIR}/${file_i} ${OUTPUT_DIR}/docs
            BYPRODUCTS ${OUTPUT_DIR}/docs/${file_i}
        )
    endforeach(file_i)
endif()

# Function to build Mac binaries
function(BUILD_MAC ARCH_TO_BUILD)
    set(MAC_BUILD_DIR "${OUTPUT_DIR}/mac_${ARCH_TO_BUILD}")
    file(MAKE_DIRECTORY ${MAC_BUILD_DIR})

    add_custom_target("zx123gui_mac_${ARCH_TO_BUILD}" ALL
        DEPENDS ${MAC_BUILD_DIR}/${APP_NAME}
        DEPENDS ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        )
    add_custom_command(OUTPUT ${MAC_BUILD_DIR}/${APP_NAME}
        DEPENDS ${PROJECT_SOURCE_DIR}/${BASENAME}.py
        COMMAND ${NUITKA_BINARY} ${PROJECT_SOURCE_DIR}/${BASENAME}.py --output-dir=${MAC_BUILD_DIR} --standalone --lto=yes --enable-plugin=tk-inter --macos-target-arch=${ARCH_TO_BUILD} --macos-disable-console --macos-create-app-bundle --macos-app-icon=${APP_RESOURCES}/${BASENAME}.icns --macos-signed-app-name="zx123_tool.kounch.github.io" --macos-app-version=${VERSION} --quiet
        BYPRODUCTS ${MAC_BUILD_DIR}/${BASENAME}.build ${MAC_BUILD_DIR}/${BASENAME}.dist
        COMMENT "MacOS ${ARCH_TO_BUILD} Binary"
        )
    add_custom_command(TARGET "zx123gui_mac_${ARCH_TO_BUILD}" POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${MAC_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${APP_RESOURCES} ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        COMMAND ${CMAKE_COMMAND} -E copy ${EXTRA_CONTENT} ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Resources
        COMMAND ${CMAKE_COMMAND} -E copy ${APP_CONTENT}/Info.plist ${MAC_BUILD_DIR}/${APP_NAME}/Contents
        COMMAND sed -i '' "s/VERSION_STRING/${VERSION}/" ${MAC_BUILD_DIR}/${APP_NAME}/Contents/Info.plist
        #Fix rpath (needed with Nuitka 1.0 and later)
        COMMAND install_name_tool -change '/Library/Frameworks/Python.framework/Versions/3.10/Python' '@executable_path/Python' ${MAC_BUILD_DIR}/${APP_NAME}/Contents/MacOS/${PROJECT_NAME}
        COMMENT "MacOS App"
        )

    if (CREATE-DMG_FOUND)
        set(DMG_FILE "${OUTPUT_DIR}/${BASENAME} MacOS ${ARCH_TO_BUILD} v${VERSION}.dmg")
        add_custom_command(TARGET "zx123gui_mac_${ARCH_TO_BUILD}" POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E remove ${DMG_FILE}
            COMMAND ${CREATE-DMG_BINARY} --volname ${PROJECT_NAME} --volicon "${APP_CONTENT}/DMG Icon.icns" --background "${APP_CONTENT}/DMG background.png" --window-pos 20 40 --window-size 420 550 --icon-size 64 --app-drop-link 0 0 --icon "ZX123 Tool.app" 100 0 --icon "LICENSE" 210 0 --icon "README.md" 100 125 --icon "ZX123 Tool Manual.pdf" 100 245 --icon "Manual de ZX123 Tool.pdf" 100 365 --no-internet-enable --hdiutil-quiet ${DMG_FILE} ${MAC_BUILD_DIR} >/dev/null
            BYPRODUCTS ${DMG_FILE}
            COMMENT "MacOS Disk Image"
        )
    endif()
endfunction()

# Build MacOS binaries and packages
if(NUITKA_FOUND)
    message("Prepare MacOS binary builds and packages")

    build_mac("arm64")
    build_mac("x86_64")
endif()

# Function to build Windows packages
function(BUILD_WIN ARCH_TO_PACKAGE)
    set(WIN_BUILD_DIR "${OUTPUT_DIR}/win_${ARCH_TO_PACKAGE}")
    set(WIN_ZIP_FILE "${OUTPUT_DIR}/${BASENAME} Windows ${ARCH_TO_PACKAGE} v${VERSION}.zip")

    add_custom_target("zx123gui_win_${ARCH_TO_PACKAGE}" ALL
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${WIN_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${EXTRA_CONTENT} ${WIN_BUILD_DIR}
        )

    add_custom_command(TARGET "zx123gui_win_${ARCH_TO_PACKAGE}" POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove ${WIN_ZIP_FILE}
        COMMAND ${CMAKE_COMMAND} -E tar "cf" "${WIN_ZIP_FILE}" --format=zip -- .
        WORKING_DIRECTORY ${WIN_BUILD_DIR}
        COMMENT "Compressing"
        )
endfunction()

# Build Windows ZIP files
message("Prepare Windows packages")
build_win("x86_32")
build_win("x86_64")

# Function to build Python ZIP package
function(BUILD_PYTHON)
    set(PYTHON_BUILD_DIR "${OUTPUT_DIR}/py")
    set(PYTHON_ZIP_FILE "${OUTPUT_DIR}/${BASENAME} Python v${VERSION}.zip")

    file(MAKE_DIRECTORY ${PYTHON_BUILD_DIR})
    file(GLOB PY_FILES "${PROJECT_SOURCE_DIR}/*py")

    add_custom_target("zx123gui_python" ALL
        COMMAND ${CMAKE_COMMAND} -E copy ${PY_FILES} ${PYTHON_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${PROJECT_SOURCE_DIR}/zx123_tool_gui ${PYTHON_BUILD_DIR}/zx123_tool_gui
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${OUTPUT_DIR}/docs ${PYTHON_BUILD_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${EXTRA_CONTENT} ${PYTHON_BUILD_DIR}
        )
    add_custom_command(
        TARGET "zx123gui_python" 
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove ${PYTHON_ZIP_FILE}
        COMMAND ${CMAKE_COMMAND} -E tar "cf" "${PYTHON_ZIP_FILE}" --format=zip -- .
        WORKING_DIRECTORY ${PYTHON_BUILD_DIR}
        COMMENT "Compressing"
        )
endfunction()

# Build generic ZIP Python file
message("Prepare Generic package")
build_python()
