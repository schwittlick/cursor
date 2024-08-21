from cursor.load.compress import JsonCompressor


def test_json_decoder():
    enc = "{'base64(zip(o))': 'eJyrVsrNLy1OVbJSqFYqSCzJKAayoqOrlSqAtIGOglIllC4BSR \
     iaGZkZGJubGRrXxsaCBDNzU4tLEnMLIHLmBiYWpuYGeoYGphYWRrVABdmplWADY2sB4yQcFQ=='}"
    compressor = JsonCompressor()
    res = compressor.json_unzip(eval(enc))
    assert len(res["mouse"]) == 1
    assert len(res["keys"]) == 0
