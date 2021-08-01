pub mod cursor {
    use serde::{Deserialize, Serialize};
    use std::fmt;

    use crate::helpers::help;
    use crate::path::cursor;

    use chrono::{DateTime, Utc};
    use std::time::SystemTime;
    #[derive(Serialize, Deserialize, Debug)]
    pub struct TimedPoint {
        pub x: f64,
        pub y: f64,
        pub ts: i64,
    }

    static mut RESOLUTION: (u16, u16) = (0, 0); //help::get_resolution().unwrap();
                                                // how to init this from a non-static function?
                                                // how to make a static function?
    impl TimedPoint {
        pub fn new(x: f64, y: f64, ts: i64) -> TimedPoint {
            unsafe {
                if RESOLUTION.0 == 0 || RESOLUTION.1 == 0 {
                    RESOLUTION = match help::get_resolution() {
                        Ok(res) => res,
                        Err(err) => {
                            println!("Couldnt get resolution: {:?}", err);
                            std::process::exit(0);
                        }
                    };
                }
            }
            TimedPoint { x: x, y: y, ts: ts }
        }

        pub fn now() -> TimedPoint {
            let (x, y) = help::get_mouse_pos();
            //println!("{:?}x{:?}", x, y);

            let now = SystemTime::now();
            let now: DateTime<Utc> = now.into();
            unsafe {
                cursor::TimedPoint::new(
                    x as f64 / RESOLUTION.0 as f64,
                    y as f64 / RESOLUTION.1 as f64,
                    now.timestamp(),
                )
            }
        }

        pub fn same_pos(&self, other: &TimedPoint) -> bool {
            self.x == other.x && self.y == other.y
        }
    }

    impl fmt::Display for TimedPoint {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            write!(f, "({}, {}, {})", self.x, self.y, self.ts)
        }
    }

    impl PartialEq for TimedPoint {
        fn eq(&self, other: &Self) -> bool {
            self.x == other.x && self.y == other.y && self.ts == other.ts
        }
    }
    #[derive(Serialize, Deserialize, Debug)]
    pub struct PathCollection {
        pub paths: Vec<TimedPoint>,
    }

    impl PathCollection {
        pub fn new() -> PathCollection {
            PathCollection { paths: Vec::new() }
        }
        pub fn size(&self) -> usize {
            self.paths.len()
        }
        pub fn last(&self) -> std::option::Option<&TimedPoint> {
            self.paths.last()
        }
        pub fn add(&mut self, p: TimedPoint) {
            self.paths.push(p);
        }
        pub fn iter(&self) -> std::slice::Iter<TimedPoint> {
            self.paths.iter()
        }
    }
}
