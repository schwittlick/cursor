class DrawingMachine:
    def __init__(self):
        pass

    class Paper:
        X_FACTOR = 2.91666
        Y_FACTOR = 2.83333

        CUSTOM_36_48 = (360 * X_FACTOR, 480 * Y_FACTOR)
        CUSTOM_48_36 = (480 * X_FACTOR, 360 * Y_FACTOR)
        DIN_A1_LANDSCAPE = (841 * X_FACTOR, 594 * Y_FACTOR)
        DIN_A0_LANDSCAPE = (1189 * X_FACTOR, 841 * Y_FACTOR)

        @staticmethod
        def custom_36_48_portrait():
            return DrawingMachine.Paper.CUSTOM_36_48

        @staticmethod
        def custom_36_48_landscape():
            return DrawingMachine.Paper.CUSTOM_48_36

        @staticmethod
        def a1_landscape():
            return DrawingMachine.Paper.DIN_A1_LANDSCAPE

        @staticmethod
        def a0_landscape():
            return DrawingMachine.Paper.DIN_A0_LANDSCAPE
