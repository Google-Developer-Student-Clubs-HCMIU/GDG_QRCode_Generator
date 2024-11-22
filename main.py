### From Academic/Technical Leader From Google Developer Group on Campus - International University - VNU-HCMIU ###
###                                        https://gdgiu.dev/ with love                                         ###

import qrcode
from utils import CircleModuleDrawer,StyledPilImage
from PIL import Image, ImageOps

def create_qr_code_with_logo(url, logo_path, output_path):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    qr_image = qr.make_image(image_factory=StyledPilImage, module_drawer=CircleModuleDrawer()).convert("RGBA")
    qr_image = ImageOps.expand(qr_image, border=20, fill=(255, 255, 255))

    background = Image.new('RGBA', qr_image.size, 'WHITE')
    qr_image = Image.alpha_composite(background, qr_image)

    logo = Image.open(logo_path)
    logo_size = (155, 75)
    logo = logo.resize(logo_size, Image.LANCZOS)

    logo_padding = 10
    padded_logo = ImageOps.expand(logo, border=logo_padding, fill="white")

    qr_width, qr_height = qr_image.size
    logo_width, logo_height = padded_logo.size
    logo_position = (
        (qr_width - logo_width) // 2,
        (qr_height - logo_height) // 2,
    )
    qr_image.paste(padded_logo, logo_position, mask=padded_logo if padded_logo.mode == 'RGBA' else None)

    qr_image.save(output_path)
    print(f"QR code with logo saved to {output_path}")


create_qr_code_with_logo(
    url="https://gdgiu.dev/",
    logo_path="logo/gdg.png",  
    output_path="output/qr_code.png",  
)
