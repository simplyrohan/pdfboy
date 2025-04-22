# PDF Generator from DoomPDF
# Will probably be replaced soon
import sys

from pdfrw import PdfWriter
from pdfrw.objects.pdfname import PdfName
from pdfrw.objects.pdfstring import PdfString
from pdfrw.objects.pdfdict import PdfDict
from pdfrw.objects.pdfarray import PdfArray


def create_script(js):
    action = PdfDict()
    action.S = PdfName.JavaScript
    action.JS = js
    return action


def create_page(width, height):
    page = PdfDict()
    page.Type = PdfName.Page
    page.MediaBox = PdfArray([0, 0, width, height])

    page.Resources = PdfDict()
    page.Resources.Font = PdfDict()
    page.Resources.Font.F1 = PdfDict()
    page.Resources.Font.F1.Type = PdfName.Font
    page.Resources.Font.F1.Subtype = PdfName.Type1
    page.Resources.Font.F1.BaseFont = PdfName.Courier

    r, g, b = 190 / 255, 185 / 255, 180 / 255  # background color
    background_stream = f"""
    {r} {g} {b} rg
    0 0 {width} {height} re
    f 
    """

    page.Contents = PdfDict(stream=background_stream)

    return page


def create_field(
    name,
    x,
    y,
    width,
    height,
    value="",
    font_size=None,
    bg=(1, 1, 1),
    fg=(0, 0, 0),
    f_type=PdfName.Tx,
):
    annotation = PdfDict()
    annotation.Type = PdfName.Annot
    annotation.Subtype = PdfName.Widget
    annotation.R = 45
    annotation.FT = f_type
    annotation.Ff = 1
    annotation.Rect = PdfArray([x, y, x + width, y + height])
    annotation.T = PdfString.encode(name)
    annotation.V = PdfString.encode(value)

    annotation.BS = PdfDict()
    annotation.BS.W = 0

    annotation.MK = PdfDict(BG=bg)

    annotation.DA = f"{fg[0]} {fg[1]} {fg[2]} rg"
    if font_size:
        annotation.DA = f"/Courier {font_size} Tf {fg[0]} {fg[1]} {fg[2]} rg"

    return annotation


def create_text(x, y, size, txt, color=[0, 0, 0], bold=False):
    return f"""
  BT
  /Helvetica {size} Tf {color[0]} {color[1]} {color[2]} rg
  {x} {y} Td ({txt}) Tj
  ET
  """


def create_button(name, x, y, width, height, value, font_size, bg, fg, tl, tr, bl, br):
    shave = 1 * ((tl + tr + bl + br) / 4)
    button = create_field(
        name,
        x + (shave / 2),
        y + (shave / 2),
        width - shave,
        height - shave,
        f_type=PdfName.Btn,
        font_size=font_size,
        fg=fg,
    )
    button.AA = PdfDict()
    button.Ff = 65536
    button.MK = PdfDict()
    button.MK.BG = PdfArray(bg)
    button.MK.CA = value
    button.MK.AC = PdfString("hi")

    page.Contents.stream += (
        "\n" + rounded_rect(x, y, width, height, bg, tl, tr, br, bl) + "\n"
    )

    return button


def create_key_buttons(keys_info):
    buttons = []
    for info in keys_info:
        name = info["name"] + "_button"
        key = info["key"]
        button = create_button(
            name,
            info["x"],
            info["y"],
            info["width"],
            info["height"],
            info["name"],
            info["font-size"],
            info["bg"],
            info["fg"],
            info["tl"],
            info["tr"],
            info["bl"],
            info["br"],
        )
        button.AA = PdfDict()
        button.AA.D = create_script(f"key_down('{key}')")
        button.AA.U = create_script(f"key_up('{key}')")
        buttons.append(button)
    return buttons


