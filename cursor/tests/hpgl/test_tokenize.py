from cursor.hpgl.tokenize import tokenizer


def test_tokenize():
    string = 'SP1;SI1.000,1.000;DI0.839,0.545;LBTDI1.000,0.000;SP3;LBAIN;PU0,0;SP4;SI1.000,1.000;DI0.839,' \
             '0.545;LBASP2;PA201,130;PD1201,1130;LB1234LB'

    expected_commands = ['SP1', 'SI1.000,1.000', 'DI0.839,0.545', 'LBT', 'DI1.000,0.000',
                         'SP3', 'LBA', 'IN', 'PU0,0', 'SP4', 'SI1.000,1.000', 'DI0.839,0.545',
                         'LBA', 'SP2', 'PA201,130', 'PD1201,1130', 'LB1234LB']
    commands = tokenizer(string)
    assert expected_commands == commands


def test_tokenize2():
    string = "IN;VS100;ES-0.330,-1.000;DI0.000,1.000;SI0.096,0.138;SP1;PA57,0;SP1;LBINPA57,77;SP1;" \
             "LBIW0,0,15490,10870PA57,739;SP1;LBVS100PA57,934;SP1;LBES-0.330,-1.000PA57,1518;SP1;" \
             "LBDI0.000,1.000PA57,2024;SP1;LBSI0.115,0.163PA57,2998;SP1;LBLBINPA57,3543;SP1;" \
             "LBLBIW0,0,15490,10870PA57,4711;SP1;LBLBVS100PA57,5451;SP1;LBLBES-0.330,-1.000PA57,6580;" \
             "SP1;LBLBDI0.000,1.000PA57,7632;SP1;LBLBSI0.120,0.171PA57,8683;SP1;" \
             "LBLBLBPhotography intersects several areas of responsibility"

    expected_commands = ['IN']
    commands = tokenizer(string)
    assert expected_commands == commands
