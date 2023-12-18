import arrr
from pyscript import document
import spline


def translate_english(event):
    print("Lol")
    print(event)
    chain_points: list = spline.catmull_rom_chain([(0, 0), (1, 1), (2, 3), (4, 1)], 4)
    print(chain_points)
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = arrr.translate(english)
