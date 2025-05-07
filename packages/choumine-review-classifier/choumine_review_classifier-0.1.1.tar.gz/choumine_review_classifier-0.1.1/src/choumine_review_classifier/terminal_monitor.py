import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import time

class TerminalMonitorGUI:
    def __init__(self, master, script_path='main.py', function=None, function_args=None, function_kwargs=None):
        self.master = master
        self.script_path = script_path
        master.title("Terminal Monitor")
        master.overrideredirect(True)
        master.attributes('-topmost', True)
        
        # 设置窗口居中
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = 500
        window_height = 400
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        master.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.NONE)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        if function:
            # 执行自定义函数
            self.execute_function(function, function_args or [], function_kwargs or {})
        else:
            # 执行脚本
            thread = threading.Thread(target=self.run_main_script)
            thread.daemon = True
            thread.start()
    
    def run_main_script(self):
        process = subprocess.Popen(['python', '-u', self.script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True, 
                                  bufsize=1)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                self.master.after(0, self.countdown, 5)
                break
            if output:
                self.master.after(0, self._append_output, output)
        
    def countdown(self, remaining):
        if remaining == 0:
            self.master.destroy()
        else:
            self.text_area.config(state=tk.NORMAL)
            self.text_area.insert(tk.END, f"{remaining} 秒后窗口自动关闭...\n")
            self.text_area.see(tk.END)
            self.text_area.config(state=tk.DISABLED)
            self.master.after(1000, self.countdown, remaining - 1)
            
    def _append_output(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
    def execute_function(self, func, args=None, kwargs=None):
        """执行自定义函数并捕获其输出"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
            
        thread = threading.Thread(target=self._run_function, args=(func, args, kwargs))
        thread.daemon = True
        thread.start()
        
    def _run_function(self, func, args, kwargs):
        # 创建自定义输出重定向类，实时捕获打印内容
        class RealTimeOutput:
            def __init__(self, callback):
                self.callback = callback
            
            def write(self, text):
                if text:  # 忽略空字符串
                    self.callback(text)
                return len(text)
            
            def flush(self):
                pass
        
        # 创建实时输出对象
        real_time_output = RealTimeOutput(lambda text: self.master.after(0, self._append_output, text))
        
        # 保存原始的stdout和stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # 重定向标准输出和标准错误到实时输出对象
            sys.stdout = real_time_output
            sys.stderr = real_time_output
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 如果函数有返回值，显示它
            if result is not None:
                self.master.after(0, self._append_output, f"\n结果: {result}\n")
                
        except Exception as e:
            self.master.after(0, self._append_output, f"错误: {str(e)}\n")
        finally:
            # 恢复原始的stdout和stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self.master.after(0, self.countdown, 5)

def show_terminal_window(function=None, *args, **kwargs):
    """显示终端监视器窗口并执行指定函数"""
    root = tk.Tk()
    app = TerminalMonitorGUI(root, function=function, function_args=args, function_kwargs=kwargs)
    root.mainloop()

# 用于测试的示例函数
def test_function():
    print("开始执行测试函数...")
    for i in range(10):
        print(f"正在处理步骤 {i+1}/10")
        time.sleep(0.5)  # 模拟耗时操作
    print("测试函数执行完毕!")
    return "执行成功"

if __name__ == "__main__":
    # import sys
    # script_path = sys.argv[1] if len(sys.argv) > 1 else 'main.py'
    # root = tk.Tk()
    # app = TerminalMonitorGUI(root, script_path)
    # root.mainloop()

    show_terminal_window(test_function)