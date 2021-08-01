mod helpers;
mod path;
mod test;

use crate::helpers::help;
use crate::path::cursor;

use rdev;
use std::io;
use std::thread;
use std::time::Duration;

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
            //println!("{}x{}", _x, _y);
        }
        _ => {
            println!("{:?}", event.name);
        }
    }
}

fn record() -> Result<i32, io::Error> {
    thread::spawn(|| {
        let mut counter = 0;
        let mut pc = cursor::PathCollection::new();

        loop {
            let timed_pos = cursor::TimedPoint::now();

            match pc.last() {
                Some(x) => {
                    if !x.same_pos(&timed_pos) {
                        pc.add(timed_pos);
                    }
                }
                None => pc.add(timed_pos),
            };

            thread::sleep(Duration::from_millis(100));

            counter += 1;
            if counter >= 3 {
                println!("collected {} points", pc.size());
                match help::write_points(&pc) {
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
