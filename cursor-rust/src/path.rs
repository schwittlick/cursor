pub mod cursor {
    use chrono::{DateTime, Utc};
    use std::fmt;

    pub struct TimedPoint {
        pub x: f64,
        pub y: f64,
        pub time: DateTime<Utc>,
    }

    impl fmt::Display for TimedPoint {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            // let string = format!("({x.*}, {}, {})", 3, x=self.x, y=self.y, time=self.time.to_rfc3339());
            write!(f, "({}, {}, {})", self.x, self.y, self.time.to_rfc3339())
        }
    }
}
