from PIL import Image, ImageOps
import os, subprocess, shutil

try:
    shutil.rmtree("input/temp")
except:
    pass

os.makedirs("output", exist_ok=True)
os.system("cls")

for texture in os.listdir("input"):
    print("Converting texture: " + texture)

    # Check if the texture is alpha using PIL, and save an alpha copy
    os.makedirs("input/temp", exist_ok=True)

    img_path = os.path.join("input", texture)
    img = Image.open(img_path).convert("RGBA")
    
    def getAlphaChannel(texture):
        img = Image.open('input//' + texture)
        if img.info.get("transparency", None) is not None:
            return True
        if img.mode == "P":
            transparent = img.info.get("transparency", -1)
            for _, index in img.getcolors():
                if index == transparent:
                    return True
        elif img.mode == "RGBA":
            extrema = img.getextrema()
            if extrema[3][0] < 255:
                return True
        return False
    
    if getAlphaChannel(texture):
        img.save("input/" + texture, 'PNG')
        img = Image.open(img_path).convert("RGBA")
        alpha = img.split()[3]
        alpha.save("input/temp/ALPHA_" + texture, 'PNG')
        
        # Invert and reinvert colors of the original image
        rimg = Image.open(img_path).convert("RGB")  # Convert to RGB before inverting
        rimg = ImageOps.invert(ImageOps.invert(rimg))  # Invert colors in one line
        rimg.save("input/temp/" + texture, 'PNG')
        
        # Create an extended image (original + alpha below)
        new_image = Image.new('RGBA', (img.width, img.height * 2), (0, 0, 0, 0))
        new_image.paste(Image.open("input/temp/" + texture), (0, 0))  # Paste the original image
        new_image.paste(Image.open(os.path.join("input/temp", f"ALPHA_{texture}")), (0, img.height))  # Paste the alpha image

        # Save the image
        new_image.save(f"input/temp/FINAL_{texture}", 'PNG')
        res1, res2 = new_image.width, new_image.height // 2

        img_type_bytes = b'\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x54\x54\x56\x4E\x00\x02\x00\x07\x00\x00\x00\x20\x00\x00\x00\x41\x41\x50\x4D\x43\x00\x00\x00\x20\x00\xFF\x00\x00\x00\x00\xFF\x00\x00\x00\x00\xFF\xFF\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    else:
        img.save(f"input/temp/FINAL_{texture}", 'PNG')
        res1, res2 = img.width, img.height # Cause this is a non-alpha texture, we can just use the original image
        
        # This is the img_type_bytes for a non-alpha texture
        img_type_bytes = b'\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x54\x54\x56\x4E\x00\x02\x00\x07\x00\x00\x00\x20\x00\x00\x00\x04\x31\x54\x58\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' 

    # Wimgt
    subprocess.run(['utils/wimgt/wimgt', 'copy', os.path.join('.', 'input', 'temp', f'FINAL_{texture}'), '--dest', os.path.join('.', 'input', 'temp', f'{texture}.tpl'), '--transform', 'tpl.cmpr'], check=True, stderr=subprocess.DEVNULL)

    # FINALLY, MAKE THE TEXTURE
    with open("input/temp/" + texture + ".tpl", "rb") as f:
        tpl = f.read()
        
    ckd = b'\x00\x00\x00\x09\x54\x45\x58\x00\x00\x00\x00\x2C\x00\x04\x00\x80\x04\x00\x04\x00\x00\x01\x20\x00\x00\x04\x00\x80\x00\x00\x00\x00\x00\x02\xAA\xEA\x00\x09\xC2\xE7\x00\x00\xCC\xCC\x20\x53\x44\x44\x00\x00\x00\x7C\x00\x00\x10\x0F'
    ckd += res2.to_bytes(4, "big") + res1.to_bytes(4, "big")
    ckd += img_type_bytes
    ckd += tpl[64:]
        
    with open("output/" + texture.split(".")[0] + ".tga.ckd", 'wb') as outfile:
        outfile.write("".encode('utf8'))
        num_bytes_written = outfile.write(ckd)

shutil.rmtree("input/temp")