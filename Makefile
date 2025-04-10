BUILD = build/
ROM = rom.gb
.PHONY: pdf,build, setup, clean

pdf:
	emcc main.c -o $(BUILD)emulator.js -sWASM=0 -sEXPORTED_FUNCTIONS=[_main,_loop]
	cat glue.js build/emulator.js > build/build.js
	@echo "Embedding ROM..."
	./embed_file.py $(ROM) build/build.js
	@echo "Generating PDF..."
	python generate.py build/build.js build/pdfboy.pdf

build:
	emcc main.c -o $(BUILD)index.html -sWASM=0 -sSINGLE_FILE=1 --preload-file rom.gb

setup:
	@echo "Installing tools and setting up project"

	git clone https://github.com/emscripten-core/emsdk.git --branch 1.39.20

	./emsdk/emsdk install 1.39.20-fastcomp
	./emsdk/emsdk activate 1.39.20-fastcomp

	mkdir $(BUILD)

	@echo "Setup Finished"

clean:
	rm build/*
	@echo "Build Output Cleaned"