mod helpers;
mod path;
mod test;

use crate::helpers::help;
use crate::path::cursor;

//use mpsc;
use rdev;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;

fn main() {
    //let (rx, tx) = channel();
    let l: lol = lol { p: 1 };
    let mut pc = cursor::PathCollection::new();
    help::add_ctrlc_handler();
    help::add_event_listener(l.callback);
    // here i would pass a lambda to do a bit more
    // but i need to research this
    // just remove the l. from l.callback and it will work again
    let data = record(&pc);
    match data {
        Ok(pc) => {
            match help::write_points(&pc) {
                Ok(num_points) => println!("saved {} points lol", num_points),
                Err(_) => println!("failed to save points"),
            };
        }
        Err(_) => println!("failed to record"),
    };
    std::process::exit(0);
    help::test_tray();
}

struct lol {
    pub p: u8,
}
impl lol {
    pub fn callback(&self, event: rdev::Event) {}
}

fn callback(event: rdev::Event) {
    match event.event_type {
        rdev::EventType::KeyRelease(key) => match key {
            rdev::Key::KeyG => println!("g pressed"),
            rdev::Key::Escape => std::process::exit(0),
            _ => {}
        },
        rdev::EventType::MouseMove { x, y } => {
            let _x_clamped = x.clamp(0.0, 3840.0);
            let _y_clamped = y.clamp(0.0, 2160.0);
            //println!("{}x{}", _x, _y);
        }
        _ => {
            println!("{:?}", event.name);
        }
    }
}

fn record(mut pc: &cursor::PathCollection) -> Result<cursor::PathCollection, u8> {
    let handler = thread::spawn(|| {
        let mut counter = 0;

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
            if counter >= 30 {
                println!("collected {} points", pc.size());
                return pc;
            }
        }
    });

    return match handler.join() {
        Ok(pc) => Ok(pc),
        Err(_) => Err(1),
    };
}

#[cfg(test)]
mod tests {
    #[test]
    fn internal() {
        let encoded = "";
        assert_eq!(encoded, "");
    }
}
