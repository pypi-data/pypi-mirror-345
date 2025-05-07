# Choumine 手机评论智能分析工具

[English Version Below]

## 功能特性
- 基于OpenAI API的智能评论分析
- 支持CSV/TXT格式输入
- 可配置的自定义分析问题
- 批量处理与自动重试机制
- 结果统计与可视化输出
- 自动生成配置文件模板

## 安装要求
```bash
Python 3.10+  
pip install -r requirements.txt
```

## 快速开始
```bash
# 生成默认配置文件
python -m choumine_review_classifier.review-classifier --create-config

# 分析评论文件  
python -m choumine_review_classifier.review-classifier -i reviews.csv
```

## 配置文件说明
编辑`config.yaml`：
```yaml
api_key: "your-openai-key"
model: "gpt-4o"
custom_questions:
  - id: "positive"
    question: "评论情感是否为正面？"
  - id: "recommend"
    question: "是否推荐购买？"
```

## 注意事项
1. 确保网络可访问OpenAI API
2. 大规模分析建议设置`batch_size: 20-50`
3. 结果文件包含原始回答和解析后的独立列
4. 临时文件`.temp`可中断续传

---

# Choumine Mobile Review Analyzer

## Features
- OpenAI API powered analysis
- CSV/TXT input support
- Customizable questions
- Batch processing with auto-retry
- Statistical visualization
- Config template generation

## Requirements
```bash
Python 3.10+
pip install -r requirements.txt
```

## Quick Start
```bash
# Generate config template
python -m choumine_review_classifier.review-classifier --create-config

# Analyze reviews
python -m choumine_review_classifier.review-classifier -i reviews.csv
```

## Configuration
Edit `config.yaml`:
```yaml
api_key: "your-openai-key"
model: "gpt-4o"
custom_questions:
  - id: "positive"
    question: "Is the review sentiment positive?"
  - id: "recommend"
    question: "Would you recommend this product?"
```

## Best Practices
1. Verify API connectivity
2. Optimal `batch_size: 20-50`
3. Results include raw JSON and parsed columns
4. `.temp` files allow resume interrupted jobs