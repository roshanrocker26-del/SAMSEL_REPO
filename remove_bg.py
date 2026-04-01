from PIL import Image

def remove_white_background(image_path, output_path, tolerance=25):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # white is (255, 255, 255)
    for item in datas:
        # Check if pixel is white or near white
        if (item[0] >= 255 - tolerance and 
            item[1] >= 255 - tolerance and 
            item[2] >= 255 - tolerance):
            newData.append((255, 255, 255, 0)) # Transparent
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")

remove_white_background(
    r"C:\Users\HP\.gemini\antigravity\brain\7f9dbe8f-366e-44a9-8f99-3435b5c38539\media__1774940587531.png",
    r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\static\images\st_joseph_nobg.png",
    tolerance=50
)
print("Background removed successfully.")