def rounded_rect(x, y, w, h, color, rtl, rtr, rbr, rbl):
    K = 0.552284749831
    rtl = min(rtl, w / 2, h / 2)
    rtr = min(rtr, w / 2, h / 2)
    rbr = min(rbr, w / 2, h / 2)
    rbl = min(rbl, w / 2, h / 2)

    path = [f"{color[0]:.2f} {color[1]:.2f} {color[2]:.2f} rg"]

    path.append(f"{x + rbl} {y} m")

    path.append(f"{x + w - rbr} {y} l")
    if rbr:
        x0, y0 = x + w - rbr, y
        path.append(
            f"{x0 + rbr*K} {y0} {x0 + rbr} {y0 + rbr*K} {x0 + rbr} {y0 + rbr} c"
        )

    path.append(f"{x + w} {y + h - rtr} l")
    if rtr:
        x0, y0 = x + w, y + h - rtr
        path.append(
            f"{x0} {y0 + rtr*K} {x0 - rtr*K} {y0 + rtr} {x0 - rtr} {y0 + rtr} c"
        )

    path.append(f"{x + rtl} {y + h} l")
    if rtl:
        x0, y0 = x + rtl, y + h
        path.append(
            f"{x0 - rtl*K} {y0} {x0 - rtl} {y0 - rtl*K} {x0 - rtl} {y0 - rtl} c"
        )

    path.append(f"{x} {y + rbl} l")
    if rbl:
        x0, y0 = x, y + rbl
        path.append(
            f"{x0} {y0 - rbl*K} {x0 + rbl*K} {y0 - rbl} {x0 + rbl} {y0 - rbl} c"
        )

    path.append("f")

    return "\n".join(path)


GAMEBOY_WIDTH = 160 * 2
GAMEBOY_HEIGHT = 263 * 2

PDF_WIDTH = GAMEBOY_WIDTH
PDF_HEIGHT = GAMEBOY_HEIGHT

DISPLAY_HEIGHT = 144 * 2

SCREEN_WIDTH = (
    (160 * 0.3067) / 90 * GAMEBOY_WIDTH
)  # 0.3067 is the size of the pixels on the gameboy in mm
SCREEN_HEIGHT = SCREEN_WIDTH / 160 * 144


SCREEN_X = (GAMEBOY_WIDTH - SCREEN_WIDTH) / 2
SCREEN_Y = PDF_HEIGHT - SCREEN_HEIGHT - 48  # Not real, but good enough

BORDER_SIZE = 24


