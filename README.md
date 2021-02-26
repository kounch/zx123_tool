# zx123_tool

Copyright (c) 2020-2021, kounch

All rights reserved.

---

Select your desired language / Elija idioma:

- Click [this link for English](#english)

- Pulse [este enlace para Castellano](#castellano)

---

## English

### Features

This is a tool that analyzes, extracts and injects data in SPI flash image files for ZX-Uno, ZXDOS and similar devices.

These are the main features:

- List the contents of a ZX-Uno, etc. SPI flash image, showing, if possible, the version of BIOS, esxdos, main Spectrum core and optional cores, Spectrum ROMs and several BIOS settings
- Extract BIOS, esxdos ROM, Spectrum core and/or other cores, Spectrum ROMs to individual files
- Create a copy of the flash image and, optionally, and/or truncate some (or all) of the optional cores
- Change some BIOS default options (video mode, keyboard layout, default core, default ROM, etc.)
- Add or replace FPGA cores and/or Spectrum ROM images (from individual ROM files or RomPack files)
- Wipe with  0s all Cores an ZX Spectrum ROMs data
- If supplied a different kind of file (like a core or BIOS installation file) it will also try to identify its contents
- List, add or extract ROMs from a ROMPack v2 ROms file

Requires a [`zx123_hash.json`](##description-of-json-file) file with block structure for the kind of SPI flash file (e.g.: ZXD) and, optionally, hashes to identify the blocks inside. If not found, it tries to download it from the GitHub repository.

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
      -r, --roms          Process ZX Spectrum ROMs (list or, in extract mode,
                          extract instead of Cores)
      -q, --check_updated For each Core or non Spectrum ROM, check version
                          against 'latest' entry in the JSON database
      -s, --show_hashes   Show computed hashes
      -x EXTRACT, --extract EXTRACT
                Item(s) to extract, split using ",": BIOS, Spectrum, ROMS, 
                esxdos and/or core/ROM Number(s)
      -n N_CORES, --number_of_cores N_CORES
                Number of cores to keep on output file
      -a INJECT_DATA, --add INJECT_DATA
                Data of item to inject with one of these formats:
                    BIOS,Path to BIOS binary
                    esxdos,Path to esxdos ROM binary
                    Spectrum,Path to Spectrum core binary
                    CORE,Core Number,Name to use,Path to core binary
                    ROM,Slot,Parameters,Name to use,Path to Spectrum ROM binary
                    ROMS,Path to RomPack file with some ROMs inside
      -w, --wipe            Wipe all ROMs and all secondary cores from image
      -e, --32              Expand, if needed, flash file to 32MiB
      -c DEFAULT_CORE, --default_core DEFAULT_CORE
                Default core number: 1 and up
      -z DEFAULT_ROM, --default_rom DEFAULT_ROM
                Index of default Spectrum ROM: 0 and up
      -m VIDEO_MODE, --video_mode VIDEO_MODE
                    Default BIOS video mode: 0 (PAL), 1 (NTSC) or 2 (VGA)
      -k KEYBOARD_LAYOUT, --keyboard_layout KEYBOARD_LAYOUT
                    Default BIOS Keyboard Layout:
                                    0 (Auto), 1 (ES), 2 (EN) or 3 (Spectrum)
      -b BOOT_TIMER, --boot_timer BOOT_TIMER
                                    Boot Timer: 0 (No Timer), 1, 2, 3 or 4
      -u, --update   If the only argument, download JSON from repository
                     If there's an SPI flash image file, updte BIOS and Cores to
                    the latest version according to JSON file contents

#### ROM Parameters

When adding individual ROM data to a file, you can specify any of the following flags when using the ROM:

-`i`: Keyboard issue 3 enabled (instead of issue 2)

-`c`: Disable memory contention

-`d`: Enable DivMMC

-`n`: Enable NMI DivMMC (esxdos Menu)

-`p`: Use Pentagon Timings

-`t`: Use 128K timings

-`s`: Disable DivMMC and ZXMMC ports

-`m`: Enable Timex Horizontal MMU

-`h`: Disable ROM high bit (1FFD bit 2)

-`l`: Disable ROM low bit (7FFD bit 4)

-`1`: Disable 1FFD port (+2A/3 paging)

-`7`: Disable 7FFD port (128K paging)

-`2`: Disable TurboSound (secondary AY chip)

-`a`: Disable AY chip

-`r`: Disable Radastanian mode

-`x`: Disable Timex mode

-`u`: Disable ULAPlus

### Examples

Show contents of file:

    python3 zx123_tool.py -i FLASH.ZXD -l

Show contents of file, including ZX Spectrum ROMs data:

    python3 zx123_tool.py -i FLASH.ZXD -l -r

Extract `FIRMWARE.ZXD` file from `FLASH32.ZXD` file (on Windows):

    py -3 zx123_tool.py -i FLASH32.ZXD -x BIOS

Extract the third ZX Spectrum ROM to a file:

    ...zx123_tool.py -i FLASH32.ZXD -r -x 3

Extract all Spectrum ROMs to `ROMS.ZX1` RomPack file from `FLASH32.ZXD` file:

    ...zx123_tool.py -i FLASH32.ZXD -x ROMS

Show contents of file and extract `SPECTRUM.ZXD`, `ESXDOS.ZXD` and `.ZXD` files for cores 1 and 3:

    ...zx123_tool.py -l -i FLASH32.ZXD -x Spectrum,3,1,esxdos

Add core `NEXT.ZXD` as number `3`, with name `SpecNext`:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD

Add core `NEXT.ZXD` as number `3`, with name `SpecNext`, and set as the default boot core:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD -c 3

Add file `48.rom` (Spectrum ROM) in slot `5`, with name `Spec48`:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROM,5,xdnlh17,Spec48,48.rom

Set ROM with index 2 (do not mistake with slot index) as the default Spectrum ROM:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -z 2

Add BIOS and esxdos ROMs:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a BIOS,FIRMWARE.ZXD -a esxdos,ESXMMC.BIN

Replace all Spectrum ROMs with the contents of `MyROMS.ZX1` RomPack file:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROMS,MyROMS.ZX1

Wipe all ROMs data and all secondary cores data:

    ...zx123_tool.py -i FLASH.ZXD -w -o FLASHempty.ZXD

Wipe all ROMs data and all secondary cores data, and then add file `48.rom` (Spectrum ROM) in slot `0`, with name `ZX Spectrum`:

    ...zx123_tool.py -i FLASH.ZXD -w -o FLASHnew.ZXD -a "ROM,0,xdnlh17,ZX Spectrum,48.rom"

Create a copy of `FLASH32.ZXD`, but removing all cores and setting BIOS default to VGA and Spectrum keyboard layout:

    ...zx123_tool.py -i FLASH32.ZXD -o FlashGDOSPlus.ZXD -n 0 -m 2 -k 3

Find out the version of a BIOS installation file:

    ...zx123_tool.py -i FIRMWARE.ZXD -l

Convert the contents of a classic ROMPack file to a ROMPack v2 file:

    ...zx123_tool.py -i ROMS_255_orig.ZX1 -o ROMS_255.ZX1 -a ROMS,MyROMS.ZX1

Add a ROM to a ROMPack v2 file:

    ...zx123_tool.py -i ROMS_255_orig.ZX1 -o ROMS_255.ZX1 -a "ROM,0,xdnlh17,ZX Spectrum,48.rom"

    ...zx123_tool.py -i ROMS_255_orig.ZX1 -o ROMS_255.ZX1 -a ROMS,MyROMS.ZX1

Extract ROMs with indexes 3, 5 and 6 from a ROMPack v2 file:

    ...zx123_tool.py -i ROMS_255.ZX1 -x 3,5,6

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
                            - "header"    -> File header and descriptors
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
                                "(Version Description)": "(Hash)",
                                "latest" -> Name of the latest version and (optionally) download URL
                                "base"   -> Name of another version with download URL if there's no URL for the latest
            },
            (...)
        }
    }.
    (...)

