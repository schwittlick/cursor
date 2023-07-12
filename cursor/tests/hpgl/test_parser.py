from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path


def test_hpgl_parser_LB():
    file = DataDirHandler().test_data_file("file_to_parse.hpgl")
    parser = HPGLParser()
    paths = parser.parse(file)

    collection = Collection()
    collection.add(Path.from_tuple_list([(100.25, 0.0), (100.875, 0.0)]))
    collection.add(Path.from_tuple_list([(100.25, 0.625), (100.625, 1.0), (100.625, 0.0)]))

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string():
    parser = HPGLParser()
    paths = parser.parse("IN;SP1;SI1,1;PA100,0;LB1")

    collection = Collection()
    collection.add(Path.from_tuple_list([(100.25, 0.0), (100.875, 0.0)]))
    collection.add(Path.from_tuple_list([(100.25, 0.625), (100.625, 1.0), (100.625, 0.0)]))

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string2():
    string = 'SP1;SI1.000,1.000;DI0.839,0.545;LBTest\x03DI1.000,0.000;SP3;LBAB\x03IN;PU0,0;SP4;SI1.000,1.000;DI0.839,0.545;LBTestA\x03SP2;PA201,130;PD1201,1130;'
    parser = HPGLParser()
    paths = parser.parse(string)

    collection = Collection()
    collection.add(Path.from_tuple_list([(100.25, 0.0), (100.875, 0.0)]))
    collection.add(Path.from_tuple_list([(100.25, 0.625), (100.625, 1.0), (100.625, 0.0)]))

    assert len(paths) == 21

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
