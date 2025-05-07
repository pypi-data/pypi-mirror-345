# __init__.py
import logging
# 设置日志级别
logging.basicConfig(level=logging.ERROR)

import argparse
import yaml
import os

from .common import app
from . import tools
from .review_classifier import create_default_config
from . import select_column
from . import analyze_reviews


def main():
    """
    主函数，处理命令行参数并运行应用
    
    参数:
        --api-key: API密钥
        --base-url: API基础URL
        --model: 使用的模型名称
        --config: 配置文件路径
    """
    parser = argparse.ArgumentParser(description="手机商品评论智能分析工具")
    parser.add_argument("--api-key", required=True, help="OpenAI API密钥")
    parser.add_argument("--base-url", required=True, help="API基础URL")
    parser.add_argument("--model", required=True, help="使用的模型名称")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 检查参数完整性
    if not all([args.api_key, args.base_url, args.model]):
        parser.error("必须提供api-key、base-url和model参数")
    
    # 检查配置文件是否存在，不存在则创建
    if not os.path.exists(args.config):
        print(f"配置文件不存在，创建默认配置文件: {args.config}")
        try:
            create_default_config(args.config)
        except Exception as e:
            raise Exception(f"创建默认配置文件失败: {e}")
    
    # 更新配置
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 更新关键配置
        config.update({
            "api_key": args.api_key,
            "base_url": args.base_url,
            "model": args.model
        })
        
        # 保存更新后的配置
        with open(args.config, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
        print(f"配置已更新并保存到 {args.config}")
    except Exception as e:
        raise Exception(f"更新配置文件失败: {e}")
    
    app.run(transport='stdio')

if __name__ == "__main__":
    main()