`roms_dir` format:

    [roms directory offset, directory block size, "", "", enabled entries offset, first ROMs block length, second ROMs block length]

`cores_dir` format:

     [cores directory offset, directory block size, "", "", first cores block length, second cores block length]

`roms_data` format:

    [first slot offset, first ROMs block size, "", "", second ROMs block offset],

`core_base` format:

    [first core offset, core length, "", First bytes of a binary core data, second cores block offset]

### Description of ROMPack v2 file

ROMPack v2 files are based on classic ROMPack files, used to extract and insert all the ROM files in a ZX-Uno, ZXDOS SPI flash. Classic ROMpack files have 64 ROM slots while ROMPack v2 files have 255 ROM slots. The file structure of a ROMPAck file is as follows:

 Start     | End        | Description
 -----     | ---        | -----------
`0x000000` | `0x000003` | Signature 'RPv2'
`0x000004` | `0x00003F` | Reserved. Unused (pad with `0x00`)
`0x000040` | `0x003FFF` | Up to 255 64 bytes blocks (ROM Entries) (pad with `0x00`)
`0x004000` | `0x0040FE` | Up to 255 1 byte blocks with ROM Index Entries (pad with `0xFF`)
`0x0040FF` | `0x0040FF` | Default ROM Index (1 byte)
`0x004100` | `0x4000FF` | Up to 255 16384 bytes ROM slots (pad with `0x00`)

