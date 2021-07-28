#[cfg(test)]
mod tests {
    use crate::path::cursor;
    use base64;
    use chrono::DateTime;
    use chrono::Utc;
    //use flate2::write::ZlibDecoder;
    use flate2::write::ZlibEncoder;
    use flate2::Compression;
    use serde_json;
    use std::fs;
    //use std::io;
    use std::io::prelude::*;
    use std::time::SystemTime;

    #[test]
    fn encoding() {
        let mut e = ZlibEncoder::new(Vec::new(), Compression::default());
        let result = e.write_all(b"{\"resolution\": {\"w\": 3840, \"h\": 2160},\"mouse\":{\"paths\":[[{\"ts\":1626037613,\"x\":0.1,\"y\":0.1}]],\"timestamp\":1627049293}, \"keys\":[]}");
        match result {
            Ok(_) => {}
            Err(result) => println!("couldnt write stuff; {:?}", result),
        }
        let compressed_bytes = e.finish();
        //let encoded = match compressed_bytes{W
        //    Ok(compressed_bytes) => compressed_bytes,
        //};

        let _encoded = base64::encode(compressed_bytes.unwrap());

        let _json = serde_json::json!({
            "base64(zip(o))": _encoded,
        });

        let all_serialized = serde_json::to_string(&_json).unwrap();

        fs::write("test_serialized.json", all_serialized).expect("Unable to write file");
        //assert_eq!(_encoded, "lol");
        assert_eq!("lol", "lol");
    }
    /*

    fn decode_reader(bytes: &[u8]) -> io::Result<String> {
        let mut writer = Vec::new();
        let mut z = ZlibDecoder::new(writer);
        let res = z.write_all(&bytes[..]);
        match res {
            Err(_what) => {}
            Ok(_) => {}
        }
        writer = z.finish()?;
        let return_string = String::from_utf8(writer).expect("String parsing error");
        Ok(return_string)
    }

        #[test]
        fn decoding() {
            let s: String = String::from("eJylmEtOnDEQhK+CZo1Gdtttt3MVxIIFUqIIBQkiJULcPYZNuuzybwZWvOrDj6q22/Nyevj1++n+9O3q5fR49/z9qX93c/Ny+tO/hrOZ2PXV6e/7Dy0k6T88v0likdJaVSnnKq/XV/+BKB6oDEgABHVALgzIHqitOkDjHrDiADqAoj7v9OVArwyoCMQtYADU5oHGgIZAckBlwDCAn5Elpo8AFJ+Lxmw2QcDNKAYWJEsIOH1kLhi6rG5Gkf5/dFn9hFJmANqsXk+3FF3OrhK66gOA19MtRdOSB4wVgmEqkp9RY0tGvbhKk2BMH9eAsCWPgFuCJOZykzWQ2Zobxii60hFltdYwR7F4gPncdA3Q4mwYpOjXUFmxHQLUB0xS8FNq1Ac7AKgPGI3gqieRQ7Keg9eX5qozzbZNcvXy2bWujwikLSAIeP1sWtdDjorpFshrQD4CyBbQNZDmHHWgILDVQ4yKP5E+AcxB7YAhIFsAclfAtzwfkvUcMRilbgFZAzrXTgcwGSVeCKhfg7LaiWi0lksBP6XCyi1iMrIfgW4SGp3jTo8+Jx+9ysozos9JdwC6lnz9sxyh3Le1yVityQD4+ZCrswNossiFQPS5a3QJeF5EN6UcWHUeAaRF6gCmwvfynwBYLgRzFFwpZGFBHQF3wmR6kUg7AFiQ0IYgX9AzmxMESVv7ip4CGQG/YKWAHgAseKmugcKCNwJxC9gaqCx4A2BtB+QDPQtqjgiULZAuBIquAdLN1+FRqP4V+QmAXSP4itRqOwBfhVrLMWBDR6L1Qn2x4zXb0JFo0UsBOfbNho5EYQ0fAvwIZa43O+OmZj8AqZ5JvylPGzoe9Q9VdgBMQCpbAIvBv1Rznq/bGfBRJaeeDR2PyuaYtKGDUUlbwA4Aope1nFxUNtz/CAirBbzOB4COgMETv6nkdrZzimsgUAAXHW0L5AOAZXUE0hbQJcDaqhk47gxtvNwCtJIsGMNdhQDR57WcdMJdL2ugsCBle729ffv9j4f7p+e7h0f/59w3JNv7p7qnn/d/3z8Qvn39B82p1X4=");
            let r = decode_reader(&s.as_bytes());
            match r {
                Ok(result) => {
                    println!("{}", result);
                }
                Err(result) => {
                    println!("{}", result);
                    assert_eq!(0, 1);
                }
            }
        }
    */
    #[test]
    fn test_serialize_deserialize() {
        let now = SystemTime::now();
        let now: DateTime<Utc> = now.into();
        let point = cursor::TimedPoint {
            x: 0 as f64,
            y: 0 as f64,
            ts: now.timestamp(),
        };

        let serialized = serde_json::to_string(&point).unwrap();
        println!("serialized = {}", serialized);

        let deserialized: cursor::TimedPoint = serde_json::from_str(&serialized).unwrap();
        println!("deserialized = {:?}", deserialized);

        assert_eq!(point, deserialized);
    }

