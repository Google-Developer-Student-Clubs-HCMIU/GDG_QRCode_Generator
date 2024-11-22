# This script extends the `qrcode` library by Lincoln Loop (https://github.com/lincolnloop/python-qrcode).
# Original library licensed under MIT. Enhancements include a custom `CircleModuleDrawer` for padded dots.

from typing import TYPE_CHECKING, List
from qrcode.image.styledpil import StyledPilImage
from PIL import Image, ImageDraw
from qrcode.image.styles.moduledrawers.base import QRModuleDrawer
import qrcode.image.base
from PIL import Image
from qrcode.image.styles.colormasks import QRColorMask, SolidFillColorMask
from qrcode.image.styles.moduledrawers import SquareModuleDrawer,GappedSquareModuleDrawer,RoundedModuleDrawer


class StyledPilImage(qrcode.image.base.BaseImageWithDrawer):
    """
    Modify the default_drawer_class in this file to change the style of the 
    position markers of the QR code.

    Styled PIL image builder, default format is PNG.

    This differs from the PilImage in that there is a module_drawer, a
    color_mask, and an optional image

    The module_drawer should extend the QRModuleDrawer class and implement the
    drawrect_context(self, box, active, context), and probably also the
    initialize function. This will draw an individual "module" or square on
    the QR code.

    The color_mask will extend the QRColorMask class and will at very least
    implement the get_fg_pixel(image, x, y) function, calculating a color to
    put on the image at the pixel location (x,y) (more advanced functionality
    can be gotten by instead overriding other functions defined in the
    QRColorMask class)

    The Image can be specified either by path or with a Pillow Image, and if it
    is there will be placed in the middle of the QR code. No effort is done to
    ensure that the QR code is still legible after the image has been placed
    there; Q or H level error correction levels are recommended to maintain
    data integrity A resampling filter can be specified (defaulting to
    PIL.Image.Resampling.LANCZOS) for resizing; see PIL.Image.resize() for possible
    options for this parameter.
    The image size can be controlled by `embeded_image_ratio` which is a ratio
    between 0 and 1 that's set in relation to the overall width of the QR code.
    """

    kind = "PNG"

    needs_processing = True
    color_mask: QRColorMask
    default_drawer_class = RoundedModuleDrawer

    def __init__(self, *args, **kwargs):
        self.color_mask = kwargs.get("color_mask", SolidFillColorMask())
        embeded_image_path = kwargs.get("embeded_image_path", None)
        self.embeded_image = kwargs.get("embeded_image", None)
        self.embeded_image_ratio = kwargs.get("embeded_image_ratio", 0.25)
        self.embeded_image_resample = kwargs.get(
            "embeded_image_resample", Image.Resampling.LANCZOS
        )
        if not self.embeded_image and embeded_image_path:
            self.embeded_image = Image.open(embeded_image_path)

        # the paint_color is the color the module drawer will use to draw upon
        # a canvas During the color mask process, pixels that are paint_color
        # are replaced by a newly-calculated color
        self.paint_color = tuple(0 for i in self.color_mask.back_color)
        if self.color_mask.has_transparency:
            self.paint_color = tuple([*self.color_mask.back_color[:3], 255])

        super().__init__(*args, **kwargs)

    def new_image(self, **kwargs):
        mode = (
            "RGBA"
            if (
                self.color_mask.has_transparency
                or (self.embeded_image and "A" in self.embeded_image.getbands())
            )
            else "RGB"
        )
        # This is the background color. Should be white or whiteish
        back_color = self.color_mask.back_color

        return Image.new(mode, (self.pixel_size, self.pixel_size), back_color)

    def init_new_image(self):
        self.color_mask.initialize(self, self._img)
        super().init_new_image()

    def process(self):
        self.color_mask.apply_mask(self._img)
        if self.embeded_image:
            self.draw_embeded_image()

    def draw_embeded_image(self):
        if not self.embeded_image:
            return
        total_width, _ = self._img.size
        total_width = int(total_width)
        logo_width_ish = int(total_width * self.embeded_image_ratio)
        logo_offset = (
            int((int(total_width / 2) - int(logo_width_ish / 2)) / self.box_size)
            * self.box_size
        )  # round the offset to the nearest module
        logo_position = (logo_offset, logo_offset)
        logo_width = total_width - logo_offset * 2
        region = self.embeded_image
        region = region.resize((logo_width, logo_width), self.embeded_image_resample)
        if "A" in region.getbands():
            self._img.alpha_composite(region, logo_position)
        else:
            self._img.paste(region, logo_position)

    def save(self, stream, format=None, **kwargs):
        if format is None:
            format = kwargs.get("kind", self.kind)
        if "kind" in kwargs:
            del kwargs["kind"]
        self._img.save(stream, format=format, **kwargs)

    def __getattr__(self, name):
        return getattr(self._img, name)

if TYPE_CHECKING:
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.main import ActiveWithNeighbors