#### ROM entry detail

 Start              | End      | Description
 -----              | ---      | -----------
`0x00`              | `0x00`   | Slot offset
`0x01`              | `0x01`   | Slot size
`0x02`              | `0x02`   | Flags 1:
`0x02`:Bit `0`      |  Bit `1` | Machine timings: `00`=48K `01`=128K, `10`=Pentagon
`0x02`:Bit `2`      | Bit `2`  | NMI DivMMC: `0`=disabled, `1`=enabled
`0x02`:Bit `3`      | Bit `3`  | DivMMC: `0`=disabled, `1`=enabled
`0x02`:Bit `4`      | Bit `4`  | Contention: `0`=disabled, `1`=enabled
`0x02`:Bit `5`      | Bit `5`  | Keyboard issue: `0`=issue 2, `1`=issue 3
`0x03`              | `0x03`   | Flags 2:
`0x03`:Bit `0`      | Bit `0`  | AY chip: `0`=enabled, `1`=disabled
`0x03`:Bit `1`      | Bit `1`  | 2nd AY chip (TurboSound): `0`=enabled, `1`=disabled
`0x03`:Bit `2`      | Bit `2`  | `7ffd` port: `0`=enabled, `1`=disabled
`0x03`:Bit `3`      | Bit `3`  | `1ffd` port: `0`=enabled, `1`=disabled
`0x03`:Bit `4`      | Bit `4`  | ROM low bit: `0`=enabled, `1`=disabled
`0x03`:Bit `5`      | Bit `5`  | ROM high bit: `0`=enabled, `1`=disabled
`0x03`:Bit `6`      | Bit `6`  | horizontal MMU in Timex: `0`=disabled, `1`=enabled
`0x03`:Bit `7`      | Bit `7`  | DivMMC and ZXMMC ports: `0`=enabled, `1`=disabled
`0x08`              | `0x0F`   | crc16-ccitt values. Up to 4 16-bit values in reverse order
`0x10`              | `0x1F`   | unused
`0x20`              | `0x3F`   |Name of ROM in ASCII, space padded

## Castellano

### Características

Esta es una herramienta que analiza, extrae o añade datos en ficheros de imagen de SPI flash de ZX-Uno, ZXDOS y otros dispostivos similares.

Estas son sus funciones principales:

