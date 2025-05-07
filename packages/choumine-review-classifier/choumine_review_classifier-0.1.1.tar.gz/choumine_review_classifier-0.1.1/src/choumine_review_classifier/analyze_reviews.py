import pandas as pd

from .review_classifier import ReviewAnalyzer
from .terminal_monitor import show_terminal_window
from .common import app


def analyze_reviews_cli(csv_path: str, column_name: str, output_path: str = "", config_path: str = "config.yaml") -> pd.DataFrame:
    """
    从CSV文件加载评论并进行分析
    执行该函数前，先执行edit_custom_questions()函数更新自定义问题
    Args:
        csv_path: CSV文件路径
        column_name: 包含评论的列名
        output_path: 输出文件路径
        config_path: 配置文件路径
        
    Returns:
        带有分析结果的DataFrame
    """
    # 如果output_path为空，弹出文件保存对话框
    if not output_path:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        output_path = filedialog.asksaveasfilename(
            title="选择保存分析结果的文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialfile="results.csv"
        )
        
        if not output_path:
            print("用户取消了文件选择")
            return pd.DataFrame()
    
    analyzer = ReviewAnalyzer(config_path)
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        if column_name not in df.columns:
            raise ValueError(f"CSV文件中不存在列 '{column_name}'")
            
        reviews = df[column_name].tolist()
        return analyzer.analyze_reviews(reviews, output_path)
        
    except Exception as e:
        print(f"加载或分析CSV文件失败: {e}")
        return pd.DataFrame()

@app.tool()
def analyze_reviews(csv_path: str, column_name: str, output_path: str = "", config_path: str = "config.yaml"):
    """
    通过终端窗口执行评论分析的工具函数
    
    Args:
        csv_path: 包含评论数据的CSV文件路径
        column_name: CSV文件中包含评论内容的列名
        output_path: 可选参数，分析结果输出文件路径。如果为空，会弹出文件保存对话框
        config_path: 可选参数，配置文件路径，默认为config.yaml
        
    功能说明:
    - 调用show_terminal_window函数在终端窗口中执行analyze_reviews_cli
    - 提供用户友好的终端界面来监控分析进度
    - 支持通过配置文件自定义分析参数
    """
    show_terminal_window(analyze_reviews_cli, csv_path, column_name, output_path, config_path)

if __name__ == "__main__":
    analyze_reviews('reviews.csv', 'review')