BUILD = build/

.PHONY: pdf,build, setup, clean

pdf:
	emcc main.c -o $(BUILD)index.html -sWASM=0 -sSINGLE_FILE=1 --preload-file rom.gb

build:
	emcc main.c -o $(BUILD)index.html

setup:
	@echo "Installing tools and setting up project"

	@git clone https://github.com/emscripten-core/emsdk.git --branch 1.39.20

	@./emsdk/emsdk install 1.39.20-fastcomp
	@./emsdk/emsdk activate 1.39.20-fastcomp

	@mkdir $(BUILD)

	@echo "Setup Finished"

clean:
	@rm build/*
	@echo "Build Output Cleaned"