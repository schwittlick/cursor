from PIL import Image
import pytesseract

if __name__ == "__main__":
    im1 = "Z:\\Dropbox\\0_MARCELSCHWITTLICK\\2020_DRAWING_PHOTOS\\c71\\20220304_crop area 1.jpg"
    print(pytesseract.image_to_string(Image.open(im1)))

    print(pytesseract.image_to_string(Image.open(im1), lang='deu'))
