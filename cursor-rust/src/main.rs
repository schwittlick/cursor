use std::fs;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;

use winapi::shared::windef::POINT;

fn get_mouse_pos() -> (i32, i32) {
    let mut point = POINT { x: 0, y: 0 };
    unsafe { ::winapi::um::winuser::GetCursorPos(&mut point as *mut POINT) };
    (point.x, point.y)
}

fn set_mouse_pos(x: i32 , y: i32) {
    unsafe { ::winapi::um::winuser::SetCursorPos(x, y) };
}

fn main() {
    // store mouse postion
    let (x, y) = get_mouse_pos();

    // print mouse coords
    print!("coords = {},{}", x, y);

    // mouse mouse
    set_mouse_pos(250, 250);

}

fn main2() {
    let paths = fs::read_dir("../data/recordings/").unwrap();
    for p in paths {
        let path_string = p.unwrap().path();
        let path = Path::new(path_string.as_os_str());
        let display = path.display();
        // Open the path in read-only mode, returns `io::Result<File>`
        let mut file = match File::open(&path) {
            Err(why) => panic!("couldn't open {}: {}", display, why),
            Ok(file) => file,
        };

        // Read the file contents into a string, returns `io::Result<usize>`
        let mut s = String::new();
        match file.read_to_string(&mut s) {
            Err(why) => panic!("couldn't read {}: {}", display, why),
            Ok(_) => print!("{} contains:\n{}\n", display, &s[..30]),
        }

        }
}
