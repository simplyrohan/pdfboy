# PDFBoy

A Gameboy emulator running in a PDF file (based on [DoomPDF](https://github.com/ading2210/doompdf) by ading2210)

Try it out at https://pdfboy.thatdev.xyz/ (Only works in Chrome-based browsers)

## Building

Clone this project with
```
git clone https://github.com/simplyrohan/pdfboy
```
and run
```
./setup.sh
make
```

> [!IMPORTANT]
> This project will not build on Mac (due to the old Emscripten version required).

## How it works + History
[ading2210 describes the PDF API in DoomPDF](https://github.com/ading2210/doompdf/tree/master?tab=readme-ov-file#javascript-in-a-pdf) but I want to go more into how exactly these "_______ in a PDF file" projects work.

Adobe introduced Javascript capabilities to the [PDF specification](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) in 2006, opening the door to interactive and dynamic PDFs. The [Javascript API](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/JS_API_AcroJS.html) allowed for some crazy things like network requests, 3D graphics, and more. You can still take advantage of these crazy features using Adobe's PDF viewer, Acrobat.

However, most browsers didn't implement this, primarily due to security risks. Chromium (Chrome) did implement Javascript for PDFs but still had many limitations (no network requests, 3D graphics, or other fancy features). Still, you can modify the page's contents and run a limited version of Javascript.

Well, what can we do with this? [Omar Rizwan (osnr) showed off a version of "Atari Breakout"](https://github.com/osnr/horrifying-pdf-experiments) back in 2016 using just the Javascript APIs provided by Chrome.

Later, [Thomas Rinsma created PDFTris](https://github.com/ThomasRinsma/pdftris), a Tetris clone in a PDF file similar to the Breakout PDF. It attracted some attention and was a fun showcase of the JS capabilities with buttons and other elements.
(It's also worth noting that Thomas Rinsma was able to [get Doom working](https://github.com/ThomasRinsma/pdfdoom) although it was a slightly worse experience compared to ading2210's version).

But this idea finally went big when [ading2210 made DoomPDF](https://github.com/ading2210/doompdf/), a port of the original 1993 DOOM. 
[He also made LinuxPDF](https://github.com/ading2210/linuxpdf) which used the same ideas but with a RISC-V emulator rather than DOOM.

### DoomPDF (and how other "in a PDF" projects are made)
DOOM ports to the web are nothing new. The issue ading2210 faced when porting DOOM to a PDF was that all these ports used WebAssembly. WebAssembly is a newer technology that allows websites to use projects in other languages, like C/C++, by compiling them with tools like [Emscripten](https://emscripten.org/).

Chrome's PDF engine doesn't allow WebAssembly, blocking that path. However, Emscripten used to be able to compile to [asm.js](https://en.wikipedia.org/wiki/Asm.js). It's purely Javascript and can run in PDFs.

By installing an old Emscripten version (specifically 1.39.20), ading2210 could compile DOOM to asm.js. [doomgeneric](https://github.com/ozkl/doomgeneric) was used which is a version of DOOM that's even easier to port. Then, using a [lower-level PDF generation library](https://github.com/pmaupin/pdfrw), he embedded DOOM into a standalone PDF file.

Finally, he used a Javascript "glue" to connect the I/O functions to the PDF APIs. This included button/keyboard input and graphical output. (You can find more about his graphical output techniques in the DoomPDF repository)

## Project Structure
`main.c` - Main code to setup and run the GameBoy emulator

`peanut_gb.h` - [The core emulator](https://github.com/deltabeard/Peanut-GB/tree/master)

`glue.js` - Binds core functions like logging and other I/O between Emscripten and the PDF API

`generate.py` - PDF File generator (based off DoomPDF's version)

`embed_file.py` - Basic CLI for embedding binary files into other files using Base64 (needed for storing ROMs)

`site/` - Files for [landing website](https://pdfboy.thatdev.xyz)

## Credits
This project is made by [@simplyrohan](https://github.com/simplyrohan).

Based off [DoomPDF](https://github.com/ading2210/doompdf) by [@ading2210](https://github.com/ading2210).

Uses [Peanut-GB](https://github.com/deltabeard/Peanut-GB/tree/master) by [@deltabeard](https://github.com/deltabeard) for the emulator.

## License
This repository is licensed under the GNU General Public License V3

```
simplyrohan/pdfboy - A Gameboy emulator running in a PDF file (inspired by DoomPDF)
Copyright (C) 2025 simplyrohan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

