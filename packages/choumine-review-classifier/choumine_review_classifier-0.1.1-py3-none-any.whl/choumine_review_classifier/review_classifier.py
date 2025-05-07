import os
import json
import time

import pandas as pd
import argparse
from typing import List, Dict, Any
import openai
import yaml

from .common import app

class ReviewAnalyzer:
    """手机评论智能问题分析器"""
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.client = openai.OpenAI(
            api_key=self.config["api_key"],
            base_url=self.config.get("base_url", "https://api.openai.com/v1")
        )
        
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            # 返回默认配置
            return {
                "api_key": "YOUR_API_KEY",
                "model": "gpt-4o",
                "base_url": "https://api.openai.com/v1",  # 新增默认值
                "custom_questions": [
                    {
                        "id": "positive",
                        "question": "这条评论的情感是否为正面?"
                    },
                    {
                        "id": "recommend",
                        "question": "用户是否推荐购买这款手机?"
                    }
                ],
                "batch_size": 10,
                "max_tokens": 1000,
                "temperature": 0
            }
    
    def analyze_reviews(self, reviews: List[str], output_path: str = "results.csv") -> pd.DataFrame:
        """
        对评论进行分析
        
        Args:
            reviews: 评论列表
            output_path: 输出文件路径
            
        Returns:
            带有分析结果的DataFrame
        """
        results = []
        total = len(reviews)
        
        # 批量处理以提高效率
        for i in range(0, total, self.config["batch_size"]):
            batch = reviews[i:i+self.config["batch_size"]]
            print(f"处理批次 {i//self.config['batch_size']+1}/{(total-1)//self.config['batch_size']+1} ({len(batch)}条评论)")
            
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # 保存中间结果
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(f"{output_path}.temp", index=False, encoding='utf-8')
            
            # 避免API限速，添加延迟
            if i + self.config["batch_size"] < total:
                time.sleep(1)
        
        # 将结果保存为CSV
        df = pd.DataFrame(results)
        
        # 处理自定义问题答案，拆分成单独的列
        if 'answers' in df.columns:
            # 提取所有自定义问题的答案
            custom_questions = self.config.get("custom_questions", [])
            
            for question in custom_questions:
                question_id = question['id']
                # 创建新列来存储每个问题的答案
                df[f"q_{question_id}"] = df['answers'].apply(
                    lambda x: x.get(question_id, "未回答") if isinstance(x, dict) else "解析错误"
                )
            
            # 可以选择是否删除原始的answers列
            # df = df.drop('answers', axis=1)
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"结果已保存至 {output_path}")
        
        return df
    
    def _process_batch(self, reviews: List[str]) -> List[Dict[str, Any]]:
        """处理一批评论"""
        results = []
        
        for review in reviews:
            try:
                result = self._analyze_single_review(review)
                results.append(result)
            except Exception as e:
                print(f"处理评论时出错: {e}")
                # 添加错误记录，保证数据条数一致
                results.append({
                    "review": review,
                    "answers": {},
                    "error": str(e)
                })
                
        return results
    
    def _analyze_single_review(self, review: str) -> Dict[str, Any]:
        """
        对单条评论进行分析并回答自定义问题
        
        Args:
            review: 评论内容
            
        Returns:
            分析结果字典，包含对各问题的回答
        """
        # 获取自定义问题列表
        custom_questions = self.config.get("custom_questions", [])
        
        if not custom_questions:
            return {
                "review": review,
                "answers": {},
                "error": "配置中没有定义任何问题"
            }
        
        # 构建问题字符串
        questions_str = "\n".join([f"{i+1}. {question['question']}" for i, question in enumerate(custom_questions)])
        
        prompt = f"""
        请分析下面这条手机商品评论，并回答以下问题：

        评论内容: "{review}"

        问题列表:
        {questions_str}

        返回格式(JSON): {{
            "answers": {{
                {', '.join([f'"{q["id"]}": "对问题的回答（是/否/不确定）以及简短解释"' for q in custom_questions])}
            }}
        }}

        请只返回JSON格式结果，不要包含其他文字。对于每个问题，请首先明确回答"是"、"否"或"不确定"，然后给出简短解释。
        """

        # 调用OpenAI API
        response = self.client.chat.completions.create(
            model=self.config["model"],
            max_tokens=self.config["max_tokens"],
            temperature=self.config["temperature"],
            messages=[
                {"role": "system", "content": "你是一个专业的手机评论分析助手，只返回JSON格式的分析结果。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}  # 指定返回JSON格式
        )
        
        # 解析响应
        try:
            # 提取API返回的内容
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            result = json.loads(content)
            
            # 添加原始评论
            result["review"] = review
            return result
        except Exception as e:
            print(f"解析响应失败: {e}")
            print(f"原始响应: {response}")
            return {
                "review": review,
                "answers": {},
                "error": f"无法解析API响应: {str(e)}"
            }

@app.tool()
def select_csv_file() -> str:
    """
    弹出文件选择对话框让用户选择CSV文件
    
    Returns:
        str: 用户选择的CSV文件路径，如果取消选择则返回空字符串
    """
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 设置窗口置顶
    
    file_path = filedialog.askopenfilename(
        title="选择CSV文件",
        filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
    )
    
    return file_path

@app.tool()
def edit_custom_questions(config_path: str = "config.yaml") -> bool:
    """
    弹出多行文本框供用户输入自定义问题并更新配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        bool: 修改是否成功
    """
    import tkinter as tk
    from tkinter import scrolledtext
    
    try:
        # 加载当前配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 获取当前问题列表
        current_questions = config.get("custom_questions", [])
        current_text = "\n".join([q["question"] for q in current_questions])
        
        # 创建GUI窗口
        root = tk.Tk()
        root.title("编辑自定义问题")
        root.attributes('-topmost', True)
        
        # 添加说明标签
        label = tk.Label(root, text="每行输入一个问题:")
        label.pack(pady=5)
        
        # 添加多行文本框
        text_area = scrolledtext.ScrolledText(root, width=50, height=10)
        text_area.insert(tk.INSERT, current_text)
        text_area.pack(pady=5)
        
        # 添加确定按钮
        result = False
        
        def on_confirm():
            nonlocal result
            # 获取用户输入
            questions_text = text_area.get("1.0", tk.END).strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            if not questions:
                tk.messagebox.showerror("错误", "至少需要输入一个问题！")
                return
                
            # 更新配置
            config["custom_questions"] = [
                {"id": f"q_{i+1}", "question": q} 
                for i, q in enumerate(questions)
            ]
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
                
            result = True
            root.destroy()
            
        button = tk.Button(root, text="确定", command=on_confirm)
        button.pack(pady=5)
        
        root.mainloop()
        return result
        
    except Exception as e:
        print(f"修改配置文件失败: {e}")
        return False

def load_reviews_from_txt(file_path: str) -> List[str]:
    """从TXT文件加载评论，每行一条"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"加载TXT文件失败: {e}")
        return []

def create_default_config(file_path: str = "config.yaml"):
    """创建默认配置文件"""
    default_config = {
        "api_key": "YOUR_API_KEY_HERE",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "custom_questions": [
            {
                "id": "positive",
                "question": "这条评论的情感是否为正面?"
            },
            {
                "id": "recommend",
                "question": "用户是否推荐购买这款手机?"
            },
            {
                "id": "feature_mention",
                "question": "评论是否提到了手机的具体功能或特点?"
            }
        ],
        "batch_size": 10,  # 每批处理的评论数
        "max_tokens": 1000,  # API响应的最大令牌数
        "temperature": 0  # 确定性输出
    }
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        print(f"默认配置文件已创建: {file_path}")
    except Exception as e:
        print(f"创建配置文件失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="手机商品评论智能分析工具")
    parser.add_argument("--input", "-i", required=False, help="输入文件路径 (CSV或TXT)")  # 修改required为False
    parser.add_argument("--output", "-o", default="results.csv", help="输出文件路径")
    parser.add_argument("--config", "-c", default="config.yaml", help="配置文件路径")
    parser.add_argument("--column", default="review", help="CSV文件中评论所在的列名")
    parser.add_argument("--create-config", action="store_true", help="创建默认配置文件")
    
    args = parser.parse_args()
    
    # 创建默认配置文件
    if args.create_config:
        create_default_config(args.config)
        return
    
    # 新增参数校验
    if not args.input:
        parser.error("正常使用时必须提供 --input 参数")
    
    # 检查配置文件是否存在，如果不存在则创建
    if not os.path.exists(args.config):
        print(f"配置文件不存在，创建默认配置文件: {args.config}")
        create_default_config(args.config)
    
    # 加载评论
    if args.input.endswith('.csv'):
        # reviews = load_reviews_from_csv(args.input, args.column)
        reviews = []
    elif args.input.endswith('.txt'):
        reviews = load_reviews_from_txt(args.input)
    else:
        print("不支持的文件格式，请提供CSV或TXT文件")
        return
    
    if not reviews:
        print("没有评论可处理或文件加载失败")
        return
        
    print(f"成功加载 {len(reviews)} 条评论")
    
    # 分析评论
    analyzer = ReviewAnalyzer(args.config)
    
    # 打印自定义问题信息
    custom_questions = analyzer.config.get("custom_questions", [])
    if custom_questions:
        print(f"\n检测到 {len(custom_questions)} 个自定义问题:")
        for q in custom_questions:
            print(f"- {q['question']} (ID: {q['id']})")
    else:
        print("\n警告: 配置中未定义任何问题！")
        return
    
    results_df = analyzer.analyze_reviews(reviews, args.output)
    
    # 显示问题回答统计
    custom_question_cols = [col for col in results_df.columns if col.startswith('q_')]
    if custom_question_cols:
        print("\n问题回答统计:")
        for col in custom_question_cols:
            question_id = col[2:]  # 移除 'q_' 前缀
            # 查找对应的问题文本
            question_text = next((q['question'] for q in custom_questions if q['id'] == question_id), question_id)
            
            # 计算"是"回答的比例
            yes_count = sum(1 for answer in results_df[col] if isinstance(answer, str) and answer.lower().startswith(("是", "yes")))
            yes_percentage = yes_count / len(results_df) * 100
            
            print(f"- {question_text}: {yes_count}/{len(results_df)} 条评论为\"是\" ({yes_percentage:.1f}%)")

if __name__ == "__main__":
    main()