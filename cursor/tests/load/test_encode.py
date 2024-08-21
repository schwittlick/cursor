from cursor.collection import Collection
from cursor.load.compress import JsonCompressor
from cursor.path import Path


def test_json_encoder():
    mouse_recordings = Collection()
    p1 = Path()
    p1.add(0, 0, 1626037613)
    mouse_recordings.add(p1)
    keyboard_recodings = []

    recs = {"mouse": mouse_recordings, "keys": keyboard_recodings}
    compressor = JsonCompressor()
    enc = compressor.json_zip(j=recs)
    assert 124 <= len(enc["base64(zip(o))"]) <= 142