- Mostrar el contenido de la imagen, diciendo, si es posible, la versión de BIOS, esxdos, el core principal de Spectrum, otros cores que haya instalados, ROMs de Spectrum y algunos ajustes de la BIOS
- Extraer la BIOS, la ROM de esxdos, el core de Spectrum y/o otros cores, ROMs de Spectrum a ficheros individuales
- Crear una copia de la imagen y, opcionalmente, truncar alguno (o todos) los cores opcionales
- Cambiar algunas opciones por defecto de la BIOS (modo de vídeo, distribución de teclado, core por defecto, ROM de Spectrum por defecto, etc.)
- Añadir o reemplazar cores de la FPGA y/o imágenes de ROM de Spectrum (desde ficheros de ROM individuales o un fichero RomPack)
- Borrar con 0s todos los datos de los Cores y las ROMs de ZX Spectrum
- Si se tratase de un tipo distinto de fichero (como un archivo de instalación de core o BIOS), también puede intentar identificar su versión
- Mostrar, añadir o extraer ROMs de un fichero ROMPack v2

Necesita un fichero  [`zx123_hash.json`](#descripción-del-arhivo-json) con la estructura de bloques del archivo de imagen y, opcionalmente, datos para identificar dichos bloques. Si no se encuentra, intentará descargarlo desde el repositorio en GitHub.

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
      -r, --roms          Procesar ROMs de ZX Spectrum (listar o, en modo de 
                          extracción, extraer en vez de Core)
      -q, --check_updated Para cada Core o ROM que no sea de Spectrum, comparar
                          la versión con la entrada 'latest' del JSON
      -s, --show_hashes   Mostrar los datos de hash calculados
      -x EXTRAER, --extract EXTRAER
                Elemento(s) a extraer, separados por ",": BIOS, Spectrum, ROMS,
                esxdos y/o número(s) de core/ROM
      -n N_CORES, --number_of_cores N_CORES
                Número de cores a guardar en la copia
      -a DATOS, --add DATOS
                Datos de un elemento a añadir siguiendo uno de estos formatos:
                    BIOS,Ruta a fichero de BIOS
                    esxdos,Ruta a fichero ROM de esxdos
                    Spectrum,Ruta a core principal de Spectrum
                    CORE,Número,Nombre a usar,Ruta a fichero de core
                    ROM,Slot,Parámetros,Nombre a usar,Ruta a ROM de Spectrum
                    ROMS,Ruta a un archivo RomPack con varias ROMs
      -w, --wipe           Borrar todas las ROMs y todos los cores secundarios
      -e, --32             Expandir, si hiciera falta la imagen a 32MiB
      -c CORE_D, --default_core CORE_D
                Número de core por defecto: 1 o superior
      -z ROM_D, --default_rom ROM_D
                Índice de ROM de Spectrum por defecto: 0 o superior
      -m VIDEO_MODE, --video_mode MODO_VIDEO
                    Modo de vídeo por defecto de la BIOS:
                                                0 (PAL), 1 (NTSC) ó 2 (VGA)
      -k KEYBOARD_LAYOUT, --keyboard_layout DISTRIB_TECLADO
                    Distribución de teclado por defecto de la BIOS:
                                    0 (Auto), 1 (ES), 2 (EN) ó 3 (Spectrum)
      -b BOOT_TIMER, --boot_timer RETRASO
                       Retraso en el arranque: 0 (Sin retraso), 1, 2, 3 ó 4
      -u, --update   Si no hay más argumentos, descargar JSON del repositorio
                     Si hay imagen SPI flash, actualizar BIOS y Cores a la 
                    última versión posible según se indica en el fichero JSON

#### Parámetros de ROM

Al añadir datos de una ROM individual a un fichero, se pueden especificar los siguientes indicadores para usar al utilizar la ROM:

- `i`: Habilitar teclado issue 3 (en vez de issue 2)

- `c`: Deshabilitar la contención de memoria

- `d`: Habilitar DivMMC

- `n`: Habilitar NMI DivMMC (menú de esxdos)

- `p`: Usar timings de Pentagon

- `t`: Usar timings de 128K

- `s`: Deshabilitar puertos de DivMMC y ZXMMC

- `m`: Habilitar MMU horizontal de Timex

- `h`: Deshabilitar bit alto de ROM (bitd 2 de 1FFD)

- `l`: Deshabilitar bit bajo de ROM (bit 4 de 7FFD)

- `1`: Deshabilitar puerto 1FFD (paginado de +2A/3)

- `7`: Deshabilitar puerto 7FFD (paginado de 128K)

- `2`: Deshabilitar TurboSound (chip AY secundario)

- `a`: Deshabilitar chip AY

- `r`: Deshabilitar modo Radastaniano

- `x`: Deshabilitar modo Timex

- `u`: Deshabilitar ULAPlus

### Ejemplos

Mostrar contenido de una imagen:

    python3 zx123_tool.py -i FLASH.ZXD -l

Mostrar contenido de una imagen, incluyendo datos de ROMs de ZX Spectrum:

    python3 zx123_tool.py -i FLASH.ZXD -l -r

Extraer un fichero `FIRMWARE.ZXD` del archivo de imagen `FLASH32.ZXD` (en Windows):

    py -3 zx123_tool.py -i FLASH32.ZXD -x BIOS

Extraer la tercera ROM de ZX Spectrum a un fichero:

    ...zx123_tool.py -i FLASH32.ZXD -r -x 3

Extraer todas las ROMs de Spectrum a un archivo RomPack `ROMS.ZX1` desde el archivo de imagen `FLASH32.ZXD`:

    ...zx123_tool.py -i FLASH32.ZXD -x ROMS

Mostrar contenido de archivo de imagen y extraer `SPECTRUM.ZXD`, `ESXDOS.ZXD` y ficheros `.ZXD` para los cores 1 y 3:

    ...zx123_tool.py -l -i FLASH32.ZXD -x Spectrum,3,1,esxdos

Añadir el core `NEXT.ZXD` con el número `3`, con nombre`SpecNext`:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD

Añadir el core `NEXT.ZXD` con el número `3`, con nombre`SpecNext`,y configurar como core de inicio por defecto:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a CORE,3,SpecNext,NEXT.ZXD -c 3

Añadir ROM de Spectrum `48.rom` en el slot `5`, con el nombre `Spec48`:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROM,5,xdnlh17,Spec48,48.rom

Configurar la ROM con índice 2 (no confundir con número de slot) como la ROM de Spectrum por defecto:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -z 2

Añadir ROMs de BIOS y esxdos:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a BIOS,FIRMWARE.ZXD -a esxdos,ESXMMC.BIN

Reemplazar todas las ROMs con el contenido del fichero RomPack `MisROMS.ZX1`:

    ...zx123_tool.py -i FLASH.ZXD -o FLASHnew.ZXD -a ROMS,MisROMS.ZX1

Borrar todos los datos de ROMs y todos los datos de los cores secundarios:

    ...zx123_tool.py -i FLASH.ZXD -w -o FLASHempty.ZXD

Borrar todos los datos de ROMs y todos los datos de los cores secundarios, y luego añadir el fichero ROM de Spectrum `48.rom` en el slot `0`, con el nombre `ZX Spectrum`:

    ...zx123_tool.py -i FLASH.ZXD -w -o FLASHnew.ZXD -a "ROM,0,xdnlh17,ZX Spectrum,48.rom"

Crear una copia de `FLASH32.ZXD`, pero quitando todos los cores opcionales y configurando por defecto la BIOS para VGA y distribución de teclado tipo Spectrum:

    ...zx123_tool.py -i FLASH32.ZXD -o FlashGDOSPlus.ZXD -n 0 -m 2 -k 3

Averiguar la versión de un archivo de instalación de BIOS:

    ...zx123_tool.py -i FIRMWARE.ZXD -l

Convertir el contenido de un fichero ROMPack clásico a un fichero ROMPack v2:

    ...zx123_tool.py -i ROMS_255_orig.ZX1 -o ROMS_255.ZX1 -a ROMS,MyROMS.ZX1

Añadir una ROM a un fichero ROMPack v2:

    ...zx123_tool.py -i ROMS_255_orig.ZX1 -o ROMS_255.ZX1 -a "ROM,0,xdnlh17,ZX Spectrum,48.rom"

Extraer las ROMs con índices 3, 5 y 6 de un fichero ROMPack v2:

    ...zx123_tool.py -i ROMS_255.ZX1 -x 3,5,6

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
                                       "latest" -> Nombre de la última versión y (opcionalmente) URL de descarga
                                       "base"   -> Nombre de otra versión descargable si la última no la tiene
            },
            (...)
        }
    }.
    (...)

