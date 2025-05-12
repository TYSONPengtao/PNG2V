import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from create_video import create_video_from_images

class PNG2VGui:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG2V - 历史地图视频生成器")
        
        # 设置窗口大小和位置
        window_width = 700
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # 输入文件夹选择
        input_frame = ttk.LabelFrame(main_frame, text="输入配置", padding="5 5 5 5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="输入文件夹:").grid(row=0, column=0, sticky=tk.W)
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path, width=70).grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="浏览", command=self.browse_input).grid(row=0, column=2)
        
        # 输出文件选择
        output_frame = ttk.LabelFrame(main_frame, text="输出配置", padding="5 5 5 5")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W)
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=70).grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(row=0, column=2)
        
        # 状态输出区域
        status_frame = ttk.LabelFrame(main_frame, text="处理状态", padding="5 5 5 5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(2, weight=1)
        
        # 添加状态文本区域
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10)
        self.status_text.pack(fill="both", expand=True)
        
        # 进度显示
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(fill="x", expand=True)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status = ttk.Label(main_frame, textvariable=self.status_var)
        self.status.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 开始按钮
        self.start_button = ttk.Button(main_frame, text="开始生成", command=self.start_conversion)
        self.start_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 处理线程
        self.processing_thread = None
        self.is_processing = False

    def browse_input(self):
        folder = filedialog.askdirectory(title="选择输入文件夹")
        if folder:
            self.input_path.set(folder)
            # 自动设置输出文件名
            folder_name = os.path.basename(folder)
            output_dir = r"E:\历史地图"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output_path.set(os.path.join(output_dir, f"{folder_name}_video.mp4"))

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 文件", "*.mp4")],
            title="选择视频保存位置"
        )
        if path:
            self.output_path.set(path)

    def update_progress(self, value):
        """更新进度条"""
        self.progress['value'] = value
        self.root.update_idletasks()

    def update_status(self, message):
        """更新状态文本"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_var.set(message.split("\n")[0])
        self.root.update_idletasks()

    def start_conversion(self):
        if self.is_processing:
            return
        
        input_folder = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_folder or not output_path:
            messagebox.showerror("错误", "请选择输入文件夹和输出文件位置！")
            return
        
        if not os.path.exists(input_folder):
            messagebox.showerror("错误", "输入文件夹不存在！")
            return
        
        self.is_processing = True
        self.start_button.state(['disabled'])
        self.status_text.delete(1.0, tk.END)
        self.update_status("正在处理...")
        self.progress['value'] = 0
        
        def process():
            try:
                success = create_video_from_images(
                    input_folder,
                    output_path,
                    progress_callback=lambda p: self.root.after(0, self.update_progress, p),
                    status_callback=lambda m: self.root.after(0, self.update_status, m)
                )
                
                if success:
                    self.root.after(0, self.update_status, "处理完成！")
                    self.root.after(0, lambda: messagebox.showinfo("成功", f"视频已成功生成：\n{output_path}"))
                else:
                    self.root.after(0, self.update_status, "处理失败！")
            except Exception as e:
                self.root.after(0, self.update_status, f"发生错误：{str(e)}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"生成视频时出错：\n{str(e)}"))
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.start_button.state(['!disabled']))
        
        self.processing_thread = threading.Thread(target=process)
        self.processing_thread.daemon = True
        self.processing_thread.start()

def main():
    root = tk.Tk()
    # 设置应用程序图标
    try:
        root.iconbitmap("icon.ico")
    except:
        pass  # 如果图标文件不存在则忽略
    app = PNG2VGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
