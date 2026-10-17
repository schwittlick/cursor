from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.tools.serial_powertools.seriallib import resume_point, state_before

FILE = "IN;AP11;SP1;VS20;FS8;PA0,0;PD;PA10,0;PU;PA0,5;PD;PA10,5;PU;LT2;PA0,9;PD;PA10,9;PU;PA0,0;SP0;"


def test_state_before_replays_modes_in_file_order():
    commands = tokenizer(FILE)

    assert state_before(commands, commands.index("LT2") + 1) == ["IN", "AP11", "SP1", "VS20", "FS8", "LT2"]


def test_state_before_keeps_only_the_latest_value():
    commands = tokenizer("IN;SP1;VS20;PA0,0;VS40;PD;PA1,1;PU;")

    assert state_before(commands, len(commands)) == ["IN", "SP1", "VS40"]


def test_state_before_starts_at_the_last_in():
    commands = tokenizer("SP3;VS5;IN;SP1;PA0,0;PD;PA1,1;PU;")

    assert state_before(commands, len(commands)) == ["IN", "SP1"]


def test_state_before_without_in_collects_from_the_start():
    commands = tokenizer("SP2;VS10;PA0,0;PD;PA1,1;PU;")

    assert state_before(commands, 4) == ["SP2", "VS10"]


def test_resume_point_moves_to_the_next_pen_up():
    commands = tokenizer(FILE)
    mid_path = commands.index("PD")

    assert resume_point(commands, mid_path) == commands.index("PU")
    assert resume_point(commands, commands.index("PU")) == commands.index("PU")
    assert resume_point(commands, len(commands) - 1) == len(commands) - 1