Para `roms_dir`, el formato es el siguiente:

    [offset de inicio del directorio, tamaño del bloque de directorio, "", "", offset de entradas activas, longitud del primer bloque de ROMs, longitud del segundo bloque de ROMs]

Para `cores_dir`, el formato es el siguiente:

     [offset de inicio del directorio, tamaño del bloque de directorio, "", "", longitud del primer bloque de cores, longitud del segundo bloque de cores]

Para `roms_data`, el formato es el siguiente:

    [offset del primer slot, tamaño del primer bloque de ROMs, "", "", offset del segundo bloque de ROMs],

Para `core_base`, el formato es el siguiente:

    [offset del primer core, longitud de un core, "", Primeros bytes de un fichero binario de core, offset del segundo bloque de cores]

### Descripción de un fichero ROMPack v2

ROMPack v2 files are based on classic ROMPack files, used to extract and insert all the ROM files in a ZX-Uno, ZXDOS SPI flash. Classic ROMpack files have 64 ROM slots while ROMPack v2 files have 255 ROM slots. The file structure of a ROMPAck file is as follows:

 Inicio    | Fin        | Descripción
 ------    | ----       | -----------
`0x000000` | `0x000003` | Firma 'RPv2'
`0x000004` | `0x00003F` | Reservado. Sin usar (rellenar con `0x00` hasta el final)
`0x000040` | `0x003FFF` | Hasta 255 bloques de 64 bytes (ROM Entry) (rellenar con 0x00 hasta el final)
`0x004000` | `0x0040FE` | Hasta 255 bloques de 1 byte con índice de ROM Entry (rellenar con `0xFF` hasta el final)
`0x0040FF` | `0x0040FF` | Índice de ROM por defecto (1 byte)
`0x004100` | `0x4000FF` | Hasta 255 slots de 16384 bytes (rellenar con `0x00` hasta el final)

