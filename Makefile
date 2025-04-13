BUILD = build/
ROM = rom.gb
.PHONY: pdf, build-gb, setup, clean

pdf: build-gb
	cat glue.js build/emulator.js > build/build.js
	@echo "Embedding $(ROM)..."
	./embed_file.py $(ROM) build/build.js
	@echo "Generating PDF..."
	python generate.py build/build.js build/pdfboy.pdf

site: build-gb
	cat glue.js build/emulator.js > build/norom.js
	@echo "Generating PDF..."
	python generate.py build/norom.js build/norom.pdf
	cp site/* build/

build-gb:
	emcc main.c -o $(BUILD)emulator.js -sWASM=0 -sEXPORTED_FUNCTIONS=[_main,_loop,_key_down,_key_up] -sEXTRA_EXPORTED_RUNTIME_METHODS=[ccall]

setup:
	@echo "Installing tools and setting up project"

	git clone https://github.com/emscripten-core/emsdk.git --branch 1.39.20

	./emsdk/emsdk install 1.39.20-fastcomp
	./emsdk/emsdk activate 1.39.20-fastcomp

	pip install pdfrw

	mkdir $(BUILD)

	@echo "Setup Finished"

clean:
	rm build/*
	@echo "Build Output Cleaned"