# Buttons
BUTTON_SIZE = 40
GAP = 50  # Gap between arrows and A/B
FONT_SIZE = 15  # Button Font Size

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        js = f.read()

    writer = PdfWriter()
    page = create_page(PDF_WIDTH, PDF_HEIGHT)
    page.AA = PdfDict()
    page.AA.O = create_script("try {" + js + "} catch (e) {app.alert(e.stack || e)}")

    fields = []

    fields.append(
        create_field(
            "fps",
            6,
            PDF_HEIGHT - 8 - 6,
            38,
            8,
            "",
            8,
            (190 / 255, 185 / 255, 180 / 255),
        )
    )
    fields.append(
        create_field(
            "speed",
            PDF_WIDTH - 42 - 6,
            PDF_HEIGHT - 8 - 6,
            42,
            8,
            "",
            8,
            (190 / 255, 185 / 255, 180 / 255),
        )
    )

    for i in range(0, 144):
        field = create_field(
            f"field_{i}",
            SCREEN_X,
            i * (SCREEN_HEIGHT / 144) + SCREEN_Y,
            SCREEN_WIDTH,
            SCREEN_HEIGHT / 144,
            "",
            font_size=1.8 * (SCREEN_HEIGHT / 144),
            bg=[155 / 255, 188 / 255, 15 / 255],
            fg=[15 / 255, 56 / 255, 15 / 255],
        )
        fields.append(field)

    # Bounding rect
    w, h = GAMEBOY_WIDTH - (BORDER_SIZE * 2), SCREEN_HEIGHT + (
        BORDER_SIZE * 2
    )  # width and height
    x, y = SCREEN_X - (BORDER_SIZE * 2), SCREEN_Y - BORDER_SIZE  # bottom-left corner
    r, g, b = 80 / 255, 85 / 255, 100 / 255  # red fill color

    page.Contents.stream += rounded_rect(x, y, w, h, [r, g, b], 10, 10, 40, 10)

    fields += create_key_buttons(
        [
            # Arrows
            {
                "name": "",
                "key": "up",
                "x": (GAMEBOY_WIDTH / 2) - (GAP / 2) - (BUTTON_SIZE * 2),
                "y": GAMEBOY_HEIGHT
                - (
                    DISPLAY_HEIGHT
                    + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2
                    - (BUTTON_SIZE * 1.5)
                ),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (10 / 255, 10 / 255, 20 / 255),
                "fg": (1, 1, 1),
                "tl": 5,
                "tr": 5,
                "bl": 0,
                "br": 0,
            },
            {
                "name": "",
                "key": "down",
                "x": (GAMEBOY_WIDTH / 2) - (GAP / 2) - (BUTTON_SIZE * 2),
                "y": GAMEBOY_HEIGHT
                - (
                    DISPLAY_HEIGHT
                    + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2
                    + (BUTTON_SIZE * 0.5)
                ),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (10 / 255, 10 / 255, 20 / 255),
                "fg": (1, 1, 1),
                "tl": 0,
                "tr": 0,
                "bl": 5,
                "br": 5,
            },
            {
                "name": "",
                "key": "left",
                "x": (GAMEBOY_WIDTH / 2) - (GAP / 2) - (BUTTON_SIZE * 3),
                "y": GAMEBOY_HEIGHT
                - (
                    DISPLAY_HEIGHT
                    + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2
                    - (BUTTON_SIZE * 0.5)
                ),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (10 / 255, 10 / 255, 20 / 255),
                "fg": (1, 1, 1),
                "tl": 5,
                "tr": 0,
                "bl": 5,
                "br": 0,
            },
            {
                "name": "",
                "key": "right",
                "x": (GAMEBOY_WIDTH / 2) - (GAP / 2) - (BUTTON_SIZE),
                "y": GAMEBOY_HEIGHT
                - (
                    DISPLAY_HEIGHT
                    + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2
                    - (BUTTON_SIZE * 0.5)
                ),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (10 / 255, 10 / 255, 20 / 255),
                "fg": (1, 1, 1),
                "tl": 0,
                "tr": 5,
                "bl": 0,
                "br": 5,
            },
            # A/B
            {
                "name": "A",
                "key": "a",
                "x": (GAMEBOY_WIDTH / 2) + (GAP / 2) + (BUTTON_SIZE * 2),
                "y": GAMEBOY_HEIGHT
                - (
                    DISPLAY_HEIGHT
                    + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2
                    - (BUTTON_SIZE)
                ),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (180 / 255, 50 / 255, 95 / 255),
                "fg": (0, 0, 0),
                "tl": BUTTON_SIZE / 2,
                "tr": BUTTON_SIZE / 2,
                "bl": BUTTON_SIZE / 2,
                "br": BUTTON_SIZE / 2,
            },
            {
                "name": "B",
                "key": "b",
                "x": (GAMEBOY_WIDTH / 2) + (GAP / 2) + (BUTTON_SIZE),
                "y": GAMEBOY_HEIGHT
                - (DISPLAY_HEIGHT + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (180 / 255, 50 / 255, 95 / 255),
                "fg": (0, 0, 0),
                "tl": BUTTON_SIZE / 2,
                "tr": BUTTON_SIZE / 2,
                "bl": BUTTON_SIZE / 2,
                "br": BUTTON_SIZE / 2,
            },
            # Start/Select
            {
                "name": "Start",
                "key": "start",
                "x": (GAMEBOY_WIDTH / 2) - 50 - 5,
                "y": 62,
                "width": 50,
                "height": BUTTON_SIZE / 2,
                "font-size": FONT_SIZE,
                "bg": (140 / 255, 140 / 255, 140 / 255),
                "fg": (0, 0, 0),
                "tl": 5,
                "tr": 5,
                "bl": 5,
                "br": 5,
            },
            {
                "name": "Select",
                "key": "select",
                "x": (GAMEBOY_WIDTH / 2) + 5,
                "y": 62,
                "width": 50,
                "height": BUTTON_SIZE / 2,
                "font-size": FONT_SIZE,
                "bg": (140 / 255, 140 / 255, 140 / 255),
                "fg": (0, 0, 0),
                "tl": 5,
                "tr": 5,
                "bl": 5,
                "br": 5,
            },
        ]
    )

    page.Contents.stream += "\n".join(
        [
            create_text(
                SCREEN_X - (BORDER_SIZE * 2),
                SCREEN_Y - BORDER_SIZE - 32,
                24,
                "PDFBoy",
                (0, 0, 0.8),
                bold=True
            ),
            # Bottom text
            create_text(
                6,
                6,
                8,
                "Upload ROM (.gb) file at: https://gameboy.doompdf.dev/",
            ),
            create_text(
                6,
                16,
                8,
                "Source Code: https://github.com/simplyrohan/pdfboy",
            ),
            create_text(
                6,
                26,
                8,
                "This PDF only works in Chromium based browsers",
            ),
        ]
    )

    page.Annots = PdfArray(fields)
    writer.addpage(page)
    writer.write(sys.argv[2])
    print("Wrote PDF to " + sys.argv[2])
