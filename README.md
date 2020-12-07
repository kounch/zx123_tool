# zx123_tool

Copyright (c) 2020, kounch
All rights reserved.

## English

### Features

Analyzes and extracts data from SPI flash image files for ZX-Uno, ZXDOS and similar devices. These are the main features:

- List the contents of a ZX-Uno, etc. SPI flash image, showing, if possible, the version of BIOS, esxdos, main Spectrum core and optional cores
- Extract BIOS, esxdos ROM, Spectrum core and/or other cores to individual files
- Create a copy of the flash image and, optionally, change some BIOS default options, and/or truncate some (or all) of the optional cores
- If supplied a different kind of file (like a core or BIOS installation file) it will also try to identify its contents

Requires a `zx123_hash.json` file with block estructure (e.g.: ZXD) and, optionally, hashes to identify the blocks inside.

The maximum output Flash image size is 16 MiB (16384 KiB, or 16777216 Bytes), so a larger image (like 32 MiB) will be truncated if needed.

### Use

    Arguments:
      -h, --help          show help and exit
      -v, --version       show program's version number and exit
      -i INPUT_FILE, --input_file INPUT_FILE
                          ZX-Uno, ZXDOS, etc. File
      -d OUTPUT_DIR, --output_dir OUTPUT_DIR
                            Output directory for extracted files
      -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            Output flash file to copy
      -f, --force           Force overwrite of existing files
      -l, --list_contents List file contents
      -r, --roms          Process ZX Spectrum ROMs (extract instead of Cores)
      -s, --show_hashes   Show computed hashes
      -x EXTRACT, --extract EXTRACT
                Item(s) to extract (split using ","): BIOS, Spectrum, esxdos
                or core Number(s)
      -n N_CORES, --number_of_cores N_CORES
                    Number of cores to keep on output file
      -a INJECT_DATA, --add INJECT_DATA
                Data of item to inject with one of these formats:
                    BIOS,Path to BIOS binary
                    esxdos,Path to esxdos ROM binary
                    Spectrum,Path to Spectrum core binary
                    CORE,Core Number,Name to use,Path to core binary
                    ROM,Slot,Parameters,Name to use,Path to Spectrum ROM binary
      -m VIDEO_MODE, --video_mode VIDEO_MODE
                    Default BIOS video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
      -k KEYBOARD_LAYOUT, --keyboard_layout KEYBOARD_LAYOUT
                    Default BIOS Keyboard Layout:
                                    0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)

### Examples

Show contents of file:

    python3 zx123_tool.py -i FLASH.ZXD -l

Show contents of file, including ZX Spectrum ROMs data:

    python3 zx123_tool.py -i FLASH.ZXD -l -r

Extract `FIRMWARE.ZXD` file from `FLASH32.ZXD` file (on Windows):

    py -3 zx123_tool.py -i FLASH32.ZXD -x BIOS

Extract the third ZX Spectrum ROM to a file:

    ../zx123_tool.py -i FLASH32.ZXD -r -x 3

Show contents of file and extract `SPECTRUM.ZXD`, `ESXDOS.ZXD` and `.ZXD` files for cores 1 and 3:

    .../zx123_tool.py -l -i FLASH32.ZXD -x Spectrum,3,1,esxdos

Add core `NEXT.ZXD` as number `3`, with name `SpecNext`:

    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD

Add file `48.rom` (Spectrum ROM) in slot `5`, with name `Spec48`:

    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROM,5,xdnlh17,Spec48,48.rom

Add BIOS and esxdos ROMs:
    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a BIOS,FIRMWARE.ZXD -a esxdos,ESXMMC.BIN

Create a copy of `FLASH32.ZXD`, but removing all cores and setting BIOS default to VGA and Spectrum keyboard layout:

    .../zx123_tool.py -i FLASH32.ZXD -o FlashGDOSPlus.ZXD -n 0 -m 2 -k 3

Find out the version of a BIOS installation file:

    zx123_tool.py -i FIRMWARE.ZXD -l

### Description of JSON file

