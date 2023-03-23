import queue
import socket
import threading
import time
import traceback

import wasabi

logger = wasabi.Printer(pretty=True, no_print=False)


class PlotterThread(threading.Thread):
    def __init__(self, thread_id, plotter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.running = True
        self.plotter = plotter
        self._speed = None
        self.c = None
        self.stopped = False

        self.buffer = queue.Queue()
        self.delays = queue.Queue()

        # arcade flat ui buttons
        self.button = None
        self.thread_count = None
        self.speed_label = None
        self.pen_label = None
        self.remaining_seconds = []
        self.remaining_seconds_label = None
        self.line_distance_label = None

        self.v1_label = None
        self.v2_label = None

        self.task_completed_cb = None

        self.max_buffer_size = 50

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, v):
        if self.speed_label:
            self.speed_label.text = str(int(v))
        self._speed = v

    def set_cb(self, cb):
        self.task_completed_cb = cb

    def clear(self):
        while self.buffer.qsize() > 0:
            logger.info(f"Removing a task from {self.plotter}")
            self.buffer.get()
            self.delays.get()
            self.update_thread_count_ui()

    def add(self, func):
        current_delay = self.plotter.get_delay()
        logger.info(
            f"Added {func.__name__} to {self.plotter.type} at {self.plotter.serial_port} with delay {current_delay}")

        if self.buffer.qsize() >= self.max_buffer_size:
            logger.warn(f"Discarding ...")
            return
        self.buffer.put(func)
        self.delays.put(current_delay)

        self.update_thread_count_ui()

    def update_thread_count_ui(self):
        s = self.buffer.qsize()
        self.thread_count.text = "↔️ " + str(s)

    def run(self):
        logger.info(f"Thread for {self.plotter.type} at {self.plotter.serial_port} started")
        while True:
            if self.stopped:
                return

            if not self.running:
                time.sleep(0.1)
                continue
            else:
                if not self.buffer.empty():
                    func = self.buffer.get()
                    delay = self.delays.get()

                    self.update_thread_count_ui()
                    time.sleep(delay)

                    if not self.plotter.serial_port:
                        if self.task_completed_cb:
                            # TODO: callback
                            self.task_completed_cb()
                        continue

                    try:

                        # run
                        func(self.c, self.speed)

                        if self.task_completed_cb:
                            self.task_completed_cb()

                    except socket.timeout as e:
                        logger.fail(f"{self.plotter.type} at {self.plotter} timed out")
                    except Exception as e:
                        logger.fail(f"Scheduled call failed: {e}")
                        logger.fail(f"{traceback.format_exc()}")
                else:
                    time.sleep(0.01)
                    continue

        logger.info(f"Thread for {self.plotter.type} at {self.plotter.serial_port} finished")

    def stop(self):
        self.stopped = True

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True


class CheckerThread(threading.Thread):
    def __init__(self, plotters):
        threading.Thread.__init__(self)
        self.plotters = plotters
        self.running = True

    def run(self):
        while True:
            if not self.running:
                logger.info("Checker thread finished")
                return

            time.sleep(1)
            threads = {}
            for plo in self.plotters:
                threads[plo.serial_port] = plo

            dict_copy = threads.copy()
            for port, plo in dict_copy.items():
                if not plo.thread:
                    continue
                if not plo.thread.running:
                    plo.thread.pause()
                elif not plo.thread.is_alive():
                    plo.thread = None
                else:
                    # Resume the thread if it was paused
                    plo.thread.resume()

    def stop(self):
        self.running = False