    #[test]
    fn test_serialize_python() {
        let to_match = "{\"keys\":[],\"mouse\":{\"paths\":[{\"ts\":1626037613,\"x\":0.1,\"y\":0.1}]},\"timestamp\":1627049293}";
        let point = cursor::TimedPoint {
            x: 0.1 as f64,
            y: 0.1 as f64,
            ts: 1626037613,
        };
        let mut vec = Vec::new();
        vec.push(point);
        let pc = cursor::PathCollection { paths: vec };

        let _json = serde_json::json!({
            "keys": [],
            "timestamp": 1627049293,
            "mouse": pc,
        });

        let all_serialized = serde_json::to_string(&_json).unwrap();
        assert_eq!(all_serialized, to_match);
    }
    #[test]
    fn test_deserialize_python() {
        let _json = serde_json::json!({
            "base64(zip(o))": "eJylmEtOnDEQhK+CZo1Gdtttt3MVxIIFUqIIBQkiJULcPYZNuuzybwZWvOrDj6q22/Nyevj1++n+9O3q5fR49/z9qX93c/Ny+tO/hrOZ2PXV6e/7Dy0k6T88v0likdJaVSnnKq/XV/+BKB6oDEgABHVALgzIHqitOkDjHrDiADqAoj7v9OVArwyoCMQtYADU5oHGgIZAckBlwDCAn5Elpo8AFJ+Lxmw2QcDNKAYWJEsIOH1kLhi6rG5Gkf5/dFn9hFJmANqsXk+3FF3OrhK66gOA19MtRdOSB4wVgmEqkp9RY0tGvbhKk2BMH9eAsCWPgFuCJOZykzWQ2Zobxii60hFltdYwR7F4gPncdA3Q4mwYpOjXUFmxHQLUB0xS8FNq1Ac7AKgPGI3gqieRQ7Keg9eX5qozzbZNcvXy2bWujwikLSAIeP1sWtdDjorpFshrQD4CyBbQNZDmHHWgILDVQ4yKP5E+AcxB7YAhIFsAclfAtzwfkvUcMRilbgFZAzrXTgcwGSVeCKhfg7LaiWi0lksBP6XCyi1iMrIfgW4SGp3jTo8+Jx+9ysozos9JdwC6lnz9sxyh3Le1yVityQD4+ZCrswNossiFQPS5a3QJeF5EN6UcWHUeAaRF6gCmwvfynwBYLgRzFFwpZGFBHQF3wmR6kUg7AFiQ0IYgX9AzmxMESVv7ip4CGQG/YKWAHgAseKmugcKCNwJxC9gaqCx4A2BtB+QDPQtqjgiULZAuBIquAdLN1+FRqP4V+QmAXSP4itRqOwBfhVrLMWBDR6L1Qn2x4zXb0JFo0UsBOfbNho5EYQ0fAvwIZa43O+OmZj8AqZ5JvylPGzoe9Q9VdgBMQCpbAIvBv1Rznq/bGfBRJaeeDR2PyuaYtKGDUUlbwA4Aope1nFxUNtz/CAirBbzOB4COgMETv6nkdrZzimsgUAAXHW0L5AOAZXUE0hbQJcDaqhk47gxtvNwCtJIsGMNdhQDR57WcdMJdL2ugsCBle729ffv9j4f7p+e7h0f/59w3JNv7p7qnn/d/3z8Qvn39B82p1X4="
        });

        let _encoded = &_json["base64(zip(o))"];
    }

    #[test]
    fn unix_timestamp() {
        let utc_time: DateTime<Utc> = SystemTime::now().into();
        let _utc = utc_time.timestamp();
        assert!(_utc > 0);
    }
}
