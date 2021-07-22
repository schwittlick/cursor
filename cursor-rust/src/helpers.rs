pub mod help {
    use crate::path::cursor;
    
    use std::fs;
    use std::io::prelude::*;
    use std::path::Path;
    use winapi::shared::windef::POINT;

    pub fn get_mouse_pos() -> (i32, i32) {
        let mut point = POINT { x: 0, y: 0 };
        unsafe { ::winapi::um::winuser::GetCursorPos(&mut point as *mut POINT) };
        (point.x, point.y)
    }

    pub fn get_resolution() -> (i32, i32) {
        let mut _r = unsafe {
            let _dpi_aware = ::winapi::um::winuser::SetProcessDPIAware();
            let x =
                ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CXVIRTUALSCREEN);
            let y =
                ::winapi::um::winuser::GetSystemMetrics(::winapi::um::winuser::SM_CYVIRTUALSCREEN);
            (x, y)
        };
        return (_r.0, _r.1);
    }

    pub fn write_points(point: &Vec<cursor::TimedPoint>) -> std::io::Result<()> {
        let mut f = fs::File::create("foo.txt")?;

        for p in point.iter() {
            let str = p.to_string() + "\n";
            f.write_all(str.as_bytes()).expect("couldnt write :(");
        }

        f.sync_all()?;
        Ok(())
    }

    pub fn add_ctrlc_handler() {
        ctrlc::set_handler(move || {
            println!("cleaning up.");
            std::process::exit(0);
        })
        .expect("Error setting Ctrl-C handler");
    }

    fn writesomestuff() {
        let paths = fs::read_dir("../data/recordings/").unwrap();
        for p in paths {
            let path_string = p.unwrap().path();
            let path = Path::new(path_string.as_os_str());
            let display = path.display();
            // Open the path in read-only mode, returns `io::Result<File>`
            let mut file = match fs::File::open(&path) {
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
    pub fn test_tray() {
        use simple_logger::SimpleLogger;
        use std::collections::HashMap;
        #[cfg(target_os = "linux")]
        use std::path::Path;
        #[cfg(target_os = "macos")]
        use tao::platform::macos::{CustomMenuItemExtMacOS, NativeImage};
        use tao::{
            event::{Event, WindowEvent},
            event_loop::{ControlFlow, EventLoop},
            menu::{ContextMenu as Menu, MenuItemAttributes, MenuType},
            system_tray::SystemTrayBuilder,
            window::{Window, WindowId},
        };

        SimpleLogger::new().init().unwrap();
        let event_loop = EventLoop::new();
        let mut windows: HashMap<WindowId, Window> = HashMap::new();

        let mut tray_menu = Menu::new();

        let mut submenu = Menu::new();

        // open new window menu item
        let open_new_window_element = submenu.add_item(MenuItemAttributes::new("Open new window"));

        // set default icon
        #[cfg(target_os = "macos")]
        open_new_window_element
            .clone()
            .set_native_image(NativeImage::StatusAvailable);

        // focus all window menu item
        let mut focus_all_window =
            tray_menu.add_item(MenuItemAttributes::new("Focus window").with_enabled(false));

        let change_menu = tray_menu.add_item(MenuItemAttributes::new("Change menu"));

        // inject submenu into tray_menu
        tray_menu.add_submenu("Sub menu", true, submenu);

        // add quit button
        let quit_element = tray_menu.add_item(MenuItemAttributes::new("Quit"));

        // Windows require Vec<u8> ICO file
        #[cfg(target_os = "windows")]
        let icon = include_bytes!("icon.ico").to_vec();
        // macOS require Vec<u8> PNG file
        #[cfg(target_os = "macos")]
        let icon = include_bytes!("icon.png").to_vec();
        // Linux require Pathbuf to PNG file
        #[cfg(target_os = "linux")]
        let icon = Path::new(env!("CARGO_MANIFEST_DIR")).join("examples/icon.png");

        // Windows require Vec<u8> ICO file
        #[cfg(target_os = "windows")]
        let new_icon = include_bytes!("icon_blue.ico").to_vec();
        // macOS require Vec<u8> PNG file
        #[cfg(target_os = "macos")]
        let new_icon = include_bytes!("icon_dark.png").to_vec();
        // Linux require Pathbuf to PNG file
        #[cfg(target_os = "linux")]
        let new_icon = Path::new(env!("CARGO_MANIFEST_DIR")).join("examples/icon_dark.png");

        // Menu is shown with left click on macOS and right click on Windows.
        let mut system_tray = SystemTrayBuilder::new(icon.clone(), Some(tray_menu))
            .build(&event_loop)
            .unwrap();

        event_loop.run(move |event, event_loop, control_flow| {
            *control_flow = ControlFlow::Wait;

            let mut create_window_or_focus = || {
                // if we already have one window, let's focus instead
                if !windows.is_empty() {
                    for window in windows.values() {
                        window.set_focus();
                    }
                    return;
                }

                // create new window
                let mut open_new_window_element = open_new_window_element.clone();
                let mut focus_all_window = focus_all_window.clone();

                let window = Window::new(event_loop).unwrap();
                windows.insert(window.id(), window);
                // disable button
                open_new_window_element.set_enabled(false);
                // change title (text)
                open_new_window_element.set_title("Window already open");
                // set checked
                open_new_window_element.set_selected(true);
                // enable focus window
                focus_all_window.set_enabled(true);
                // update tray icon
                system_tray.set_icon(new_icon.clone());
                // add macOS Native red dot
                #[cfg(target_os = "macos")]
                open_new_window_element.set_native_image(NativeImage::StatusUnavailable);
            };

            match event {
                Event::WindowEvent {
                    event, window_id, ..
                } => {
                    if event == WindowEvent::CloseRequested {
                        let mut open_new_window_element = open_new_window_element.clone();
                        // Remove window from our hashmap
                        windows.remove(&window_id);
                        // Modify our button's state
                        open_new_window_element.set_enabled(true);
                        focus_all_window.set_enabled(false);
                        // Reset text
                        open_new_window_element.set_title("Open new window");
                        // Set selected
                        open_new_window_element.set_selected(false);
                        // Change tray icon
                        system_tray.set_icon(icon.clone());
                        // macOS have native image available that we can use in our menu-items
                        #[cfg(target_os = "macos")]
                        open_new_window_element.set_native_image(NativeImage::StatusAvailable);
                    }
                }
                // on Windows, habitually, we show the window with left click
                #[cfg(target_os = "windows")]
                Event::TrayEvent {
                    event: tao::event::TrayEvent::LeftClick,
                    ..
                } => create_window_or_focus(),
                // left click on menu item
                Event::MenuEvent {
                    menu_id,
                    // specify only context menu's
                    origin: MenuType::ContextMenu,
                    ..
                } => {
                    // Click on Open new window or focus item
                    if menu_id == open_new_window_element.clone().id()
                        || menu_id == focus_all_window.clone().id()
                    {
                        create_window_or_focus();
                    }
                    // click on `quit` item
                    if menu_id == quit_element.clone().id() {
                        // tell our app to close at the end of the loop.
                        *control_flow = ControlFlow::Exit;
                    }

                    if menu_id == change_menu.clone().id() {
                        let mut tray_menu = Menu::new();
                        tray_menu.add_item(MenuItemAttributes::new("Quit"));
                        system_tray.set_menu(&tray_menu);
                    }

                    println!("Clicked on {:?}", menu_id);
                }
                _ => (),
            }
        });
    }
}
