import random

if __name__ == "__main__":
    with open(
        "g22_06_trade_test_out_second_layer.hpgl", "w", encoding="utf8"
    ) as outfile:
        with open("g22_06_trade_styles2.txt", "r") as infile:
            for line in infile:
                pen = random.randint(1, 4)
                outfile.write(f"SP{pen};\n")
                outfile.write(f"LB{line.strip()}{chr(3)}\n")
                outfile.write("CP;\n")
