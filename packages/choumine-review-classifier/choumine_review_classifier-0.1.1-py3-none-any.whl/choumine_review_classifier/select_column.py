import pandas as pd
from .common import app

@app.tool()
def select_review_column_from_csv(file_path: str, column_name: str = "") -> str:
    """
    从CSV文件加载评论数据并选择评论列
    
    功能说明:
    - 从指定的CSV文件中读取评论数据
    - 如果未指定列名，会弹出GUI窗口让用户选择包含评论的列
    - 支持自动检测文件编码(utf-8)
    - 包含完整的GUI列选择流程
    
    参数:
    - file_path: CSV文件路径
    - column_name: 可选参数，指定包含评论的列名。如果为空，会弹出GUI选择窗口
    
    返回值:
    - str: 用户选择或指定的列名
    
    异常处理:
    - 如果文件不存在或格式错误，会打印错误信息并返回空字符串
    - 如果指定列不存在，会抛出ValueError异常
    - 如果用户取消选择，会返回空字符串
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 如果没有指定列名，弹出选择窗口
        if column_name == "":
            import tkinter as tk
            from tkinter import ttk
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # 创建选择窗口
            select_window = tk.Toplevel(root)
            select_window.title("选择评论列")
            select_window.attributes('-topmost', True)
            select_window.overrideredirect(True)
            
            # 计算窗口居中位置
            window_width = 300
            window_height = 150
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            select_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # 添加标签
            label = tk.Label(select_window, text="请选择包含评论的列:")
            label.pack(pady=10)
            
            # 添加下拉框
            combo = ttk.Combobox(select_window, values=list(df.columns), state='readonly')
            combo.set(df.columns[0])  # 默认选择第一个列名
            combo.pack(pady=5)
            
            # 添加确定按钮
            selected_column = None
            
            def on_select():
                nonlocal selected_column
                selected_column = combo.get()
                select_window.destroy()
                root.destroy()
            
            button = tk.Button(select_window, text="确定", command=on_select)
            button.pack(pady=10)
            
            # 等待用户选择
            select_window.mainloop()
            
            if not selected_column:
                return ""
                
            column_name = selected_column
        
        if column_name not in df.columns:
            raise ValueError(f"CSV文件中不存在列 '{column_name}'")
        return column_name
    except Exception as e:
        print(f"加载CSV文件失败: {e}")
        return ""

if __name__ == "__main__":
    r = select_review_column_from_csv(r"D:\Users\91000873\Desktop\reviews.csv")
    print(r)