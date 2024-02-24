from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def test_hpgl_parser_PAPD():
    paths = HPGLParser().parse("IN;SP1;PA100,0;PD100,100;PU;PA0,0;")

    path = Path.from_tuple_list([(100, 0.0), (100, 100.0)])
    path.pen_select = 1

    collection = Collection.from_path_list([path])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_LB():
    paths = HPGLParser().parse("IN;SP1;LBHI")

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(0.0, 150.0), Position(0.0, 0.0)], properties)
    path2 = Path([Position(114.0, 150.0), Position(114.0, 0.0)], properties)
    path3 = Path([Position(0.0, 79.6875), Position(114.0, 79.6875)], properties)
    path4 = Path([Position(185.25, 150.0), Position(270.75, 150.0)], properties)
    path5 = Path([Position(228.0, 150.0), Position(228.0, 0.0)], properties)
    path6 = Path([Position(185.25, 0.0), Position(270.75, 0.0)], properties)
    collection = Collection.from_path_list([path1, path2, path3, path4, path5, path6])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_DI():
    paths = HPGLParser().parse("IN;SP1;DI0,1;PA100,0;PD100,100;")

    path = Path.from_tuple_list([(100, 0.0), (100, 100.0)])
    path.pen_select = 1
    collection = Collection()
    collection.add(path)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string():
    parser = HPGLParser()
    paths = parser.parse("IN;SP1;SI1,1;PA100,0;LB1")

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(200.0, 0.0), Position(450.0, 0.0)], properties)
    path2 = Path([Position(200.0, 250.0), Position(350.0, 400.0), Position(350.0, 0.0)], properties)
    collection = Collection.from_path_list([path1, path2])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string2():
    string = 'SP1;SI1.000,1.000;DI0.839,0.545;LBTDI1.000,0.000;SP3;LBAIN;PU0,0;SP4;SI1.000,1.000;DI0.839,' \
             '0.545;LBASP2;PA201,130;PD1201,1130;'
    parser = HPGLParser()
    paths = parser.parse(string)

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(-217.8970, 335.4414), Position(117.5444, 553.3383)], properties)
    path2 = Path([Position(-50.1763, 444.3899), Position(167.7207, 108.9485)], properties)
    path3 = Path([Position(477.8017, 362.9126), Position(677.8017, 762.9126), Position(877.8017, 362.9126)],
                 {Property.PEN_SELECT: 3, "label": 3})
    path4 = Path([Position(527.8017, 462.9126), Position(827.8017, 462.9126)], {Property.PEN_SELECT: 3, "label": 3})
    path5 = Path([Position(0.0, 0.0), Position(-50.1763, 444.3899), Position(335.4414, 217.8970)],
                 {Property.PEN_SELECT: 4, "label": 4})
    path6 = Path([Position(-12.5441, 111.0975), Position(239.0370, 274.5202)], {Property.PEN_SELECT: 4, "label": 4})
    path7 = Path([Position(201.0, 130.0), Position(1201.0, 1130.0)], {Property.PEN_SELECT: 2})

    collection = Collection.from_path_list([path1, path2, path3, path4, path5, path6, path7])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_PA():
    file = DataDirHandler().test_data_file("hpgl_pa_pd_pu.hpgl")
    parser = HPGLParser()
    paths = parser.parse(file)

    path = Path.from_tuple_list([(100, 0), (100, 100)])
    path.pen_select = 1

    collection = Collection()
    collection.add(path)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]
