from bitmap_approximator.fridge_style import create_fridge
from simple_style import main_approximation
from device import PlotterType
from grid_style import create_grid

plotter = PlotterType.HP_DM_RX_PLUS_A1

if __name__ == '__main__':
    main_approximation()
    # create_grid(plotter)
    #create_fridge(plotter)
