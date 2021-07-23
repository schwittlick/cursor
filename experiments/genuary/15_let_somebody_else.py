from cursor import data
from cursor import device
from cursor import path
from cursor import renderer

import random
import sys


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


if __name__ == "__main__":

    lines = []
    lines.append("Last login: Fri Jan 15 12:29:49 on console")
    lines.append("My-Mini:~ Me$ traceroute -m 60 www.jakarta.go.id")
    lines.append(
        "traceroute to jakarta.go.id (103.209.7.21), 60 hops max, 52 byte packets"
    )
    lines.append("1 o2.box (192.168.1.1)  3.058ms  3.572ms  3.475ms")
    lines.append(
        "3  ae13-0.0001.dbrx.02.ber.de.net.telefonica.de (62.53.11.216)  14.309ms"
    )
    lines.append(
        "   ae13-0.0002.dbrx.02.ber.de.net.telefonica.de (62.53.11.218)  16.351ms  16.359ms"
    )
    lines.append(
        "4  ae0-0.0002.prrx.02.ber.de.net.telefonica.de (62.53.12.59)  12.455ms  13.528ms"
    )
    lines.append(
        "   ae1-0.0001.prrx.02.ber.de.net.telefonica.de (62.53.4.155)  12.896ms"
    )
    lines.append(
        "5  hurricane-electric.bcix.de (193.178.185.34)  13.290ms  14.325ms  14.981ms"
    )
    lines.append("6  as6939.muc.ecix.net (194.59.190.69)  26.665ms  28.764ms  26.742ms")
    lines.append(
        "7  100ge13-2.core1.zrh2.he.net (184.105.65.41)  31.007ms  30.751ms  30.478ms"
    )
    lines.append(
        "8  100ge0-35.core2.zrh3.he.net (72.52.92.130)  57.426ms  32.029ms  31.455ms"
    )
    lines.append(
        "9  100ge0-35.core2.gva1.he.net (184.104.193.134)  34.833ms  34.310ms  34.949ms"
    )
    lines.append(
        "10  100ge16-2.core1.mrs1.he.net (184.104.193.125)  39.830ms  39.790ms  39.731ms"
    )
    lines.append(
        "11  100ge14-2.core1.sin1.he.net (184.105.65.13)  173.614ms  177.161ms  192.652ms"
    )
    lines.append(
        "13  ip-103-83-6-17.moratelindo.net.id (103.83.6.17)  193.801ms  194.040ms  319.188ms"
    )
    lines.append(
        "14  ip-103-83-6-109.moratelindo.net.id (103.83.6.109)  306.243ms  307.310ms  265.145ms"
    )
    lines.append(
        "15  ip-103-56-232-142.moratelindo.net.id (103.56.232.142)  199.450ms  195.834ms  237.249ms"
    )
    lines.append(
        "16  pan.jakarta.go.id (103.209.7.253)  206.471ms  211.976ms  218.373ms"
    )
    lines.append(
        "17  ip-251-180.moratelindo.co.id (103.22.251.180)  200.790ms  330.999ms  194.675ms"
    )
    lines.append(
        "18  ip-251-180.moratelindo.co.id (103.22.251.180)  200.015ms  195.273ms  206.848ms"
    )
    lines.append(
        "19  ip-251-180.moratelindo.co.id (103.22.251.180)  188.493ms  242.604ms  306.352ms"
    )
    lines.append(
        "20  ip-251-180.moratelindo.co.id (103.22.251.180)  201.641ms  187.424ms  197.011ms"
    )
    lines.append("21  * * *")
    lines.append("22  * * *")
    lines.append("23  * * *")
    lines.append("24  * * *")
    lines.append("25  * * *")
    lines.append("26  * * ip-251-180.moratelindo.co.id (103.22.251.180)  1209.177ms !H")
    lines.append("27  * * *")
    lines.append("28  ip-251-180.moratelindo.co.id (103.22.251.180)  1189.816ms !H * *")
    lines.append("29  * ip-251-180.moratelindo.co.id (103.22.251.180)  1247.128ms !H *")
    lines.append("30  * * ip-251-180.moratelindo.co.id (103.22.251.180)  1269.827ms !H")
    lines.append("31  * * *")
    lines.append("32  * * *")
    lines.append("33  * * *")
    lines.append("34  * * ip-251-180.moratelindo.co.id (103.22.251.180)  1285.917ms !H")
    lines.append("35  * * *")
    lines.append("36  ip-251-180.moratelindo.co.id (103.22.251.180)  1278.009ms !H * *")
    lines.append("37  * * *")
    lines.append("38  * * *")
    lines.append("39  * * *")
    lines.append("40  ip-251-180.moratelindo.co.id (103.22.251.180)  1214.396ms !H * *")
    lines.append("41  * * ip-251-180.moratelindo.co.id (103.22.251.180)  4651.336ms !H")
    lines.append("42  * * *")
    lines.append("43  * * *")
    lines.append("44  * * *")
    lines.append("45  * ip-251-180.moratelindo.co.id (103.22.251.180)  1287.057ms !H *")
    lines.append("46  * * ip-251-180.moratelindo.co.id (103.22.251.180)  1216.282ms !H")
    lines.append("47  * * *")
    lines.append("48  * * *")
    lines.append("49  * * *")
    lines.append("50  * * ip-251-180.moratelindo.co.id (103.22.251.180)  1201.671ms !H")
    lines.append("51  * * *")
    lines.append("52  * * *")
    lines.append("53  * * *")
    lines.append("54  * * *")
    lines.append("55  * * *")
    lines.append("56  * * *")
    lines.append("57  * * *")
    lines.append("58  * * *")
    lines.append("59  * * *")
    lines.append("60  * * *")

    parts = []
    for line in lines:
        p = line.split()
        for _ in p:
            parts.append(_)

    with open("genuary15_let_somebody.hpgl", "w") as f:
        f.write("SP1;\n")
        mm = device.MinmaxMapping.maps[device.PlotterType.ROLAND_DXY980]
        f.write("DT~,1;\n")
        counter = 0
        for ip in parts:
            mx = mm.minx
            mx2 = mm.maxx
            x = random.randint(-200, mx2)
            y = random.randint(-200, mm.maxy)

            f.write(f"PU{x},{y};\n")
            # f.write("PD;\n")
            f.write(f"LB{ip.rstrip()}~;\n")

            counter += 1
            # if counter >= 1000:

        f.write("SP0;\n")
        sys.exit(0)

    pc = path.PathCollection()

    p1 = path.Path()
    p1.add(534231, 5683224)
    p1.add(603776, 4178842)
    p1.add(702184, 9317347)
    p1.add(702449, 9317202)

    pc.add(p1)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A3,
        50,
        "genuary",
        "15_let_somebody",
    )
