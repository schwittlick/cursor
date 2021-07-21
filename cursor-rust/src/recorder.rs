use winapi::shared::windef::POINT;
use std::thread;
use std::fmt;
use chrono::{DateTime, Utc}; // 0.4.15
use std::time::{Duration, SystemTime};
use rdev::display_size;
use rdev::{listen, Event};

fn get_mouse_pos() -> (i32, i32) {
    let mut point = POINT { x: 0, y: 0 };
    unsafe { ::winapi::um::winuser::GetCursorPos(&mut point as *mut POINT) };
    (point.x, point.y)
}

fn get_resolution() -> (i32, i32)
{
    let mut _r = unsafe {
        let dpi_aware = ::winapi::um::winuser::SetProcessDPIAware();
        let x = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CXVIRTUALSCREEN);
        let y = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CYVIRTUALSCREEN);
        (x, y)
    };
    return (_r.0, _r.1);
}

struct TimedPoint 
{
    x: f64,
    y: f64,
    //time: String
    time: DateTime<Utc>
}

impl fmt::Display for TimedPoint {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {}, {})", self.x, self.y, self.time.to_rfc3339())
    }
}

fn callback(event: Event) {
    println!("My callback {:?}", event);
}

fn record()
{
    if let Err(error) = listen(callback) {
        println!("Error: {:?}", error)
    }

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
        let timed_pos = TimedPoint{x: pos.0 as f64/ resolution.0 as f64, y: pos.1 as f64 / resolution.1 as f64, time: now};
        println!("{}", &timed_pos);
        thread::sleep(Duration::from_millis(100));
    }
}



fn borrowing()
{
    let s1 = "hello dolly".to_string();
    let mut rs1 = &s1;
    {
        let tmp = "hello world".to_string();
        rs1 = &tmp;
        rs1 = &s1;
    }
    println!("ref {}", s1);
}

fn struct_test()
{
    //let mut point = TimedPoint{x: 0.0, y: 0.0, time: "jetzt".to_string()};
    //println!("{:?}", &point.time);
}

fn main()
{
    ctrlc::set_handler(move || {
        println!("cleaning up.");
        std::process::exit(0);
    })
    .expect("Error setting Ctrl-C handler");

    record();

    //borrowing();
    struct_test();
}
