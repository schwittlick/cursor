#[cfg(test)]
mod tests {
    use base64;
    use flate2::write::ZlibEncoder;
    use flate2::Compression;
    use std::io::prelude::*;

    #[test]
    fn it_adds_two() {
        let mut e = ZlibEncoder::new(Vec::new(), Compression::default());
        e.write_all(b"{\"mouse\": {\"paths\": [[{\"x\": 0.8638, \"y\": 0.8694, \"ts\": 1626996998.83}], [{\"x\": 0.8589, \"y\": 0.9444, \"ts\": 1626996999.33}], [{\"x\": 0.8482, \"y\": 0.937, \"ts\": 1626996999.97}]], \"timestamp\": 1626996990.504024}, \"keys\": []}");
        let compressed_bytes = e.finish();
        //let encoded = match compressed_bytes{
        //    Ok(compressed_bytes) => compressed_bytes,
        //};

        let encoded = base64::encode(compressed_bytes.unwrap());
        assert_eq!(encoded, "lol");
    }
}
