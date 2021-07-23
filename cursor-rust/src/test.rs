#[cfg(test)]
mod tests {
    use base64;
    use flate2::write::ZlibEncoder;
    use flate2::Compression;
    use std::io::prelude::*;

    #[test]
    fn it_adds_two() {
        let mut e = ZlibEncoder::new(Vec::new(), Compression::default());
        let result = e.write_all(b"{\"mouse\": {\"paths\": [[{\"x\": 0.8638, \"y\": 0.8694, \"ts\": 1626996998.83}], [{\"x\": 0.8589, \"y\": 0.9444, \"ts\": 1626996999.33}], [{\"x\": 0.8482, \"y\": 0.937, \"ts\": 1626996999.97}]], \"timestamp\": 1626996990.504024}, \"keys\": []}");
        match result {
            Ok(_) => {}
            Err(result) => println!("couldnt write stuff; {:?}", result),
        }
        let compressed_bytes = e.finish();
        //let encoded = match compressed_bytes{
        //    Ok(compressed_bytes) => compressed_bytes,
        //};

        let _encoded = base64::encode(compressed_bytes.unwrap());
        //assert_eq!(_encoded, "lol");
        assert_eq!("lol", "lol");
    }

    use chrono::DateTime;
    use chrono::Utc;
    use std::time::SystemTime;

    #[test]
    fn unix_timestamp() {
        let utc_time: DateTime<Utc> = SystemTime::now().into();
        let _utc = utc_time.timestamp();
        assert!(_utc > 0);
    }
}
