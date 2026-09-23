import os
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import traceback
import webbrowser

URL_HOME = "https://www.bilibili.com/video/BV1C1aF6WERv"     # 视频演示链接
URL_HELP = "https://github.com/e-CNY/lm_tool_-collection/blob/main/README.md"     # 使用说明链接

# ========== 全局链接打开函数==========
def open_home(event):
    webbrowser.open(URL_HOME)

def open_help(event):
    webbrowser.open(URL_HELP)

# ========== 浏览文件夹通用函数 ==========
def browse_folder(entry_widget):
    path = filedialog.askdirectory(title="选择文件夹")
    if path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)

# ===================== 【标签页1：LM主目录指针工具】=====================
def get_user_home():
    r"""获取当前用户目录 C:\Users\用户名"""
    return os.path.expanduser("~")

POINTER_FILENAME = ".lmstudio-home-pointer"
POINTER_PATH = os.path.join(get_user_home(), POINTER_FILENAME)

def on_save_pointer(entry_path, status_var):
    target_path = entry_path.get().strip()
    if not target_path:
        messagebox.showerror("错误", "路径不能为空！")
        return
    target_path = os.path.normpath(target_path)
    try:
        with open(POINTER_PATH, "w", encoding="utf-8") as f:
            f.write(target_path)
        messagebox.showinfo("成功", f"指针文件已生成\n{POINTER_PATH}\n内容：{target_path}")
    except PermissionError:
        messagebox.showerror("权限失败", "没有权限写入用户目录！")
    except Exception as e:
        messagebox.showerror("异常", f"写入失败：{str(e)}")
    # 更新状态
    if os.path.exists(POINTER_PATH):
        status_var.set(f"当前：已存在 {POINTER_FILENAME}")
    else:
        status_var.set(f"当前：无 {POINTER_FILENAME}，LM使用默认路径")

def on_remove_pointer(status_var):
    if os.path.exists(POINTER_PATH):
        try:
            os.remove(POINTER_PATH)
            messagebox.showinfo("成功", "已删除指针，LM恢复默认路径")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")
    else:
        messagebox.showinfo("提示", "指针文件不存在")
    # 更新状态
    if os.path.exists(POINTER_PATH):
        status_var.set(f"当前：已存在 {POINTER_FILENAME}")
    else:
        status_var.set(f"当前：无 {POINTER_FILENAME}，LM使用默认路径")

def create_tab_pointer(parent):
    frame = ttk.Frame(parent, padding=10)

    ttk.Label(frame, text="LMStudio自定义存储根目录：").pack(pady=6)
    frame_path = ttk.Frame(frame)
    frame_path.pack(pady=2, fill="x")

    entry_path = ttk.Entry(frame_path)
    entry_path.pack(side=tk.LEFT, fill="x", expand=True)
    entry_path.insert(0, r"D:\Data")
    ttk.Button(frame_path, text="浏览", command=lambda: browse_folder(entry_path)).pack(side=tk.LEFT, padx=5)

    frame_btn = ttk.Frame(frame)
    frame_btn.pack(pady=12)
    status_var = tk.StringVar()
    if os.path.exists(POINTER_PATH):
        status_var.set(f"当前：已存在 {POINTER_FILENAME}")
    else:
        status_var.set(f"当前：无 {POINTER_FILENAME}，LM使用默认路径")

    ttk.Button(frame_btn, text="生成指针文件", command=lambda: on_save_pointer(entry_path, status_var)).grid(row=0, column=0, padx=6)
    ttk.Button(frame_btn, text="删除指针文件", command=lambda: on_remove_pointer(status_var)).grid(row=0, column=1, padx=6)
    ttk.Label(frame, textvariable=status_var).pack()
    return frame

# ===================== 【标签页2：Skills目录联接工具】=====================
def get_c_link():
    return os.path.join(os.path.expanduser("~"), ".lmstudio", "skills")

def log(log_box, msg):
    log_box.insert(tk.END, msg+"\n")
    log_box.see(tk.END)

