# hello!

this is the mouse recorder implemented in rust

there's lots of platform specific things to handle

. mouse pos
. screen size
. tray icon
. SIGINT handling

developed on windows 10

#  recording spec



timestamp_compressed.json
base64 encoded objects of tuples (x, y, t)
format: {'base64(zip(o))': 'eJy...dRfus7'}

how to

python recode func (data.py:80):

    decoded = base64.b64decode(j[self.ZIPJSON_KEY])
    decompressed = zlib.decompress(decoded)

# rust secrets

    $env:RUST_BACKTRACE=1; cargo run