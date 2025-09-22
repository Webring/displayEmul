use pancurses::{endwin, initscr, noecho};
use std::io::{Read, Write};
use std::os::unix::net::{UnixListener, UnixStream};

const GRADIENT: &str = " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@▒▓█";

fn symbol(level: u8) -> char {
    let gradient_len = GRADIENT.chars().count();
    let index = (level as usize * (gradient_len - 1)) / 255;
    GRADIENT.chars().nth(index).unwrap_or(' ')
}

fn send_window_size(stream: &mut UnixStream, window: &pancurses::Window) {
    let (height, width) = window.get_max_yx();
    let mut buffer = [0u8; 6];
    buffer[0] = 1;
    buffer[1] = 0;
    buffer[2] = ((width as u16) >> 8) as u8;
    buffer[3] = (width as u16 & 0xFF) as u8;
    buffer[4] = ((height as u16) >> 8) as u8;
    buffer[5] = (height as u16 & 0xFF) as u8;
    let _ = stream.write_all(&buffer);
}

fn handle_client(mut stream: UnixStream, window: &pancurses::Window) {
    let mut buffer = [0u8; 6];
    loop {
        match stream.read(&mut buffer) {
            Ok(n) => {
                if n == 0 {
                    break;
                }
                match buffer[0] {
                    1 => {
                        send_window_size(&mut stream, &window);
                    }
                    2 => {
                        window.clear();
                    }
                    3 => {
                        let x = ((buffer[2] as u16) << 8 | buffer[3] as u16) as i32;
                        let y = ((buffer[4] as u16) << 8 | buffer[5] as u16) as i32;
                        let ch = symbol(buffer[1]);
                        window.mv(y, x);
                        window.addch(ch);
                        window.refresh();
                    }
                    _ => {}
                }
            }
            Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {}
            Err(_) => break,
        }
    }
}

fn main() -> std::io::Result<()> {
    let _ = std::fs::remove_file("/tmp/monitor.sock"); // удаляем старый сокет
    let listener = UnixListener::bind("/tmp/monitor.sock")?;
    println!("Сервер запущен, ждём клиентов...");

    let window = initscr();
    noecho();

    for stream in listener.incoming() {
        match stream {
            Ok(mut stream) => {
                send_window_size(&mut stream, &window);
                stream.set_nonblocking(true)?;
                handle_client(stream, &window);
            }
            Err(e) => eprintln!("Ошибка подключения: {}", e),
        }
    }

    endwin();
    Ok(())
}
