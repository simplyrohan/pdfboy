#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <emscripten.h>

#define ENABLE_SOUND 0
#define ENABLE_LCD 1

#include "peanut_gb.h"

struct priv_t
{
    /* Pointer to allocated memory holding GB file. */
    uint8_t *rom;
    /* Pointer to allocated memory holding save file. */
    uint8_t *cart_ram;

    /* Frame buffer */
    uint8_t fb[LCD_HEIGHT][LCD_WIDTH];
};

static struct gb_s gb;
static struct priv_t priv;

/**
 * Returns a byte from the ROM file at the given address.
 */
uint8_t gb_rom_read(struct gb_s *gb, const uint_fast32_t addr)
{
    const struct priv_t *const p = gb->direct.priv;
    return p->rom[addr];
}

/**
 * Returns a byte from the cartridge RAM at the given address.
 */
uint8_t gb_cart_ram_read(struct gb_s *gb, const uint_fast32_t addr)
{
    const struct priv_t *const p = gb->direct.priv;
    return p->cart_ram[addr];
}

/**
 * Writes a given byte to the cartridge RAM at the given address.
 */
void gb_cart_ram_write(struct gb_s *gb, const uint_fast32_t addr,
                       const uint8_t val)
{
    const struct priv_t *const p = gb->direct.priv;
    p->cart_ram[addr] = val;
}

/**
 * Ignore all errors.
 */
void gb_error(struct gb_s *gb, const enum gb_error_e gb_err, const uint16_t val)
{
    const char *gb_err_str[GB_INVALID_MAX] = {
        "UNKNOWN",
        "INVALID OPCODE",
        "INVALID READ",
        "INVALID WRITE",
        "HALT FOREVER"};
    struct priv_t *priv = gb->direct.priv;

    fprintf(stderr, "Error %d occurred: %s at %04X\n. Exiting.\n",
            gb_err, gb_err_str[gb_err], val);

    /* Free memory and then exit. */
    free(priv->cart_ram);
    free(priv->rom);
    exit(EXIT_FAILURE);
}

/**
 * Returns a pointer to the allocated space containing the ROM. Must be freed.
 */
uint8_t *read_rom_to_ram(const char *file_name)
{
    FILE *rom_file = fopen(file_name, "rb");
    size_t rom_size;
    uint8_t *rom = NULL;

    if (rom_file == NULL)
        return NULL;

    fseek(rom_file, 0, SEEK_END);
    rom_size = ftell(rom_file);
    rewind(rom_file);
    rom = malloc(rom_size);

    if (fread(rom, sizeof(uint8_t), rom_size, rom_file) != rom_size)
    {
        free(rom);
        fclose(rom_file);
        return NULL;
    }

    fclose(rom_file);
    return rom;
}

/**
 * Draws scanline into framebuffer.
 */
void lcd_draw_line(struct gb_s *gb, const uint8_t pixels[160],
                   const uint_fast8_t line)
{
    struct priv_t *priv = gb->direct.priv;

    for (unsigned int x = 0; x < LCD_WIDTH; x++)
        priv->fb[line][x] = pixels[x] & 3;
}

void key_down(char *key)
{
    if (strcmp(key, "up") == 0)
        gb.direct.joypad &= ~JOYPAD_UP;
    else if (strcmp(key, "down") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_DOWN;
    }
    else if (strcmp(key, "left") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_LEFT;
    }
    else if (strcmp(key, "right") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_RIGHT;
    }
    else if (strcmp(key, "a") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_A;
    }
    else if (strcmp(key, "b") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_B;
    }
    else if (strcmp(key, "start") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_START;
    }
    else if (strcmp(key, "select") == 0)
    {
        gb.direct.joypad &= ~JOYPAD_SELECT;
    }
}

void key_up(char *key)
{
    if (strcmp(key, "up") == 0)
        gb.direct.joypad |= JOYPAD_UP;
    else if (strcmp(key, "down") == 0)
    {
        gb.direct.joypad |= JOYPAD_DOWN;
    }
    else if (strcmp(key, "left") == 0)
    {
        gb.direct.joypad |= JOYPAD_LEFT;
    }
    else if (strcmp(key, "right") == 0)
    {
        gb.direct.joypad |= JOYPAD_RIGHT;
    }
    else if (strcmp(key, "a") == 0)
    {
        gb.direct.joypad |= JOYPAD_A;
    }
    else if (strcmp(key, "b") == 0)
    {
        gb.direct.joypad |= JOYPAD_B;
    }
    else if (strcmp(key, "start") == 0)
    {
        gb.direct.joypad |= JOYPAD_START;
    }
    else if (strcmp(key, "select") == 0)
    {
        gb.direct.joypad |= JOYPAD_SELECT;
    }
}

void loop()
{
    clock_t start = clock();

    /* Execute CPU cycles until the screen has to be redrawn. */
    gb_run_frame(&gb);

    clock_t frame = clock();
    EM_ASM({sendFrame($0, $1, $2, $3)}, priv.fb, LCD_WIDTH * LCD_HEIGHT * 1, LCD_WIDTH, LCD_HEIGHT);

    printf("ms: %li\n", (clock() - start) / 1000);
}

int main()
{
    printf("Starting PDFBoy\n");

    enum gb_init_error_e ret;

    /* Load the ROM from glue.js into VFS */
    EM_ASM({
        loadROMToFS();
    });

    /* Copy input ROM file to allocated memory. */
    if ((priv.rom = read_rom_to_ram("rom.gb")) == NULL)
    {
        printf("%d: %s\n", __LINE__, strerror(errno));
        exit(EXIT_FAILURE);
    }

    printf("Loaded ROM\n");

    /* Initialise context. */
    ret = gb_init(&gb, &gb_rom_read, &gb_cart_ram_read,
                  &gb_cart_ram_write, &gb_error, &priv);

    if (ret != GB_INIT_NO_ERROR)
    {
        printf("Error: %d\n", ret);
        exit(EXIT_FAILURE);
    }

    printf("Emulator initialized\n");

    priv.cart_ram = malloc(gb_get_save_size(&gb));

    gb_init_lcd(&gb, &lcd_draw_line);

    printf("Starting...\n");

    EM_ASM({
        app.setInterval('_loop()', 0);
    });

    free(priv.cart_ram);
    free(priv.rom);

    return EXIT_SUCCESS;
}
