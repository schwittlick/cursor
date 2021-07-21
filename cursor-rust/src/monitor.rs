use std::ffi::OsString;
use std::io::Error;
use std::mem;
use std::ptr;
use std::os::windows::ffi::OsStringExt;

use winapi::shared::windef::POINT;
use winapi::shared::minwindef::{LPARAM, TRUE, BOOL};
use winapi::shared::windef::{HMONITOR, HDC, LPRECT, RECT};
use winapi::um::winuser::{EnumDisplayMonitors, GetMonitorInfoW, MONITORINFOEXW};

fn main() {
    let mut _p = unsafe {
        let mut point = POINT { x: 0, y: 0 };
        unsafe { ::winapi::um::winuser::GetCursorPos(&mut point as *mut POINT) };
        (point.x, point.y)
    };
    //println!("{:?}", _p);
    let mut _r = unsafe {
        let dpi_aware = ::winapi::um::winuser::SetProcessDPIAware();
        let x = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CYVIRTUALSCREEN);
        let y = ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CXVIRTUALSCREEN);
        (x, y, dpi_aware)
    };
    println!("{:?}", _r);
    //let r = ::winapi::um::winuser::GetSystemMetrics(78);
    for monitor in enumerate_monitors() {
        // Convert the WCHAR[] to a unicode OsString
        let name = match &monitor.szDevice[..].iter().position(|c| *c == 0) {
            Some(len) => OsString::from_wide(&monitor.szDevice[0..*len]),
            None => OsString::from_wide(&monitor.szDevice[0..monitor.szDevice.len()]),
        };

        // Print some information to the console
        println!("Display name = {}", name.to_str().unwrap());
        println!("    Left: {}", monitor.rcWork.left);
        println!("   Right: {}", monitor.rcWork.right);
        println!("     Top: {}", monitor.rcWork.top);
        println!("  Bottom: {}", monitor.rcWork.bottom);
    }
}

///////////////////////////////////////////////////////////////
// The method that numerates all monitors

fn enumerate_monitors() -> Vec<MONITORINFOEXW> {
    // Define the vector where we will store the result
    let mut monitors = Vec::<MONITORINFOEXW>::new();
    let userdata = &mut monitors as *mut _;

    let result = unsafe {
        EnumDisplayMonitors(
            ptr::null_mut(),
            ptr::null(),
            Some(enumerate_monitors_callback),
            userdata as LPARAM,
        )
    };

    if result != TRUE {
        // Get the last error for the current thread.
        // This is analogous to calling the Win32 API GetLastError.
        panic!("Could not enumerate monitors: {}", Error::last_os_error());
    }

    monitors
}

///////////////////////////////////////////////////////////////
// The callback from EnumDisplayMonitors

unsafe extern "system" fn enumerate_monitors_callback(
    monitor: HMONITOR,
    _: HDC,
    _: LPRECT,
    userdata: LPARAM,
) -> BOOL {
    // Get the userdata where we will store the result
    let monitors: &mut Vec<MONITORINFOEXW> = mem::transmute(userdata);

    // Initialize the MONITORINFOEXW structure and get a pointer to it
    let mut monitor_info: MONITORINFOEXW = mem::zeroed();
    monitor_info.cbSize = mem::size_of::<MONITORINFOEXW>() as u32;
    let monitor_info_ptr = <*mut _>::cast(&mut monitor_info);

    // Call the GetMonitorInfoW win32 API
    let result = GetMonitorInfoW(monitor, monitor_info_ptr);
    if result == TRUE {
        // Push the information we received to userdata
        monitors.push(monitor_info);
    }

    TRUE
}