#### Detalle de ROM Entry

 Start              | End     | Description
 -----              | ---     | -----------
`0x00`              | `0x00`  | Offset de primer Slot utilizado
`0x01`              | `0x01`  | Tamaño en slots
`0x02`              | `0x02`  | Flags 1:
`0x02`:Bit `0`      | Bit `1` | Machine timings: `00`=48K `01`=128K, `10`=Pentagon
`0x02`:Bit `2`      | Bit `2` | NMI DivMMC: `0`=deshabilitado, `1`=habilitado
`0x02`:Bit `3`      | Bit `3` | DivMMC: `0`=deshabilitado, `1`=habilitado
`0x02`:Bit `4`      | Bit `4` | Contención: `0`=deshabilitada, `1`=habilitada
`0x02`:Bit `5`      | Bit `5` | Keyboard issue: `0`=issue 2, `1`=issue 3
`0x03`              | `0x03`  | Flags 2
`0x03`:Bit `0`      | Bit `0` | Chip AY: `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `1`      | Bit `1` | Segundo Chip AY (TurboSound): `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `2`      | Bit `2` | Puerto 7ffd: `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `3`      | Bit `3` | Puerto 1ffd: `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `4`      | Bit `4` | ROM low bit: `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `5`      | Bit `5` | ROM high bit: `0`=habilitado, `1`=deshabilitado
`0x03`:Bit `6`      | Bit `6` | MMU horizontal en Timex: `0`=deshabilitado, `1`=habilitado
`0x03`:Bit `7`      | Bit `7` | Puertos DivMMC y ZXMMC: `0`=habilitado, `1`=deshabilitado
`0x08`              | `0x0F`  | Valores de crc16-ccitt. Hata 4 valores de 16-bit en orden inverso
`0x10`              | `0x1F`  | Sin usar
`0x20`              | `0x3F`  | Nombre de la ROM en ASCII (rellenar con espacios hasta el final)

## License

BSD 2-Clause License

Copyright (c) 2020-2021, kounch
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
