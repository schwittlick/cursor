from cursor.recorder import Recorder
from pynput.keyboard import KeyCode


def test_recorder1():
    recorder = Recorder()
    recorder.on_move(0, 0)
    recorder.on_move(1, 0)
    recorder.on_move(0, 5000)

    recorded_paths = len(recorder._mouse_recordings)
    assert recorded_paths == 0
    assert len(recorder._current_line) == 3
    assert len(recorder._keyboard_recodings) == 0

    k = KeyCode(char="k")
    recorder.on_release(k)
    assert len(recorder._keyboard_recodings) == 1
    assert recorder._keyboard_recodings[0][0] == "k"
