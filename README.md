## **GDG_QRCode_Generator - Overview**
This project is a Python-based script that generates QR codes with a custom design. The QR codes are styled with circular modules and include a logo overlay in the center. The script is built upon the open-source [qrcode](https://github.com/lincolnloop/python-qrcode) library, extended with additional functionality for custom module styling and logo integration.

---

## **Features**
1. **Custom Circular Modules**:  
   - Uses a `CircleModuleDrawer` subclass to create QR codes with stylish circular modules.  
2. **Logo Overlay**:  
   - Adds a logo in the center of the QR code with customizable padding for better integration.  
3. **High Error Correction**:  
   - Ensures the QR code remains scannable even with a logo overlay by using a high error correction level.  
4. **White Background**:  
   - Generates QR codes with a clean, professional appearance by adding a white background.  
5. **Customizable Settings**:  
   - Easily adjust QR code size, border, logo dimensions, and padding to fit your needs.  

---

## **Requirements**
- Python 3.6 or higher  
- Libraries:  
  - `qrcode`  
  - `Pillow`  

---

## **Installation**
1. Clone the repository:  
   ```bash
   git clone https://github.com/GDG_QRCode_Generator.git
   cd GDG_QRCode_Generator
   ```
2. Install the required dependencies:  
   ```bash
   pip install qrcode pillow
   ```
3. Ensure your logo file is in the `logo/` directory (e.g., `logo/gdg.png`).

---

## **Usage**
1. **Edit the Code**:  
   Replace the URL, logo path, and output path in the script.  
   ```python
   create_qr_code_with_logo(
       url="https://gdgiu.dev/",
       logo_path="logo/gdg.png",  
       output_path="output/qr_code.png",  
   )
   ```
   And your logo dimension, adjust until fit.
   example:
   ```python
    logo_size = (155, 75)
   ```
2. **Run the Script**:  
   ```bash
   python main.py
   ```

3. **Output**:  
   - The QR code will be saved in the specified `output/` directory with the file name `qr_code.png`.

4. **More option**:
   - You can change the position markers style in utils.py file,
   ```python
       default_drawer_class = RoundedModuleDrawer
   ```
   Change RoundedModuleDrawer to SquareModuleDrawer or GappedSquareModuleDrawer as you like. 
   Additionally, you can import more style from [qrcode](https://github.com/lincolnloop/python-qrcode) library.
---

## **Customization**
- **Box Size**: Adjust the `box_size` parameter in the `QRCode` object to control the size of individual QR code modules.  
- **Border Size**: Modify the `border` parameter to change the size of the white border around the QR code.  
- **Logo Size**: Update the `logo_size` variable to control the dimensions of the logo.  
- **Padding**: Change the `logo_padding` variable to adjust the space around the logo.

---

## **Example**
### Generated QR Code:  
- The script generates a QR code for the URL `https://gdgiu.dev/` with the GDG logo placed in the center.  
- Example output:

<img src="output/qr_code.png" width="300" height="300" />

---

## **Acknowledgments**
- This project is based on the [qrcode](https://github.com/lincolnloop/python-qrcode) library by [Lincoln Loop](https://lincolnloop.com/), licensed under the MIT License.  
- Modifications include custom `CircleModuleDrawer` functionality to add padding for circular modules.  
- Special thanks to the open-source community for their valuable tools and resources.

---

## **Credits**
- Developed by the **Academic/Technical Leader** from **Google Developer Group on Campus - International University - VNU-HCM**.  
- Website: [https://gdgiu.dev/](https://gdgiu.dev/)  
- With ❤️ from **Google Developer Group on Campus - IU**.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.  