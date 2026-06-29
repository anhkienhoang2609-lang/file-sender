# File Sender

App GUI gửi file từ Ubuntu → Mac qua mạng LAN, dùng rsync over SSH.

## Môi trường

- Linux (Ubuntu) — máy gửi
- macOS — máy nhận (cần bật SSH: System Settings → Sharing → Remote Login)
- Python 3.10+
- `sshpass` và `rsync` phải có sẵn trên Ubuntu

```bash
sudo apt install sshpass rsync
```

## Cài đặt Python

```bash
pip install customtkinter
```

## Cấu hình (`sender_config.json`)

```bash
cp sender_config.json.example sender_config.json
```

Sửa file với thông tin máy Mac:

```json
{
  "macs": [
    {
      "name": "TenMay",
      "ip": "192.168.1.xxx",
      "user": "username",
      "pass": "password"
    }
  ]
}
```

> `sender_config.json` bị gitignore vì chứa mật khẩu.

## Chạy app

```bash
python3 sender.py
```

Hoặc dùng shortcut desktop (`FileSender.desktop`).

## Build thành file thực thi

```bash
pip install pyinstaller
pyinstaller sender.spec
# Output: dist/sender
```

## Cách dùng

1. **Folder nguồn** — chọn folder cần gửi trên Ubuntu
2. **Máy Mac** — chọn máy đích (thêm/sửa/xóa ngay trong app)
3. **Ổ đĩa** → bấm **Detect** để lấy danh sách ổ đĩa trên Mac
4. **Folder đích** → bấm **Browse** để chọn folder trong ổ đĩa
5. **GỬI FILE** → rsync chạy, log hiện tiến trình từng file + progress bar + ETA

## Cơ chế hoạt động

```
sshpass → rsync -av --progress → SSH vào Mac → copy file vào /Volumes/OĐĩa/Folder/
```

- Parse output rsync real-time → progress bar + ETA
- Log từng file khi xong
- Detect volume: SSH vào Mac, `ls /Volumes/`
- Browse folder đích: SSH vào Mac, `ls /Volumes/<vol>/`

## File quan trọng

```
sender.py                    ← toàn bộ logic app (1 file)
sender.spec                  ← PyInstaller build config
sender_config.json           ← config máy Mac (KHÔNG commit — gitignore)
sender_config.json.example   ← mẫu config
```

## Môi trường production

- Machine: Linux Ubuntu, user `mava`
- Source: `/home/mava/Mavamixi/sender.py`
- Desktop shortcut: `/home/mava/Desktop/FileSender.desktop`
- Máy nhận LAN: 192.168.1.11 (quan), 192.168.1.217 (ngocsam), 192.168.1.15 (K)
