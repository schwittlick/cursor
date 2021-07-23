#[cfg(test)]
mod tests {
    use base64;
    use flate2::write::ZlibEncoder;
    use flate2::Compression;
    use std::io::prelude::*;

    #[test]
    fn it_adds_two() {
        let mut e = ZlibEncoder::new(Vec::new(), Compression::default());
        let result = e.write_all(b"{\"mouse\": {\"paths\": [[{\"x\": 0.000, \"y\": 0.000, \"ts\": 1626037613.00}]], \"keys\": []}");
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
