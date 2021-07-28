pub mod cursor {
    use serde::{Deserialize, Serialize};
    use std::fmt;
    #[derive(Serialize, Deserialize, Debug)]
    pub struct TimedPoint {
        pub x: f64,
        pub y: f64,
        pub ts: i64,
    }

    impl TimedPoint {
        pub fn new(x: f64, y: f64, ts: i64) -> TimedPoint {
            TimedPoint { x: x, y: y, ts: ts }
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
}
