from cursor.hpgl.tokenize import tokenize


def test_tokenize():
    string = 'SP1;SI1.000,1.000;DI0.839,0.545;LBTDI1.000,0.000;SP3;LBAIN;PU0,0;SP4;SI1.000,1.000;DI0.839,' \
             '0.545;LBASP2;PA201,130;PD1201,1130;LB1234LB'

    expected_commands = ['SP1', 'SI1.000,1.000', 'DI0.839,0.545', 'LBT', 'DI1.000,0.000',
                         'SP3', 'LBA', 'IN', 'PU0,0', 'SP4', 'SI1.000,1.000', 'DI0.839,0.545',
                         'LBA', 'SP2', 'PA201,130', 'PD1201,1130', 'LB1234LB']
    commands = tokenize(string)
    assert expected_commands == commands
