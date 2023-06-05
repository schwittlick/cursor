from HersheyFonts import HersheyFonts
def draw_line(x1, y1, x2, y2):
    print(x1, y1)

if __name__ == "__main__":
    thefont = HersheyFonts()
    thefont.load_default_font()
    thefont.normalize_rendering(100)
    for (x1, y1), (x2, y2) in thefont.lines_for_text('Test'):
        draw_line(x1, y1, x2, y2)