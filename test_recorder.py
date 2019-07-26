import path
import pyautogui
import json


def test_pathcollection_serializable():
    size = pyautogui.Size(100, 100)
    coll = path.PathCollection(size)

    p = path.Path()
    p.add(0.3445657567, 0.19034956876, 0.1239348457)
    p.add(0.2947576458935, 10.12904785678, 1.20478)

    coll.add(p, size)

    print('1', coll)

    j = json.dumps(coll, cls=path.MyJsonEncoder)
    print('2', j)

    fname = 'data/test_recordings/testing.json'

    recs = {'mouse': [coll],
            'keys': []
            }

    with open(fname, 'w') as fp:
        dump = json.dumps(recs, cls=path.MyJsonEncoder)
        fp.write(dump)

    with open('data/test_recordings/testing.json') as json_file:
        json_string = json_file.readline()
        data = json.loads(json_string, cls=path.MyJsonDecoder)
        ob = data

    #ob = json.loads(j, cls=path.MyJsonDecoder)
    #print('4', ob)

    print(ob)

    # todo: test more thorougly
    assert ob == recs['mouse']