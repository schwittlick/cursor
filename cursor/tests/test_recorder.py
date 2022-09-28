import pynput
import pytest

from cursor.recorder import Recorder


@pytest.disable()
def test_recorder1():
    recorder = Recorder("suffix")
    recorder.on_move(0, 0)
    recorder.on_move(1, 0)
    recorder.on_move(0, 5000)

    recorded_paths = len(recorder._mouse_recordings)
    assert recorded_paths == 0
    assert len(recorder._current_line) == 3
    assert len(recorder._keyboard_recodings) == 0

    k = pynput.keyboard.KeyCode(char="k")
    recorder.on_release(k)
    assert len(recorder._keyboard_recodings) == 1
    assert recorder._keyboard_recodings[0][0] == "k"
    assert recorder._keyboard_recodings[0][2] == 0

    space = pynput.keyboard.KeyCode(char=" ")
    recorder.on_release(space)
    assert len(recorder._keyboard_recodings) == 2
    assert recorder._keyboard_recodings[1][0] == " "
    assert recorder._keyboard_recodings[1][2] == 0

    recorder.on_press(pynput.keyboard.Key.alt)
    assert len(recorder._keyboard_recodings) == 3
    assert recorder._keyboard_recodings[2][0] == "ALT"
    assert recorder._keyboard_recodings[2][2] == 1

    # test that pause is not added to the key list
    # the size doesnt change even though a key is pressed
    recorder.on_press(pynput.keyboard.Key.pause)
    assert len(recorder._keyboard_recodings) == 3

    recorder.stop()
