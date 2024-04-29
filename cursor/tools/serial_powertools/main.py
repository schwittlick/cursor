import logging

import dearpygui.dearpygui as dpg

from cursor.tools.serial_powertools.gui import create_file_dialogue, create_plotter_inspector_gui, file_selected, \
    print_output, add_output_window, create_send_file_gui, create_bruteforce_gui, add_plotter_info_window
from cursor.tools.serial_powertools.serial_inspector import SerialInspector

if __name__ == '__main__':
    """
    This is where everything is glued together
    """

    # serial inspector handles all the connections
    inspector = SerialInspector()

    # creating gui elements
    dpg.create_context()

    create_file_dialogue(file_selected)

    create_plotter_inspector_gui(inspector)
    create_send_file_gui(inspector)
    create_bruteforce_gui(inspector)
    add_plotter_info_window(inspector)

    add_output_window()

    # exit on ESC
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_Escape, callback=dpg.stop_dearpygui)


    # making sure all internal logging messages arrive in the gui
    def on_log(record):
        print_output(record.getMessage())
        return True


    logging.root.addFilter(on_log)

    dpg.create_viewport(title='Serial Inspector', width=1550, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
