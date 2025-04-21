# PDF Generator from DoomPDF
# Will probably be replaced soon
import sys

from pdfrw import PdfWriter
from pdfrw.objects.pdfname import PdfName
from pdfrw.objects.pdfstring import PdfString
from pdfrw.objects.pdfdict import PdfDict
from pdfrw.objects.pdfarray import PdfArray
from pdfrw.objects.pdfobject import PdfObject


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


def create_text(x, y, size, txt):
    return f"""
  BT
  /Helvetica {size} Tf
  {x} {y} Td ({txt}) Tj
  ET
  """


def create_button(name, x, y, width, height, value, font_size, bg, fg):
    button = create_field(
        name, x, y, width, height, f_type=PdfName.Btn, font_size=font_size, fg=fg
    )
    button.AA = PdfDict()
    button.Ff = 65536
    button.MK = PdfDict()
    button.MK.BG = PdfArray(bg)
    button.MK.CA = value
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
        )
        button.AA = PdfDict()
        button.AA.D = create_script(f"key_down('{key}')")
        button.AA.U = create_script(f"key_up('{key}')")
        buttons.append(button)
    return buttons


GAMEBOY_WIDTH = 160 * 2
GAMEBOY_HEIGHT = 263 * 2

DISPLAY_HEIGHT = 144 * 2

SCREEN_WIDTH = (
    (160 * 0.3067) / 90 * GAMEBOY_WIDTH
)  # 0.3067 is the size of the pixels on the gameboy in mm
SCREEN_HEIGHT = SCREEN_WIDTH / 160 * 144


SCREEN_X = (GAMEBOY_WIDTH - SCREEN_WIDTH) / 2
SCREEN_Y = GAMEBOY_HEIGHT - (SCREEN_X + SCREEN_HEIGHT)  # Not real, but good enough

PDF_WIDTH = GAMEBOY_WIDTH
PDF_HEIGHT = GAMEBOY_HEIGHT

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
    w, h = GAMEBOY_WIDTH - 48, SCREEN_HEIGHT + 48  # width and height
    x, y = 24, SCREEN_Y - 24  # bottom-left corner
    r, g, b = 80 / 255, 85 / 255, 100 / 255  # red fill color

    # PDF drawing commands
    rect = f"""
    {r} {g} {b} rg            % Set fill color (RGB)
    {x} {y} {w} {h} re        % Define rectangle
    f                         % Fill the rectangle
    """

    page.Contents.stream += rect

    fields += create_key_buttons(
        [
            # Arrows
            {
                "name": "^",
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
            },
            {
                "name": "v",
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
            },
            {
                "name": "<",
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
            },
            {
                "name": ">",
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
            },
            # A/B
            {
                "name": "A",
                "key": "a",
                "x": (GAMEBOY_WIDTH / 2) + (GAP / 2) + (BUTTON_SIZE) + 2.5,
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
            },
            {
                "name": "B",
                "key": "b",
                "x": (GAMEBOY_WIDTH / 2) + (GAP / 2) - 2.5,
                "y": GAMEBOY_HEIGHT
                - (DISPLAY_HEIGHT + (GAMEBOY_HEIGHT - DISPLAY_HEIGHT) / 2),
                "width": BUTTON_SIZE,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (180 / 255, 50 / 255, 95 / 255),
                "fg": (0, 0, 0),
            },
            # Start/Select
            {
                "name": "Start",
                "key": "start",
                "x": (GAMEBOY_WIDTH / 2) - 50 - 5,
                "y": 24,
                "width": 50,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (140 / 255, 140 / 255, 140 / 255),
                "fg": (0, 0, 0),
            },
            {
                "name": "Select",
                "key": "select",
                "x": (GAMEBOY_WIDTH / 2) + 5,
                "y": 24,
                "width": 50,
                "height": BUTTON_SIZE,
                "font-size": FONT_SIZE,
                "bg": (140 / 255, 140 / 255, 140 / 255),
                "fg": (0, 0, 0),
            },
        ]
    )

    # Meta
    # for i in range(0, 25):
    #     field = create_field(f"console_{i}", GAMEBOY_WIDTH + 12, 8 + i * 8, 100, 8, "")
    #     fields.append(field)

    page.Annots = PdfArray(fields)
    writer.addpage(page)
    writer.write(sys.argv[2])
    print("Wrote PDF to " + sys.argv[2])
