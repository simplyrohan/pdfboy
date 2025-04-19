CC = emcc
BUILD = build/
ROM = rom.gb

LDFLAGS = -sWASM=0 -sEXPORTED_FUNCTIONS=[_main,_loop,_key_down,_key_up] -sEXTRA_EXPORTED_RUNTIME_METHODS=[ccall]

.PHONY: clean

build: $(BUILD)pdfboy.pdf

site: $(BUILD)norom.pdf site/*
	cp site/* $(BUILD)/

$(BUILD)norom.pdf: $(BUILD)emulator.js glue.js generate.py
	cat glue.js build/emulator.js > build/norom.js

	@echo "Generating PDF..."
	python generate.py build/norom.js build/norom.pdf

$(BUILD)pdfboy.pdf: $(BUILD)emulator.js $(ROM) glue.js generate.py
	cat glue.js build/emulator.js > build/build.js

	@echo "Embedding $(ROM)..."
	./embed_file.py $(ROM) build/build.js

	@echo "Generating PDF..."
	python generate.py build/build.js build/pdfboy.pdf

$(BUILD)emulator.js: main.c peanut_gb.h
	$(CC) main.c -o $(BUILD)emulator.js $(LDFLAGS)



# $(BUILD)pdfboy.pdf: glue.js generate.py build-gb
# 	cat glue.js build/emulator.js > build/build.js
# 	@echo "Embedding $(ROM)..."
# 	./embed_file.py $(ROM) build/build.js
# 	@echo "Generating PDF..."
# 	python generate.py build/build.js build/pdfboy.pdf

# $(BUILD)index.html: glue.js generate.py build-gb site/* 
# 	cat glue.js build/emulator.js > build/norom.js
# 	@echo "Generating PDF..."
# 	python generate.py build/norom.js build/norom.pdf
# 	cp site/* build/

# $(BUILD)emulator.js: main.c peanut_gb.h
# 	emcc main.c -o $(BUILD)emulator.js -sWASM=0 -sEXPORTED_FUNCTIONS=[_main,_loop,_key_down,_key_up] -sEXTRA_EXPORTED_RUNTIME_METHODS=[ccall]

clean:
	rm build/*
	@echo "Build Output Cleaned"