def create_junction(entry_d, log_box):
    C_LINK = get_c_link()
    D_TARGET = entry_d.get().strip()
    if not D_TARGET:
        log(log_box, "❌ 请填写目标路径！")
        return
    log(log_box, f"\n===== 创建联接 =====")
    log(log_box, f"联接位置：{C_LINK}")
    log(log_box, f"真实目录：{D_TARGET}")
    # 删除旧链接
    if os.path.exists(C_LINK):
        cmd = f'rmdir /s /q "{C_LINK}"'
        log(log_box, f"执行：{cmd}")
        subprocess.run(cmd, shell=True)
    else:
        log(log_box, "C盘skills不存在，跳过删除")
    # 创建D文件夹
    if not os.path.exists(D_TARGET):
        cmd_mk = f'mkdir "{D_TARGET}"'
        log(log_box, f"执行：{cmd_mk}")
        subprocess.run(cmd_mk, shell=True)
    else:
        log(log_box, "目标目录已存在")
    # 创建Junction
    cmd_link = f'mklink /J "{C_LINK}" "{D_TARGET}"'
    log(log_box, f"执行：{cmd_link}")
    res = subprocess.run(cmd_link, shell=True, capture_output=True, text=True)
    log(log_box, f"stdout: {res.stdout}")
    log(log_box, f"stderr: {res.stderr}")
    if res.returncode ==0:
        log(log_box, "✅ 目录联接创建成功！")
    else:
        log(log_box, f"❌ 创建失败，错误码:{res.returncode}")

def del_junction(log_box):
    C_LINK = get_c_link()
    log(log_box, f"\n===== 删除联接 =====")
    log(log_box, f"联接位置：{C_LINK}")
    if os.path.exists(C_LINK):
        cmd = f'rmdir /s /q "{C_LINK}"'
        log(log_box, f"执行：{cmd}")
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        log(log_box, f"stdout:{res.stdout}")
        log(log_box, f"stderr:{res.stderr}")
        if res.returncode ==0:
            log(log_box, "✅ 联接删除成功（文件保留！）")
        else:
            log(log_box, f"❌ 删除失败，错误码:{res.returncode}")
    else:
        log(log_box, "⚠️ 该联接不存在")

def create_tab_junction(parent):
    frame = ttk.Frame(parent, padding=10)
    frame_top = ttk.Frame(frame)
    frame_top.pack(pady=8,fill="x")
    ttk.Label(frame_top,text="目标目录：").pack(side=tk.LEFT)
    entry_d = ttk.Entry(frame_top)
    entry_d.pack(side=tk.LEFT,padx=6,fill="x",expand=True)
    ttk.Button(frame_top, text="浏览", command=lambda: browse_folder(entry_d)).pack(side=tk.LEFT, padx=4)
    entry_d.insert(0,r"D:\Data\skills")

    frame_btn = ttk.Frame(frame)
    frame_btn.pack(pady=6)
    log_box = scrolledtext.ScrolledText(frame,height=12)
    ttk.Button(frame_btn,text="生成目录联接",command=lambda: create_junction(entry_d, log_box)).grid(row=0,column=0,padx=10)
    ttk.Button(frame_btn,text="删除目录联接",command=lambda: del_junction(log_box)).grid(row=0,column=1,padx=10)
    ttk.Label(frame,text="运行日志：").pack()
    log_box.pack(fill="both",expand=True)
    return frame

# ===================== 主窗口入口 =====================
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("LM Studio 迁移工具合集")
        root.geometry("720x480")

        # 标签页容器
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both", padx=8, pady=8)

        tab1 = create_tab_pointer(notebook)
        tab2 = create_tab_junction(notebook)
        notebook.add(tab1, text="主目录指针设置")
        notebook.add(tab2, text="Skills目录联接")

        # ========== 全局底部链接（只保留一组！）==========
        frame_bottom = ttk.Frame(root)
        frame_bottom.pack(pady=4, padx=10, fill="x")
        link_home = ttk.Label(frame_bottom, text="视频演示", foreground="blue", cursor="hand2")
        link_home.pack(side=tk.LEFT)
        link_home.bind("<Button-1>", open_home)
        link_help = ttk.Label(frame_bottom, text="使用说明", foreground="blue", cursor="hand2")
        link_help.pack(side=tk.RIGHT)
        link_help.bind("<Button-1>", open_help)

        root.mainloop()
    except Exception:
        err_info = traceback.format_exc()
        tk.messagebox.showerror("程序崩溃", err_info)