The JSON file is an object where the main name are file extensions (like `ZXD` or `ZX1`). For each of these, there is another object with the following structure:

    (...)
    "(Extension)": {
        "description" -> Short Description of the platform asssociated (e.g. "ZXDOS+")
        "hashtype"    -> "sha256sum" at this moment
        "parts": {    -> Description of SPI Flash Main Blocks
                         For each of these, an array is provided with this data:
                                [offset, size, <output name>, <magic bytes>]
                         The blocks are:
                            - "header"    -> SPI Flash Header and descriptors
                            - "esxdos"    -> esxdos binary ROM
                            - "roms_dir"  -> Description of installed Spectrum ROMs
                            - "cores_dir" -> Description of installed extra FPGA cores
                            - "BIOS"      -> Binary image of firmware
                            - "roms_data" -> Spectrum ROMs binary data
                            - "Spectrum"  -> Main FPGA core
                            - "core_base" -> Extra cores starting offset and size
        },
        "BIOS": {   -> Dictionary of hashes for different firmware versions in the format:
                       "(Version Description)": "(Hash)"
        },
        "esxdos": {  -> Dictionary of hashes for different esxdos ROM versions in the format:
                        "(Version Description)": "(Hash)"
        },
        "Spectrum": {   -> Dictionary of hashes for different Spectrum core versions in the format:
                           "(Version Description)": "(Hash)"
        "Cores": {   -> Dictionary for different FPGA cores       
            "(Core name)": {   -> Dictionary of hashes for different core versions in the format:
                                "(Version Description)": "(Hash)"
            },
            (...)
        }
    }.
    (...)

## Castellano

### Características

Analiza y extrae datos de ficheros de imagen de SPI flash de ZX-Uno, ZXDOS y otros dispostivos similares. Estas son sus funciones principales:

- Mostrar el contenido de la imagen, diciendo, si es posible, la versión de BIOS, esxdos, el core principal de Spectrum y otros cores que haya instalados
- Extraer la BIOS, la ROM de esxdos, el core de Spectrum y/o otros cores, a ficheros individuales
- Crear una copia de la imagen y, opcionalmente, cambiar algunas opciones por defecto de la BIOS, y/o truncar alguno (o todos) los cores opcionales
- Si se tratase de un tipo distinto de fichero (como un archivo de instalación de core o BIOS), también puede intentar identificar su versión

Necesita un fichero  `zx123_hash.json` con la estructrua de bloques de la imagen y, opcionalmente, datos para identificar dichos bloques.

El tamaño máximo de un fichero copiado de imagen son 16 MiB (16384 KiB, o 16777216 Bytes), así que las imágenes con un tamaño mayor (como 32 MiB) serán truncadas si fuera neceario.

### Uso

    Argumentos:
      -h, --help          Mostrar ayuda y salir
      -v, --version       Mostras versión del programa y salir
      -i FICHERO_ORIGEN, --input_file FICHERO_ORIGEN
                          Archivo ZX-Uno, ZXDOS, etc.
      -d DIRECTORIO_DESTINO, --output_dir DIRECTORIO_DESTINO
                            Directorio donde guardar los archivos extraídos
      -o FICHERO_DESTINO, --output_file FICHERO_DESTINO
                            Fichero donde guardar copia de la imagen flash
      -f, --force           Forzar sobreescribir archivos existentes
      -l, --list_contents Mostrar contenido del fichero de origen
      -r, --roms          Procesar ROMs de ZX Spectrum (extraer en vez de Core)
      -s, --show_hashes   Mostrar los datos de hash calculados
      -x EXTRAER, --extract EXTRAER
                Elemento(s) a extraer, separados por ",": BIOS, Spectrum,
                esxdos o número(s) de core
      -n N_CORES, --number_of_cores N_CORES
                    Número de cores a guardar en la copia
      -a DATOS, --add DATOS
                Datos de un elemento a añadir siguiendo uno de estos formatos:
                    BIOS,Ruta a fichero de BIOS
                    esxdos,Ruta a fichero ROM de esxdos
                    Spectrum,Ruta a core principal de Spectrum
                    CORE,Número,Nombre a usar,Ruta a fichero de core
                    ROM,Slot,Parámetros,Nombre a usar,Ruta a ROM de Spectrum
      -m VIDEO_MODE, --video_mode MODO_VIDEO
                    Modo de vídeo por defecto de la BIOS:
                                                0 (PAL), 1 (NTSC) o 2 (VGA)
      -k KEYBOARD_LAYOUT, --keyboard_layout DISTRIB_TECLADO
                    Distribución de teclado por defecto de la BIOS:
                                    0 (Auto), 1 (ES), 2 (EN) o 3 (Spectrum)

### Ejemplos

Mostrar contenido de una imagen:

    python3 zx123_tool.py -i FLASH.ZXD -l

Mostrar contenido de una imagen, incluyendo datos de ROMs de ZX Spectrum:

    python3 zx123_tool.py -i FLASH.ZXD -l -r

Extraer un fichero `FIRMWARE.ZXD` del archivo de imagen `FLASH32.ZXD` (en Windows):

    py -3 zx123_tool.py -i FLASH32.ZXD -x BIOS

Extraer la tercera ROM de ZX Spectrum a un fichero:

    ../zx123_tool.py -i FLASH32.ZXD -r -x 3

Mostrar contenido de archivo de imagen y extraer `SPECTRUM.ZXD`, `ESXDOS.ZXD` y ficheros `.ZXD` para los cores 1 y 3:

    .../zx123_tool.py -l -i FLASH32.ZXD -x Spectrum,3,1,esxdos

Añadir el core `NEXT.ZXD` con el número `3`, con nombre`SpecNext`:

    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD

Añadir ROM de Spectrum `48.rom` en el slot `5`, con el nombre `Spec48`:

    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROM,5,xdnlh17,Spec48,48.rom

Añadir ROMs de BIOS y esxdos:

    .../zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a BIOS,FIRMWARE.ZXD -a esxdos,ESXMMC.BIN

Crear una copia de `FLASH32.ZXD`, pero quitando todos los cores opcionales y configurando por defecto la BIOS para VGA y distribución de teclado tipo Spectrum:

    .../zx123_tool.py -i FLASH32.ZXD -o FlashGDOSPlus.ZXD -n 0 -m 2 -k 3

Averiguar la versión de un archivo de instalación de BIOS:

    zx123_tool.py -i FIRMWARE.ZXD -l

### Descripción del arhivo JSON

El archivo JSON es un objeto donde los nombres principales son extensiones de archivo (como `ZXD` o `ZX1`). Para cada una, se define otro objeto con la siguiente estructura:

    (...)
    "(Extensión)": {
        "description" -> Descripción corta de la plataforma asociada (ej: "ZXDOS+")
        "hashtype"    -> "sha256sum" por el momento
        "parts": {    -> Descripción de los bloques principales de una imagen SPI flash
                         Para cada uno de estos, se define una matriz con estos datos:
                                [desplazamiento, tamaño, <nombre de fichero>, <bytes de la cabecera>]
                         Los bloques son
                            - "header"    -> Cabecera y descriptores de imagen SPI Flash
                            - "esxdos"    -> ROM binaria de esxdos
                            - "roms_dir"  -> Descripción de las ROMs instaladas para Spectrum
                            - "cores_dir" -> Descripción de los cores FPGA instalados
                            - "BIOS"      -> Imagen binaria del firmware
                            - "roms_data" -> Datos binarios de las ROMs de Spectrum
                            - "Spectrum"  -> core principal de la FPGA
                            - "core_base" -> Desplazamiento y tamaño del primer core Extra
        },
        "BIOS": {   -> Diccionario con hashes para distintas versiones del firmware, con el formato:
                       "(Descripción de versión)": "(Hash)"
        },
        "esxdos": {  -> Diccionario con hashes para distintas versiones de ROMS de esxdos, con el formato:
                        "(Descripción de versión)": "(Hash)"
        },
        "Spectrum": {   -> Diccionario con hashes para distintas versiones del core principal de Spectrum, con el formato:
                           "(Descripción de versión)": "(Hash)"
        "Cores": {   -> Diccionario para distintos cores extra para la FPGA      
            "(Nombre de core)": {   -> Diccionario con hashes para distintas versiones del core, con el formato:
                                       "(Descripción de versión)": "(Hash)"
            },
            (...)
        }
    }.
    (...)

## License

BSD 2-Clause License

Copyright (c) 2020, kounch
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
