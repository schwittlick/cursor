from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path


def test_hpgl_parser_PAPD():
    paths = HPGLParser().parse("IN;SP1;PA100,0;PD100,100;PU;PA0,0;")

    collection = Collection()
    collection.add(Path.from_tuple_list([(100, 0.0), (100, 100.0)]))

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_LB():
    paths = HPGLParser().parse("IN;SP1;LBHI")

    tuples = [[(0.0, 150.0), (0.0, 0.0)],
              [(114.0, 150.0), (114.0, 0.0)],
              [(0.0, 79.6875), (114.0, 79.6875)],
              [(185.25, 150.0), (270.75, 150.0)],
              [(228.0, 150.0), (228.0, 0.0)],
              [(185.25, 0.0), (270.75, 0.0)]]
    collection = Collection.from_tuples(tuples)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_DI():
    paths = HPGLParser().parse("IN;SP1;DI0,1;PA100,0;PD100,100;")

    collection = Collection()
    collection.add(Path.from_tuple_list([(100, 0.0), (100, 100.0)]))

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string():
    parser = HPGLParser()
    paths = parser.parse("IN;SP1;SI1,1;PA100,0;LB1")

    tuples = [[(200.0, 0.0), (450.0, 0.0)], [(200.0, 250.0), (350.0, 400.0), (350.0, 0.0)]]
    collection = Collection.from_tuples(tuples)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string2():
    string = 'SP1;SI1.000,1.000;DI0.839,0.545;LBTDI1.000,0.000;SP3;LBAIN;PU0,0;SP4;SI1.000,1.000;DI0.839,' \
             '0.545;LBASP2;PA201,130;PD1201,1130;'
    parser = HPGLParser()
    paths = parser.parse(string)

    tuples = [[(-217.89695910175672, 335.44137373646583), (117.54441463470911, 553.3383328382225)],
              [(-50.176272233523804, 444.3898532873442), (167.72068686823292, 108.94847955087836)],
              [(477.8017144945594, 362.9125536903615), (677.8017144945594, 762.9125536903615),
               (877.8017144945594, 362.9125536903615)],
              [(527.8017144945594, 462.9125536903615), (827.8017144945594, 462.9125536903615)],
              [(0.0, 0.0), (-50.176272233523804, 444.3898532873442), (335.44137373646583, 217.89695910175672)],
              [(-12.544068058380951, 111.09746332183605), (239.03696224396845, 274.5201826481536)],
              [(201.0, 130.0), (1201.0, 1130.0)]]
    collection = Collection.from_tuples(tuples)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_PA():
    file = DataDirHandler().test_data_file("hpgl_pa_pd_pu.hpgl")
    parser = HPGLParser()
    paths = parser.parse(file)

    collection = Collection()
    collection.add(Path.from_tuple_list([(100, 0), (100, 100)]))

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]
