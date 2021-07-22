use chrono::{DateTime, Utc}; // 0.4.15
use rdev::display_size;
use rdev::{listen, Event};
use std::fmt;
use std::fs::File;
use std::io::prelude::*;
use std::thread;
use std::time::{Duration, SystemTime};
use winapi::shared::windef::POINT;

fn get_mouse_pos() -> (i32, i32) {
    let mut point = POINT { x: 0, y: 0 };
    unsafe { ::winapi::um::winuser::GetCursorPos(&mut point as *mut POINT) };
    (point.x, point.y)
}

fn get_resolution() -> (i32, i32) {
    let mut _r = unsafe {
        let _dpi_aware = ::winapi::um::winuser::SetProcessDPIAware();
        let x = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CXVIRTUALSCREEN);
        let y = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CYVIRTUALSCREEN);
        (x, y)
    };
    return (_r.0, _r.1);
}

struct TimedPoint {
    x: f64,
    y: f64,
    time: DateTime<Utc>,
}

fn main() {
    ctrlc::set_handler(move || {
        println!("cleaning up.");
        std::process::exit(0);
    })
    .expect("Error setting Ctrl-C handler");

    record();
}

impl fmt::Display for TimedPoint {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // let string = format!("({x.*}, {}, {})", 3, x=self.x, y=self.y, time=self.time.to_rfc3339());
        write!(f, "({}, {}, {})", self.x, self.y, self.time.to_rfc3339())
    }
}

fn callback(event: Event) {
    println!("My callback {:?}", event);
}

fn write_points(point: &Vec<TimedPoint>) -> std::io::Result<()> {
    let mut f = File::create("foo.txt")?;

    for p in point.iter() {
        let str = p.to_string() + "\n";
        f.write_all(str.as_bytes()).expect("couldnt write :(");
    }

    f.sync_all()?;
    Ok(())
}

fn record() {
    thread::spawn(|| {
        if let Err(error) = listen(callback) {
            println!("Error: {:?}", error)
        }
    });

    let mut counter = 0;
    let mut vec = Vec::new();

    loop {
        let pos = get_mouse_pos();
        println!("{:?}", pos);
        let resolution = get_resolution();
        println!("{:?}", resolution);
        let (w, h) = display_size().unwrap();

        println!("Your screen is {:?}x{:?}", w, h);

        let now = SystemTime::now();
        let now: DateTime<Utc> = now.into();
        //let now = now.to_rfc3339();
        let timed_pos = TimedPoint {
            x: pos.0 as f64 / resolution.0 as f64,
            y: pos.1 as f64 / resolution.1 as f64,
            time: now,
        };
        println!("{}", &timed_pos);
        vec.push(timed_pos);
        thread::sleep(Duration::from_millis(100));

        counter = counter + 1;
        if counter >= 4 {
            println!("{}", vec.len());
            match write_points(&vec) {
                Ok(v) => println!("ok: {:?}", v),
                Err(e) => println!("err: {}", e),
            }

            std::process::exit(0);
        }
    }
}
