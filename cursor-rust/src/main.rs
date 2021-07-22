mod helpers;
mod path;

use crate::helpers::help;
use crate::path::cursor;

use chrono::{DateTime, Utc};

use rdev::display_size;
use rdev::{listen, Event};
use std::thread;
use std::time::{Duration, SystemTime};

fn main() {
    help::add_ctrlc_handler();
    record();
    help::test_tray();
}

fn callback(event: Event) {
    println!("My callback {:?}", event);
}

fn record() {
    thread::spawn(|| {
        if let Err(error) = listen(callback) {
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
