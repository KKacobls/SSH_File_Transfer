
import tkinter as tk
from tkinter import filedialog

class SCP:
    def __init__(self, master):
        self.master = master
        self.vars = [tk.StringVar() for _ in range(4)]
        entries = []
        labels = []
        # 新增一個容器
        top_container = tk.Frame(master)
        top_container.pack(side="top")
        container = tk.Frame(self.master)
        container.pack()
        # 加入 Label 到容器中
        server_label = tk.Label(top_container, text="伺服器位置")
        server_label.pack(side="left")
        for i in range(4):
            entry = tk.Entry(container, width=10, validate="key", textvariable=self.vars[i])
            entry.grid(row=0, column=2*i)
            entry.bind("<KeyRelease>", self.on_entry_keyrelease)
            if i!=3:
                label = tk.Label(container, text=".")
                label.grid(row=0, column=2*i+1)
                labels.append(label)
            entries.append(entry)

        self.entries = entries
        self.labels = labels
        # 使用者帳號框
        label = tk.Label(text="帳號")
        label.pack(side="top")
        self.user_entry = tk.Entry(master)
        self.user_entry.pack(fill="both")
        


        # 使用者密碼框
        label = tk.Label(text="密碼(不支援不需要密碼的)")
        label.pack(side="top")
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack(fill="both")
        # 檔案位置
        label = tk.Label(text="檔案位置(預設傳到主機的/home/username)")
        label.pack(side="top")
        self.path_entry = tk.Entry(master, state="readonly")
        self.path_entry.pack(fill="both")

        # 檔案選擇按鈕
        select_button = tk.Button(master, text="選擇檔案", command=self.select_file)
        select_button.place(x=0, y=170, width=162, height=100)
        # 檔案傳送位置按鈕
        self.send_entry = tk.Entry(master, show="*")
        self.send_entry.place(x=0, y=270)
    def on_entry_keyrelease(self, event):
        entry = event.widget
        text = entry.get()
        if len(text) >=1 :
            if text[0]=='0':
                next_entry_index = self.entries.index(entry) + 1
                if next_entry_index < len(self.entries):
                    self.entries[next_entry_index].focus_set()
        if len(text) == 3:
            next_entry_index = self.entries.index(entry) + 1
            if next_entry_index < len(self.entries):
                self.entries[next_entry_index].focus_set()
                
    def select_file(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.path_entry.configure(state='normal')
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(tk.END, ";".join(file_paths))
            self.path_entry.configure(state='readonly')

root = tk.Tk()
root.geometry("325x290")
root.title("傳送檔案")
four_entries = SCP(root)
def get_entries_values():
    values = [var.get() for var in four_entries.vars]
    print(values)
    print("Username:", four_entries.user_entry.get())
    print("Password:", four_entries.password_entry.get())
    print("path_entry:", four_entries.path_entry.get())
    print("send_entry:", four_entries.send_entry.get())
def send_file():
    from tkinter import messagebox
    
    import os
    import paramiko
    serverid = [var.get() for var in four_entries.vars]
    if len(serverid)!=4:
        messagebox.showinfo("檔案傳輸", "伺服器位置打錯 請打四個！")
        return
    server = serverid[0] + '.'+serverid[1] + '.'+serverid[2] + '.'+serverid[3]
    if four_entries.user_entry.get():
        username = four_entries.user_entry.get()
    else:
        messagebox.showinfo("檔案傳輸", "阿你username咧")
        return
    if four_entries.password_entry.get():
        password = four_entries.password_entry.get()
    else:
        messagebox.showinfo("檔案傳輸", "密碼打一下啊老兄")
        return
    if four_entries.path_entry.get():
        localpath = four_entries.path_entry.get()
    else:
        messagebox.showinfo("檔案傳輸", "選個檔案==")
        return
    if not(os.path.isfile(four_entries.path_entry.get())):
        messagebox.showinfo("檔案傳輸", "檔案不存在(正常不會發生的吧)")
        return
    #get_entries_values()
    if four_entries.send_entry.get():
        remotepath = four_entries.path_entry.get()
    else:
        remotepath = r'/home/' + username + r'/' + os.path.basename(localpath)#操忘記加這個 差點睡不著
    #檢測server是否可連線
    import socket
    def is_valid_ip_address(ip_address):
        try:
            socket.inet_aton(ip_address)
            return True
        except socket.error:
            return False
    ip_address = server  # 請替換為您要檢查的IP地址
    if not(is_valid_ip_address(ip_address)):
        messagebox.showinfo("檔案傳輸", "尼打的ip怪怪的")
    try:
        # 建立一個TCP套接字並連接到目標IP地址的預設端口
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)  # 設置超時時間為3秒
        s.connect((ip_address, 22))  # 請替換為遠程服務器上開放的端口號，通常SSH端口號為22
    except socket.timeout:
        messagebox.showinfo("檔案傳輸", "IP address {} is not reachable".format(ip_address))
        return
    except socket.error:
        messagebox.showinfo("檔案傳輸", "IP address {} does not exist.".format(ip_address))
        return
    finally:
        s.close()  # 關閉套接字連接
    try:
        #print('server',server)
        #print('username',username)
        #print('password',password)
        #print('localpath',localpath)
        #print('remotepath',remotepath)
        ssh = paramiko.SSHClient() 
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(server, username=username, password=password)
        sftp = ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
        messagebox.showinfo("檔案傳輸", "成功！")
    except paramiko.AuthenticationException as e:
        messagebox.showinfo("檔案傳輸", "密碼或帳號錯誤！"+str(e))
    except Exception as e:
        messagebox.showinfo("檔案傳輸", "錯誤！ 訊息為"+str(e))


send_file_button = tk.Button(root, text="傳送檔案", command=send_file)
send_file_button.place(x=162, y=170, width=162, height=100)
#button = tk.Button(root, text="Get Values", command=get_entries_values)
#button.place(x=128, y=220)
label = tk.Label(root, text="By KKacobls製作")
label.place(x=222, y=270)
root.mainloop()