# When drawing antialiased things, make them bigger and then shrink them down
# to size after the geometry has been drawn.
ANTIALIASING_FACTOR = 4


class StyledPilQRModuleDrawer(QRModuleDrawer):
    """
    A base class for StyledPilImage module drawers.

    NOTE: the color that this draws in should be whatever is equivalent to
    black in the color space, and the specified QRColorMask will handle adding
    colors as necessary to the image
    """

    img: "StyledPilImage"


class SquareModuleDrawer(StyledPilQRModuleDrawer):
    """
    Draws the modules as simple squares
    """

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.imgDraw = ImageDraw.Draw(self.img._img)

    def drawrect(self, box, is_active: bool):
        if is_active:
            self.imgDraw.rectangle(box, fill=self.img.paint_color)


class GappedSquareModuleDrawer(StyledPilQRModuleDrawer):
    """
    Draws the modules as simple squares that are not contiguous.

    The size_ratio determines how wide the squares are relative to the width of
    the space they are printed in
    """

    def __init__(self, size_ratio=0.8):
        self.size_ratio = size_ratio

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.imgDraw = ImageDraw.Draw(self.img._img)
        self.delta = (1 - self.size_ratio) * self.img.box_size / 2

    def drawrect(self, box, is_active: bool):
        if is_active:
            smaller_box = (
                box[0][0] + self.delta,
                box[0][1] + self.delta,
                box[1][0] - self.delta,
                box[1][1] - self.delta,
            )
            self.imgDraw.rectangle(smaller_box, fill=self.img.paint_color)


class CircleModuleDrawer(StyledPilQRModuleDrawer):
    """
    Draws the modules as circles with optional padding
    """

    circle = None

    def __init__(self, padding_ratio=0.15):
        self.padding_ratio = padding_ratio

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        box_size = self.img.box_size
        padding = int(box_size * self.padding_ratio)
        fake_size = (box_size - 2 * padding) * ANTIALIASING_FACTOR
        self.circle = Image.new(
            self.img.mode,
            (fake_size, fake_size),
            self.img.color_mask.back_color,
        )
        ImageDraw.Draw(self.circle).ellipse(
            (0, 0, fake_size, fake_size), fill=self.img.paint_color
        )
        self.circle = self.circle.resize((box_size - 2 * padding, box_size - 2 * padding), Image.Resampling.LANCZOS)
        self.padding = padding

    def drawrect(self, box, is_active: bool):
        if is_active:
            self.img._img.paste(self.circle, (box[0][0] + self.padding, box[0][1] + self.padding))



class RoundedModuleDrawer(StyledPilQRModuleDrawer):
    """
    Draws the modules with all 90 degree corners replaced with rounded edges.

    radius_ratio determines the radius of the rounded edges - a value of 1
    means that an isolated module will be drawn as a circle, while a value of 0
    means that the radius of the rounded edge will be 0 (and thus back to 90
    degrees again).
    """

    needs_neighbors = True

    def __init__(self, radius_ratio=1):
        self.radius_ratio = radius_ratio

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.corner_width = int(self.img.box_size / 2)
        self.setup_corners()

    def setup_corners(self):
        mode = self.img.mode
        back_color = self.img.color_mask.back_color
        front_color = self.img.paint_color
        self.SQUARE = Image.new(
            mode, (self.corner_width, self.corner_width), front_color
        )

        fake_width = self.corner_width * ANTIALIASING_FACTOR
        radius = self.radius_ratio * fake_width
        diameter = radius * 2
        base = Image.new(
            mode, (fake_width, fake_width), back_color
        )  # make something 4x bigger for antialiasing
        base_draw = ImageDraw.Draw(base)
        base_draw.ellipse((0, 0, diameter, diameter), fill=front_color)
        base_draw.rectangle((radius, 0, fake_width, fake_width), fill=front_color)
        base_draw.rectangle((0, radius, fake_width, fake_width), fill=front_color)
        self.NW_ROUND = base.resize(
            (self.corner_width, self.corner_width), Image.Resampling.LANCZOS
        )
        self.SW_ROUND = self.NW_ROUND.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.SE_ROUND = self.NW_ROUND.transpose(Image.Transpose.ROTATE_180)
        self.NE_ROUND = self.NW_ROUND.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def drawrect(self, box: List[List[int]], is_active: "ActiveWithNeighbors"):
        if not is_active:
            return
        # find rounded edges
        nw_rounded = not is_active.W and not is_active.N
        ne_rounded = not is_active.N and not is_active.E
        se_rounded = not is_active.E and not is_active.S
        sw_rounded = not is_active.S and not is_active.W

        nw = self.NW_ROUND if nw_rounded else self.SQUARE
        ne = self.NE_ROUND if ne_rounded else self.SQUARE
        se = self.SE_ROUND if se_rounded else self.SQUARE
        sw = self.SW_ROUND if sw_rounded else self.SQUARE
        self.img._img.paste(nw, (box[0][0], box[0][1]))
        self.img._img.paste(ne, (box[0][0] + self.corner_width, box[0][1]))
        self.img._img.paste(
            se, (box[0][0] + self.corner_width, box[0][1] + self.corner_width)
        )
        self.img._img.paste(sw, (box[0][0], box[0][1] + self.corner_width))


