#!/usr/bin/env python3
import os, json, re, threading, subprocess, tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("dark")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sender_config.json")

BG     = "#111111"
BG2    = "#1a1a1a"
BG3    = "#222222"
ACCENT = "#ffffff"
GRAY   = "#888888"
BLUE   = "#2196F3"
GREEN  = "#4CAF50"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    return {"macs": []}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

def zenity_folder(title="Chọn folder"):
    try:
        r = subprocess.run(["zenity","--file-selection","--directory","--filename=/home/mava/",f"--title={title}"],
                           capture_output=True, text=True)
        return r.stdout.strip()
    except: return ""

class SenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Sender")
        self.geometry("780x750")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.cfg = load_config()
        self.selected_src = tk.StringVar()
        self.selected_mac = tk.StringVar()
        self.selected_vol = tk.StringVar()
        self.selected_dst = tk.StringVar()
        self.is_running = False
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 20, "pady": 5}

        ctk.CTkLabel(self, text="FILE SENDER", font=("Consolas", 22, "bold"),
                     text_color=ACCENT).pack(pady=(20,2))
        ctk.CTkLabel(self, text="Ubuntu → Mac over LAN",
                     font=("Consolas", 11), text_color=GRAY).pack(pady=(0,14))

        # Source
        fs = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        fs.pack(fill="x", **pad)
        ctk.CTkLabel(fs, text="Folder nguồn", font=("Consolas", 12, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=14, pady=(10,3))
        r = ctk.CTkFrame(fs, fg_color="transparent"); r.pack(fill="x", padx=14, pady=(0,10))
        self.src_entry = ctk.CTkEntry(r, textvariable=self.selected_src, width=560,
                                       font=("Consolas", 11), fg_color=BG3, border_color="#333")
        self.src_entry.pack(side="left")
        ctk.CTkButton(r, text="...", width=55, command=self._browse_src,
                      fg_color="#333", hover_color="#555").pack(side="left", padx=(6,0))

        # Mac
        fm = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        fm.pack(fill="x", **pad)
        ctk.CTkLabel(fm, text="Máy Mac", font=("Consolas", 12, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=14, pady=(10,3))
        r2 = ctk.CTkFrame(fm, fg_color="transparent"); r2.pack(fill="x", padx=14, pady=(0,10))
        self.mac_dropdown = ctk.CTkOptionMenu(r2, variable=self.selected_mac,
                                               values=self._mac_names(), width=390,
                                               font=("Consolas", 11), fg_color=BG3,
                                               button_color="#333", button_hover_color="#555",
                                               command=self._on_mac_select)
        self.mac_dropdown.pack(side="left")
        ctk.CTkButton(r2, text="🔍 Scan", width=80, fg_color="#1a3a2a", hover_color="#2d6b4a",
                      command=self._scan_macs).pack(side="left", padx=(6,0))
        ctk.CTkButton(r2, text="+ Thêm", width=75, fg_color="#1a3a1a", hover_color="#2d6b2d",
                      command=self._add_mac).pack(side="left", padx=(4,0))
        ctk.CTkButton(r2, text="Sửa", width=55, fg_color="#1a2a3a", hover_color="#2d4a6b",
                      command=self._edit_mac).pack(side="left", padx=(4,0))
        ctk.CTkButton(r2, text="Xóa", width=55, fg_color="#3a1a1a", hover_color="#6b2d2d",
                      command=self._del_mac).pack(side="left", padx=(4,0))

        # Volume
        fv = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        fv.pack(fill="x", **pad)
        ctk.CTkLabel(fv, text="Ổ đĩa", font=("Consolas", 12, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=14, pady=(10,3))
        r3 = ctk.CTkFrame(fv, fg_color="transparent"); r3.pack(fill="x", padx=14, pady=(0,10))
        self.vol_dropdown = ctk.CTkOptionMenu(r3, variable=self.selected_vol,
                                               values=["-- chọn Mac trước --"], width=390,
                                               font=("Consolas", 11), fg_color=BG3,
                                               button_color="#333", button_hover_color="#555")
        self.vol_dropdown.pack(side="left")
        ctk.CTkButton(r3, text="Detect", width=80, command=self._detect_volumes,
                      fg_color="#333", hover_color="#555").pack(side="left", padx=(6,0))

        # Dest
        fd = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        fd.pack(fill="x", **pad)
        ctk.CTkLabel(fd, text="Folder đích", font=("Consolas", 12, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=14, pady=(10,3))
        r4 = ctk.CTkFrame(fd, fg_color="transparent"); r4.pack(fill="x", padx=14, pady=(0,10))
        self.dst_entry = ctk.CTkEntry(r4, textvariable=self.selected_dst, width=560,
                                       font=("Consolas", 11), fg_color=BG3, border_color="#333")
        self.dst_entry.pack(side="left")
        ctk.CTkButton(r4, text="Browse", width=70, command=self._browse_dst,
                      fg_color="#333", hover_color="#555").pack(side="left", padx=(6,0))

        # Send button
        self.btn_send = ctk.CTkButton(self, text="GỬI FILE", height=46,
                                       font=("Consolas", 15, "bold"),
                                       fg_color=BLUE, hover_color="#1565C0",
                                       text_color="white", command=self._send)
        self.btn_send.pack(fill="x", padx=20, pady=(10,4))

        # Progress
        fp = ctk.CTkFrame(self, fg_color="transparent")
        fp.pack(fill="x", padx=20, pady=(2,4))
        self.progress_bar = ctk.CTkProgressBar(fp, height=14, corner_radius=6,
                                                fg_color=BG2, progress_color=BLUE)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.eta_label = ctk.CTkLabel(fp, text="", font=("Consolas", 11),
                                       text_color=GRAY, width=110, anchor="e")
        self.eta_label.pack(side="left", padx=(8,0))

        # Log
        ctk.CTkLabel(self, text="Log", font=("Consolas", 12, "bold"),
                     text_color=GRAY).pack(anchor="w", padx=20, pady=(2,2))
        self.log_box = ctk.CTkTextbox(self, height=260, font=("Consolas", 11),
                                       fg_color=BG2, text_color="#ccc")
        self.log_box.pack(fill="x", padx=20, pady=(0,6))
        self.log_box.configure(state="disabled")

        # Status
        self.status_label = ctk.CTkLabel(self, text="Sẵn sàng",
                                          font=("Consolas", 11), text_color=GRAY)
        self.status_label.pack(anchor="w", padx=20, pady=(0,10))

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _mac_names(self):
        n = [f"{m['name']}  ({self._mac_host(m)})" for m in self.cfg["macs"]]
        return n if n else ["-- chưa có máy --"]

    def _get_mac(self):
        sel = self.selected_mac.get()
        for m in self.cfg["macs"]:
            if m["name"] in sel: return m
        return None

    def _mac_host(self, mac):
        return mac.get("host") or mac.get("ip", "")

    def _status(self, msg):
        self.status_label.configure(text=msg)

    def _lock_ui(self, locked):
        state = "disabled" if locked else "normal"
        for w in [self.src_entry, self.dst_entry, self.mac_dropdown, self.vol_dropdown]:
            w.configure(state=state)

    def _browse_src(self):
        if self.is_running: return
        p = zenity_folder("Chọn folder nguồn")
        if p: self.selected_src.set(p)

    def _on_mac_select(self, _=None):
        if not self.is_running:
            self.selected_vol.set("-- nhấn Detect --")

    def _detect_volumes(self):
        if self.is_running: return
        mac = self._get_mac()
        if not mac: self._status("Chưa chọn Mac"); return
        self._status(f"Detecting {mac['name']}...")
        def w():
            try:
                r = subprocess.run(
                    ["sshpass","-p",mac["pass"],"ssh","-o","StrictHostKeyChecking=no",
                     "-o","ConnectTimeout=8",
                     f"{mac['user']}@{self._mac_host(mac)}","ls /Volumes/"],
                    capture_output=True, text=True, timeout=12)
                vols = [v.strip() for v in r.stdout.strip().split("\n") if v.strip()]
                if vols:
                    self.after(0, lambda v=vols: self.vol_dropdown.configure(values=v))
                    self.after(0, lambda v=vols: self.selected_vol.set(v[0]))
                    self.after(0, lambda v=vols: self._status("OK: " + ", ".join(v)))
                elif r.returncode != 0:
                    err = r.stderr.strip().split("\n")[0] if r.stderr.strip() else f"exit code {r.returncode}"
                    self.after(0, lambda e=err: self._status(f"❌ SSH lỗi: {e}"))
                    self.after(0, lambda e=err: self._log(f"❌ Detect thất bại: {e}"))
                else:
                    self.after(0, lambda: self._status("Không tìm thấy ổ"))
            except subprocess.TimeoutExpired:
                self.after(0, lambda ip=mac['ip']: self._status(f"❌ Timeout — không kết nối được {ip}"))
                self.after(0, lambda ip=mac['ip']: self._log(f"❌ Timeout kết nối {ip} — kiểm tra IP hoặc máy đã bật chưa"))
            except Exception as e:
                self.after(0, lambda err=str(e): self._status(f"❌ Lỗi: {err}"))
        threading.Thread(target=w, daemon=True).start()

    def _browse_dst(self):
        if self.is_running: return
        mac = self._get_mac(); vol = self.selected_vol.get()
        if not mac or vol.startswith("--"): self._status("Chọn Mac và ổ trước"); return
        def w():
            try:
                r = subprocess.run(
                    ["sshpass","-p",mac["pass"],"ssh","-o","StrictHostKeyChecking=no",
                     f"{mac['user']}@{self._mac_host(mac)}", f"ls \"/Volumes/{vol}/\""],
                    capture_output=True, text=True, timeout=10)
                folders = [f.strip() for f in r.stdout.strip().split("\n") if f.strip()]
                if folders: self.after(0, lambda: self._show_folder_picker(folders, vol))
            except Exception as e:
                self.after(0, lambda: self._status(f"Lỗi: {e}"))
        threading.Thread(target=w, daemon=True).start()

    def _show_folder_picker(self, folders, vol):
        win = ctk.CTkToplevel(self)
        win.title("Chọn folder đích")
        win.geometry("400x450")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text=f"/Volumes/{vol}/", font=("Consolas", 12, "bold"),
                     text_color=ACCENT).pack(pady=(15,5))
        frame = ctk.CTkScrollableFrame(win, height=300, fg_color=BG2)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        sel_var = tk.StringVar(value=folders[0])
        for f in folders:
            ctk.CTkRadioButton(frame, text=f, variable=sel_var, value=f,
                               font=("Consolas", 11)).pack(anchor="w", pady=2)
        def confirm():
            self.selected_dst.set(sel_var.get()); win.destroy()
        ctk.CTkButton(win, text="Chọn", command=confirm,
                      fg_color=BLUE, hover_color="#1565C0").pack(pady=10)

    def _scan_macs(self):
        if self.is_running: return
        self._status("Đang scan mạng LAN...")
        def w():
            try:
                r = subprocess.run(
                    ["avahi-browse", "-t", "-r", "_ssh._tcp"],
                    capture_output=True, text=True, timeout=15)
                found = {}
                in_ipv6 = False
                cur = {}
                for line in r.stdout.splitlines():
                    if line.startswith("="):
                        in_ipv6 = "IPv6" in line
                        cur = {}
                        if in_ipv6: continue
                        cur = {"display": re.sub(r'\s+', ' ', line.split("IPv4")[-1].split("SSH")[0].strip())}
                    elif in_ipv6:
                        continue
                    elif "hostname" in line and "[" in line:
                        cur["host"] = line.split("[")[1].rstrip("]").strip()
                    elif "address" in line and "[" in line:
                        cur["ip"] = line.split("[")[1].rstrip("]").strip()
                        if cur.get("host") and cur["host"] not in found:
                            found[cur["host"]] = dict(cur)
                if found:
                    self.after(0, lambda f=found: self._show_scan_results(f))
                else:
                    self.after(0, lambda: self._status("Không tìm thấy Mac nào"))
            except Exception as e:
                self.after(0, lambda err=str(e): self._status(f"❌ Scan lỗi: {err}"))
        threading.Thread(target=w, daemon=True).start()

    def _show_scan_results(self, found):
        win = ctk.CTkToplevel(self)
        win.title("Máy Mac tìm thấy")
        win.geometry("480x400")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text=f"Tìm thấy {len(found)} máy", font=("Consolas", 13, "bold"),
                     text_color=ACCENT).pack(pady=(15,5))
        frame = ctk.CTkScrollableFrame(win, height=200, fg_color=BG2)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        existing_hosts = {m.get("host"): m for m in self.cfg["macs"] if m.get("host")}
        saved_pass = next((m.get("pass","") for m in self.cfg["macs"] if m.get("pass")), "")
        checks = {}
        for host, info in found.items():
            already = host in existing_hosts
            var = tk.BooleanVar(value=False)
            lbl = f"{info['display']}  ({host})" + ("  ✓" if already else "")
            ctk.CTkCheckBox(frame, text=lbl, variable=var,
                            font=("Consolas", 11)).pack(anchor="w", pady=3)
            checks[host] = (var, info)
        cred_frame = ctk.CTkFrame(win, fg_color="transparent")
        cred_frame.pack(fill="x", padx=15, pady=(5,0))
        ctk.CTkLabel(cred_frame, text="Username:", font=("Consolas", 11),
                     text_color=GRAY).pack(side="left")
        user_entry = ctk.CTkEntry(cred_frame, width=120, font=("Consolas", 11), fg_color=BG3)
        user_entry.pack(side="left", padx=(8,0))
        ctk.CTkLabel(cred_frame, text="Password:", font=("Consolas", 11),
                     text_color=GRAY).pack(side="left", padx=(12,0))
        pass_entry = ctk.CTkEntry(cred_frame, width=120, font=("Consolas", 11),
                                   fg_color=BG3, show="*")
        pass_entry.insert(0, saved_pass)
        pass_entry.pack(side="left", padx=(8,0))

        def add_selected():
            pw = pass_entry.get().strip()
            usr = user_entry.get().strip()
            if not usr:
                self._status("❌ Cần nhập username"); return
            added = 0
            for host, (var, info) in checks.items():
                if not var.get(): continue
                existing = existing_hosts.get(host)
                if existing:
                    existing.update({"user": usr or existing.get("user",""), "pass": pw or existing.get("pass","")})
                else:
                    self.cfg["macs"].append({
                        "name": info["display"], "host": host,
                        "user": usr, "pass": pw
                    })
                added += 1
            save_config(self.cfg)
            self.mac_dropdown.configure(values=self._mac_names())
            self.selected_mac.set(self._mac_names()[0])
            self._status(f"✅ Đã thêm {added} máy")
            win.destroy()

        ctk.CTkButton(win, text="Thêm đã chọn", command=add_selected,
                      fg_color=BLUE, hover_color="#1565C0").pack(pady=10)

    def _add_mac(self):
        if self.is_running: return
        win = ctk.CTkToplevel(self)
        win.title("Thêm máy Mac")
        win.geometry("350x310")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        fields = {}
        for label, key in [("Tên hiển thị","name"),("Hostname (vd: editor2.local)","host"),("Username","user"),("Password","pass")]:
            ctk.CTkLabel(win, text=label, font=("Consolas", 11),
                         text_color=ACCENT).pack(anchor="w", padx=20, pady=(8,0))
            e = ctk.CTkEntry(win, font=("Consolas", 11), width=300,
                             fg_color=BG3, show="*" if key=="pass" else "")
            e.pack(padx=20); fields[key] = e
        def save():
            mac = {k: v.get().strip() for k,v in fields.items()}
            if not all(mac.values()): messagebox.showwarning("Lỗi","Điền đầy đủ"); return
            self.cfg["macs"].append(mac); save_config(self.cfg)
            self.mac_dropdown.configure(values=self._mac_names())
            self.selected_mac.set(self._mac_names()[-1])
            self._status(f"Đã thêm: {mac['name']}"); win.destroy()
        ctk.CTkButton(win, text="Lưu", command=save,
                      fg_color=BLUE, hover_color="#1565C0").pack(pady=15)

    def _edit_mac(self):
        if self.is_running: return
        mac = self._get_mac()
        if not mac: self._status("Chưa chọn Mac"); return
        win = ctk.CTkToplevel(self)
        win.title("Sửa máy Mac")
        win.geometry("350x310")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        fields = {}
        for label, key in [("Tên hiển thị","name"),("Hostname (vd: editor2.local)","host"),("Username","user"),("Password","pass")]:
            ctk.CTkLabel(win, text=label, font=("Consolas", 11),
                         text_color=ACCENT).pack(anchor="w", padx=20, pady=(8,0))
            e = ctk.CTkEntry(win, font=("Consolas", 11), width=300,
                             fg_color=BG3, show="*" if key=="pass" else "")
            e.insert(0, mac.get(key, mac.get("ip","") if key=="host" else ""))
            e.pack(padx=20); fields[key] = e
        def save():
            updated = {k: v.get().strip() for k,v in fields.items()}
            if not all(updated.values()): messagebox.showwarning("Lỗi","Điền đầy đủ"); return
            for m in self.cfg["macs"]:
                if m["name"] == mac["name"]: m.update(updated)
            save_config(self.cfg)
            self.mac_dropdown.configure(values=self._mac_names())
            self.selected_mac.set(f"{updated['name']}  ({updated['ip']})")
            self._status(f"Đã cập nhật: {updated['name']}"); win.destroy()
        ctk.CTkButton(win, text="Lưu", command=save,
                      fg_color=BLUE, hover_color="#1565C0").pack(pady=15)

    def _del_mac(self):
        if self.is_running: return
        mac = self._get_mac()
        if not mac: return
        self.cfg["macs"] = [m for m in self.cfg["macs"] if m["name"] != mac["name"]]
        save_config(self.cfg)
        names = self._mac_names()
        self.mac_dropdown.configure(values=names)
        self.selected_mac.set(names[0])
        self._status(f"Đã xóa: {mac['name']}")

    def _send(self):
        if self.is_running: return
        src = self.selected_src.get().strip()
        mac = self._get_mac()
        vol = self.selected_vol.get().strip()
        dst = self.selected_dst.get().strip()

        if not src or not os.path.exists(src):
            self._status("Chọn folder nguồn hợp lệ"); return
        if not mac:
            self._status("Chưa chọn Mac"); return
        if not vol or vol.startswith("--"):
            self._status("Chưa chọn ổ"); return

        dest_path = f"/Volumes/{vol}/{dst}" if dst else f"/Volumes/{vol}/"
        self.is_running = True
        self._lock_ui(True)
        self.btn_send.configure(text="ĐANG GỬI...", fg_color="#555", state="disabled")
        self.progress_bar.set(0)
        self.eta_label.configure(text="")
        self._log(f"Bắt đầu gửi: {src}")
        self._log(f"Đích: {mac['name']} → {dest_path}")
        self._status("Đang gửi...")

        def worker():
            import time as _time, re as _re
            try:
                cmd = [
                    "sshpass", "-p", mac["pass"],
                    "rsync", "-av", "--progress",
                    "-e", "ssh -o StrictHostKeyChecking=no",
                    src + "/",
                    f"{mac['user']}@{self._mac_host(mac)}:{dest_path}"
                ]

                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )

                buf = ""
                start_time = _time.time()
                current_file = ""
                total_files = 0
                success = 0

                for chunk in iter(lambda: proc.stdout.read(256), ""):
                    buf += chunk
                    now = _time.time()

                    # Parse to-chk=X/Y → progress + ETA + log từng file
                    for m in _re.finditer(r'to-chk=(\d+)/(\d+)', buf):
                        remaining, total = int(m.group(1)), int(m.group(2))
                        total_files = total
                        done = total - remaining
                        frac = done / total if total else 0
                        elapsed = now - start_time
                        if frac > 0.01:
                            eta_sec = int(elapsed / frac - elapsed)
                            if eta_sec >= 3600:
                                eta_str = f"{eta_sec//3600}h{(eta_sec%3600)//60}m"
                            elif eta_sec >= 60:
                                eta_str = f"{eta_sec//60}m{eta_sec%60}s"
                            else:
                                eta_str = f"{eta_sec}s"
                            eta_txt = f"{done}/{total}  ETA {eta_str}"
                        else:
                            eta_txt = f"{done}/{total}"
                        self.after(0, lambda f=frac: self.progress_bar.set(f))
                        self.after(0, lambda t=eta_txt: self.eta_label.configure(text=t))
                        # Log file vừa xong
                        if current_file:
                            fname = os.path.basename(current_file)
                            success += 1
                            self.after(0, lambda p=done, t=total, n=fname:
                                       self._log(f"[{p}/{t}] ✅ {n}"))
                            current_file = ""

                    # Lấy tên file đang transfer (dòng không có số bytes)
                    for line in buf.split("\n"):
                        line = line.strip()
                        if (line and not _re.search(r'[\d,]+ +\d+%', line)
                                and not line.startswith("sending")
                                and not line.startswith("sent ")
                                and not line.startswith("total ")
                                and "to-chk" not in line
                                and "/" in line):
                            current_file = line

                    buf = buf.split("\n")[-1]  # giữ lại dòng chưa hoàn chỉnh

                proc.wait()
                elapsed_total = int(_time.time() - start_time)
                elapsed_str = (f"{elapsed_total//60}m{elapsed_total%60}s"
                               if elapsed_total >= 60 else f"{elapsed_total}s")
                if proc.returncode == 0:
                    self.after(0, lambda: self.progress_bar.set(1))
                    self.after(0, lambda: self.eta_label.configure(text="✅ Xong!"))
                    self.after(0, lambda: self._status("✅ Xong!"))
                    self.after(0, lambda s=success, t=total_files, e=elapsed_str:
                               self._log(f"\n🏁 Xong: {s}/{t} file — {e}"))
                else:
                    self.after(0, lambda: self.eta_label.configure(text="❌ Thất bại"))
                    self.after(0, lambda: self._status("❌ Thất bại!"))
                    self.after(0, lambda: self._log("❌ Thất bại!"))
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ Exception: {e}"))
                self.after(0, lambda: self._status(f"Lỗi: {e}"))
            finally:
                self.after(0, self._finish_send)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_send(self):
        self.is_running = False
        self._lock_ui(False)
        self.btn_send.configure(text="GỬI FILE", fg_color=BLUE, state="normal")

if __name__ == "__main__":
    app = SenderApp()
    app.mainloop()
