from cursor.hpgl import ESC_TERM, ESC


class MemoryConfig:
    pass


class DraftMasterMemoryConfig(MemoryConfig):
    def __init__(self):
        self.physical_io_buffer = 2, 25518
        self.polygon_buffer = 4, 25520
        self.char_buffer = 0, 25516
        self.vector_buffer = 66, 25582
        self.pen_sort_buffer = 12, 24528

        self.max_sum = 25600

    def memory_alloc_cmd(self, io: int = 1024, polygon: int = 3072, char: int = 0, vector: int = 3000,
                         pen_sort: int = 18504) -> tuple[str, str]:
        assert self.physical_io_buffer[0] <= io <= self.physical_io_buffer[1]
        assert self.polygon_buffer[0] <= polygon <= self.polygon_buffer[1]
        assert self.char_buffer[0] <= char <= self.char_buffer[1]
        assert self.vector_buffer[0] <= vector <= self.vector_buffer[1]
        assert self.pen_sort_buffer[0] <= pen_sort <= self.pen_sort_buffer[1]
        assert sum([io, polygon, char, vector, pen_sort]) <= self.max_sum

        memory_config = f"{ESC}.T{io};{polygon};{char};{vector};{pen_sort}{ESC_TERM}"

        io_conditions = 3
        # io_conditions specifies an integer equivalent value that controls the states of bits 0 through 4
        # of the configuration byte. When using an RS-232-C interface, these bits control hardware handshake,
        # communications protocol, monitor modes 1 and 2, and block I/O error checking. When using HP-IB
        # interface, this parameter is ignored.
        # Check chapter 15-28 Device-Control Instructions of HP Draftmaster Programmers Reference
        plotter_config = f"{ESC}.@{io};{io_conditions}{ESC_TERM}"

        return memory_config, plotter_config


class HP7550AMemoryConfig(MemoryConfig):
    def __init__(self):
        self.physical_io_buffer = 2, 12752
        self.polygon_buffer = 4, 12754
        self.char_buffer = 0, 12750
        self.replot_buffer = 0, 12750
        self.vector_buffer = 44, 12794

        self.max_sum = 12800

    def memory_alloc_cmd(self, io: int = 1024, polygon: int = 1778, char: int = 0, replot: int = 9954,
                         vector: int = 44) -> tuple[str, str]:
        assert self.physical_io_buffer[0] <= io <= self.physical_io_buffer[1]
        assert self.polygon_buffer[0] <= polygon <= self.polygon_buffer[1]
        assert self.char_buffer[0] <= char <= self.char_buffer[1]
        assert self.replot_buffer[0] <= replot <= self.replot_buffer[1]
        assert self.vector_buffer[0] <= vector <= self.vector_buffer[1]
        assert sum([io, polygon, char, replot, vector]) <= self.max_sum

        buffer_sizes = f"{ESC}.T{io};{polygon};{char};{replot};{vector}{ESC_TERM}"
        logical_buffer_size = f"{ESC}.@{io}{ESC_TERM}"

        return buffer_sizes, logical_buffer_size
