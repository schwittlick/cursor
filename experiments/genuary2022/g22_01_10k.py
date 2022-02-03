from cursor import device
from cursor import path
from cursor import renderer
from cursor import data
from numpy import random

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def debug():
    sns.distplot(random.normal(loc=0, scale=10, size=(10000, 2)))

    plt.show()

def normal():
    v = random.normal(loc=0, scale=100, size=(10000, 2))
    return v


def noncentral_chisquare():
    plt.figure()
    values = plt.hist(
        np.random.noncentral_chisquare(100, 2, 40), bins=1000, density=True
    )
    plt.show()
    return values


def make_one():
    pc = path.PathCollection()

    # x = random.normal(loc=1, scale=2, size=(10000, 2))

    #x1 = noncentral_chisquare()
    x1 = normal()
    c = 0
    for pos in x1:
        p = path.Path()
        p.add(pos[0], c)
        p.add(pos[0] + 50.5, c)
        pc.add(p)

        c += 1
    return pc


def g21_10k():
    pc = path.PathCollection()
    for i in range(2):
        pc1 = make_one()
        pc1.translate(i * 0.54, i)
        pc = pc + pc1
        # pc3 = pc1 + pc2

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A,
        device.PaperSize.PORTRAIT_A3,
        25,
        "genuary22",
        "second_day_normal_long_two",
    )


if __name__ == "__main__":
    # debug()
    # noncentral_chisquare()
    g21_10k()
