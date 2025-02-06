BUILD = build/
build: main.c
	emcc main.c -o $(BUILD)index.html

setup:
	@echo "Installing tools and setting up project"

	@echo "[START] Installing Emscripten"
	@git clone https://github.com/emscripten-core/emsdk.git --branch 1.39.20

	@./emsdk/emsdk install 1.39.20-fastcomp
	@./emsdk/emsdk activate 1.39.20-fastcomp

	@echo "[DONE] Installed Emscripten"

	@mkdir $(BUILD)

	@echo "[DONE] Setup Finished"

clean:
	@rm build/*
	@echo "Build Output Cleaned"