class VerticalBarsDrawer(StyledPilQRModuleDrawer):
    """
    Draws vertically contiguous groups of modules as long rounded rectangles,
    with gaps between neighboring bands (the size of these gaps is inversely
    proportional to the horizontal_shrink).
    """

    needs_neighbors = True

    def __init__(self, horizontal_shrink=0.8):
        self.horizontal_shrink = horizontal_shrink

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.half_height = int(self.img.box_size / 2)
        self.delta = int((1 - self.horizontal_shrink) * self.half_height)
        self.setup_edges()

    def setup_edges(self):
        mode = self.img.mode
        back_color = self.img.color_mask.back_color
        front_color = self.img.paint_color

        height = self.half_height
        width = height * 2
        shrunken_width = int(width * self.horizontal_shrink)
        self.SQUARE = Image.new(mode, (shrunken_width, height), front_color)

        fake_width = width * ANTIALIASING_FACTOR
        fake_height = height * ANTIALIASING_FACTOR
        base = Image.new(
            mode, (fake_width, fake_height), back_color
        )  # make something 4x bigger for antialiasing
        base_draw = ImageDraw.Draw(base)
        base_draw.ellipse((0, 0, fake_width, fake_height * 2), fill=front_color)

        self.ROUND_TOP = base.resize((shrunken_width, height), Image.Resampling.LANCZOS)
        self.ROUND_BOTTOM = self.ROUND_TOP.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def drawrect(self, box, is_active: "ActiveWithNeighbors"):
        if is_active:
            # find rounded edges
            top_rounded = not is_active.N
            bottom_rounded = not is_active.S

            top = self.ROUND_TOP if top_rounded else self.SQUARE
            bottom = self.ROUND_BOTTOM if bottom_rounded else self.SQUARE
            self.img._img.paste(top, (box[0][0] + self.delta, box[0][1]))
            self.img._img.paste(
                bottom, (box[0][0] + self.delta, box[0][1] + self.half_height)
            )


class HorizontalBarsDrawer(StyledPilQRModuleDrawer):
    """
    Draws horizontally contiguous groups of modules as long rounded rectangles,
    with gaps between neighboring bands (the size of these gaps is inversely
    proportional to the vertical_shrink).
    """

    needs_neighbors = True

    def __init__(self, vertical_shrink=0.8):
        self.vertical_shrink = vertical_shrink

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.half_width = int(self.img.box_size / 2)
        self.delta = int((1 - self.vertical_shrink) * self.half_width)
        self.setup_edges()

    def setup_edges(self):
        mode = self.img.mode
        back_color = self.img.color_mask.back_color
        front_color = self.img.paint_color

        width = self.half_width
        height = width * 2
        shrunken_height = int(height * self.vertical_shrink)
        self.SQUARE = Image.new(mode, (width, shrunken_height), front_color)

        fake_width = width * ANTIALIASING_FACTOR
        fake_height = height * ANTIALIASING_FACTOR
        base = Image.new(
            mode, (fake_width, fake_height), back_color
        )  # make something 4x bigger for antialiasing
        base_draw = ImageDraw.Draw(base)
        base_draw.ellipse((0, 0, fake_width * 2, fake_height), fill=front_color)

        self.ROUND_LEFT = base.resize(
            (width, shrunken_height), Image.Resampling.LANCZOS
        )
        self.ROUND_RIGHT = self.ROUND_LEFT.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def drawrect(self, box, is_active: "ActiveWithNeighbors"):
        if is_active:
            # find rounded edges
            left_rounded = not is_active.W
            right_rounded = not is_active.E

            left = self.ROUND_LEFT if left_rounded else self.SQUARE
            right = self.ROUND_RIGHT if right_rounded else self.SQUARE
            self.img._img.paste(left, (box[0][0], box[0][1] + self.delta))
            self.img._img.paste(
                right, (box[0][0] + self.half_width, box[0][1] + self.delta)
            )

class CustomStyledPilImage(StyledPilImage):
    def drawrect(self, box, is_active):
        if not is_active:
            return

        draw = ImageDraw.Draw(self._img)
        draw.rounded_rectangle(box, radius=10, fill=self._color)

    def drawfinder(self, row, col):
        size = self.box_size * 7
        box = (col * self.box_size, row * self.box_size, col * self.box_size + size, row * self.box_size + size)
        draw = ImageDraw.Draw(self._img)
        draw.ellipse(box, outline='white', width=self.box_size)
        inner_box = (
            box[0] + self.box_size * 2,
            box[1] + self.box_size * 2,
            box[2] - self.box_size * 2,
            box[3] - self.box_size * 2,
        )
        draw.ellipse(inner_box, fill=self._color)