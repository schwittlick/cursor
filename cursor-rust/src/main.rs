mod helpers;
mod path;
mod test;

use crate::helpers::help;
use crate::path::cursor;

use chrono::{DateTime, Utc};
use rdev;
use std::io;
use std::thread;
use std::time::{Duration, SystemTime};

fn main() {
    // let mut vec: Vec<cursor::TimedPoint> = Vec::new();

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
        let mut vec: Vec<cursor::TimedPoint> = Vec::new();

        let (width, height) = match help::get_resolution() {
            Ok(res) => res,
            Err(err) => {
                println!("Couldnt get resolution: {:?}", err);
                std::process::exit(0);
            }
        };
        println!("{:?}x{:?}", width, height);

        loop {
            let (x, y) = help::get_mouse_pos();
            println!("{:?}x{:?}", x, y);

            let now = SystemTime::now();
            let now: DateTime<Utc> = now.into();
            let timed_pos = cursor::TimedPoint::new(
                x as f64 / width as f64,
                y as f64 / height as f64,
                now.timestamp(),
            );

            println!("{}", &timed_pos);
            if vec.len() > 0 {
                let ll = vec.last().unwrap();
                if !ll.same_pos(&timed_pos) {
                    println!("added");
                    vec.push(timed_pos);
                } else {
                    println!("not added. hura");
                }
            } else {
                vec.push(timed_pos);
            }
            thread::sleep(Duration::from_millis(100));

            counter = counter + 1;
            if counter >= 3 {
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
