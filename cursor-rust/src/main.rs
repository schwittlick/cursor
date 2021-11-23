mod helpers;
mod path;
mod test;

use crate::helpers::help;
use crate::path::cursor;

use chrono::{DateTime, Utc};
use rdev;
use rdev::display_size;
use std::thread;
use std::time::{Duration, SystemTime};

fn main() {
    help::add_ctrlc_handler();
    record();
    help::test_tray();
}

fn match_events(event: rdev::Event) {
    match event.event_type {
        rdev::EventType::KeyRelease(key) => {
            match key {
                rdev::Key::KeyG => println!("g pressed"),
                rdev::Key::Escape => std::process::exit(0),
                _ => {}
            }
            println!("{:?}", event.name);
        }
        _ => {}
    }
}

fn callback(event: rdev::Event) {
    let _event_type = event.event_type;
    let _res = match_events(event);
}

fn record() {
    thread::spawn(|| {
        if let Err(error) = rdev::listen(callback) {
            println!("Error: {:?}", error)
        }
    });

    thread::spawn(|| {
        let mut counter = 0;
        let mut vec = Vec::new();
        let resolution = help::get_resolution();
        println!("{:?}", resolution);

        loop {
            let pos = help::get_mouse_pos();
            println!("{:?}", pos);
            let (w, h) = display_size().unwrap();

            println!("Your screen is {:?}x{:?}", w, h);

            let now = SystemTime::now();
            let now: DateTime<Utc> = now.into();
            //let now = now.to_rfc3339();
            let timed_pos = cursor::TimedPoint {
                x: pos.0 as f64 / resolution.0 as f64,
                y: pos.1 as f64 / resolution.1 as f64,
                time: now,
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
}

#[cfg(test)]
mod tests {
    #[test]
    fn internal() {
        let encoded = "";
        assert_eq!(encoded, "");
    }
}
