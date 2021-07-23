# hello!

this is the mouse recorder implemented in rust

there's lots of platform specific things to handle

* mouse pos
* screen size
* tray icon
* SIGINT handling

developed on windows 10

#  recording spec



timestamp_compressed.json
base64 encoded objects of tuples (x, y, t)
format: {'base64(zip(o))': 'eJy...dRfus7'}

how to

python recode func (data.py:56):

    dumped = json.dumps(j, cls=MyJsonEncoder)
    dumped_encoded = dumped.encode("utf-8")
    compressed = zlib.compress(dumped_encoded)
    encoded = {self.ZIPJSON_KEY: base64.b64encode(compressed).decode("ascii")}


sample data
3 paths, length=(5, 6, 4)
dumped_encoded=

    b'{"mouse": {"paths": [[{"x": 0.8638, "y": 0.8694, "ts": 1626996998.83}, {"x": 0.8638, "y": 0.8685, "ts": 1626996998.84}, {"x": 0.8638, "y": 0.8681, "ts": 1626996998.85}, {"x": 0.8638, "y": 0.8676, "ts": 1626996998.87}, {"x": 0.8638, "y": 0.8671, "ts": 1626996998.9}], [{"x": 0.8589, "y": 0.9444, "ts": 1626996999.33}, {"x": 0.8583, "y": 0.9454, "ts": 1626996999.34}, {"x": 0.8581, "y": 0.9458, "ts": 1626996999.34}, {"x": 0.8578, "y": 0.9463, "ts": 1626996999.36}, {"x": 0.8576, "y": 0.9463, "ts": 1626996999.38}, {"x": 0.8576, "y": 0.9472, "ts": 1626996999.38}], [{"x": 0.8482, "y": 0.937, "ts": 1626996999.97}, {"x": 0.8477, "y": 0.937, "ts": 1626996999.98}, {"x": 0.8477, "y": 0.9366, "ts": 1626997000.0}, {"x": 0.8474, "y": 0.9366, "ts": 1626997000.01}]], "timestamp": 1626996990.504024}, "keys": []}'

compressed=

    b'x\x9x\xa5 [...] \x95KN\x9'

encoded=

    {'base64(zip(o))': 'eJylmEtOnDEQhK+CZo1Gdtttt3MVxIIFUqIIBQkiJULcPYZNuuzybwZWvOrDj6q22/Nyevj1++n+9O3q5fR49/z9qX93c/Ny+tO/hrOZ2PXV6e/7Dy0k6T88v0likdJaVSnnKq/XV/+BKB6oDEgABHVALgzIHqitOkDjHrDiADqAoj7v9OVArwyoCMQtYADU5oHGgIZAckBlwDCAn5Elpo8AFJ+Lxmw2QcDNKAYWJEsIOH1kLhi6rG5Gkf5/dFn9hFJmANqsXk+3FF3OrhK66gOA19MtRdOSB4wVgmEqkp9RY0tGvbhKk2BMH9eAsCWPgFuCJOZykzWQ2Zobxii60hFltdYwR7F4gPncdA3Q4mwYpOjXUFmxHQLUB0xS8FNq1Ac7AKgPGI3gqieRQ7Keg9eX5qozzbZNcvXy2bWujwikLSAIeP1sWtdDjorpFshrQD4CyBbQNZDmHHWgILDVQ4yKP5E+AcxB7YAhIFsAclfAtzwfkvUcMRilbgFZAzrXTgcwGSVeCKhfg7LaiWi0lksBP6XCyi1iMrIfgW4SGp3jTo8+Jx+9ysozos9JdwC6lnz9sxyh3Le1yVityQD4+ZCrswNossiFQPS5a3QJeF5EN6UcWHUeAaRF6gCmwvfynwBYLgRzFFwpZGFBHQF3wmR6kUg7AFiQ0IYgX9AzmxMESVv7ip4CGQG/YKWAHgAseKmugcKCNwJxC9gaqCx4A2BtB+QDPQtqjgiULZAuBIquAdLN1+FRqP4V+QmAXSP4itRqOwBfhVrLMWBDR6L1Qn2x4zXb0JFo0UsBOfbNho5EYQ0fAvwIZa43O+OmZj8AqZ5JvylPGzoe9Q9VdgBMQCpbAIvBv1Rznq/bGfBRJaeeDR2PyuaYtKGDUUlbwA4Aope1nFxUNtz/CAirBbzOB4COgMETv6nkdrZzimsgUAAXHW0L5AOAZXUE0hbQJcDaqhk47gxtvNwCtJIsGMNdhQDR57WcdMJdL2ugsCBle729ffv9j4f7p+e7h0f/59w3JNv7p7qnn/d/3z8Qvn39B82p1X4='}

# rust secrets

    $env:RUST_BACKTRACE=1; cargo run