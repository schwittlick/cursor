mod helpers;
mod path;
mod test;

use crate::helpers::help;
use crate::path::cursor;

use chrono::{DateTime, Utc};
use rdev;
use rdev::display_size;
use std::io;
use std::thread;
use std::time::{Duration, SystemTime};

fn main() {
    help::add_ctrlc_handler();
    help::add_event_listener(callback);
    record().unwrap();
    help::test_tray();
}

fn callback(event: rdev::Event) {
    match event.event_type {
        rdev::EventType::KeyRelease(key) => match key {
            rdev::Key::KeyG => println!("g pressed"),
            rdev::Key::Escape => std::process::exit(0),
            _ => {}
        },
        rdev::EventType::MouseMove { x, y } => {
            let mut _x = x.clamp(0.0, 2180.0);
            let mut _y = y;
            if _x < 0.0 {
                _x = 0.0
            };
            if _y < 0.0 {
                _y = 0.0
            };
            println!("{}x{}", _x, _y);
        }
        _ => {
            println!("{:?}", event.name);
        }
    }
}

fn record() -> Result<i32, io::Error> {
    thread::spawn(|| {
        let mut counter = 0;
        let mut vec = Vec::new();
        let (width, height) = match help::get_resolution() {
            Ok(res) => res,
            Err(err) => {
                println!("Couldnt get resolution: {:?}", err);
                return err;
                //return Err(err);
            }
        };
        println!("{:?}x{:?}", width, height);

        let (w, h) = match display_size() {
            Ok(wh) => wh,
            Err(err) => {
                println!("Couldn't get display size: {:?}", err);
                std::process::exit(0);
                //return Err();
            }
        };

        println!("Your screen is {:?}x{:?}", w, h);

        loop {
            let (x, y) = help::get_mouse_pos();
            println!("{:?}x{:?}", x, y);

            let now = SystemTime::now();
            let now: DateTime<Utc> = now.into();
            let timed_pos = cursor::TimedPoint {
                x: x as f64 / width as f64,
                y: y as f64 / height as f64,
                ts: now.timestamp(),
            };
            println!("{}", &timed_pos);
            vec.push(timed_pos);
            thread::sleep(Duration::from_millis(1000));

            counter = counter + 1;
            if counter >= 4 {
                println!("{}", vec.len());
                match help::write_points(&vec) {
                    Ok(v) => println!("ok: {:?}", v),
                    Err(e) => println!("err: {}", e),
                }

                std::process::exit(0);
            }
        }
    });

    return Ok(0);
}

#[cfg(test)]
mod tests {
    #[test]
    fn internal() {
        let encoded = "";
        assert_eq!(encoded, "");
    }
}
