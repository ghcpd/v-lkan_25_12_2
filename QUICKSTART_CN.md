# 快速开始指南 (Quick Start Guide)

## 环境已配置完成 ✓

虚拟环境已创建并安装所有依赖项。

## 使用方法

### 1. 激活虚拟环境

```cmd
venv\Scripts\activate.bat
```

### 2. 运行系统

#### 处理完整数据集
```cmd
python main.py --input tickets_label.jsonl --output output/results.jsonl --verbose
```

#### 仅提取冲突样本
```cmd
python main.py --input tickets_label.jsonl --output output/conflicts_only.jsonl --conflicts-only --verbose
```

#### 生成详细报告
```cmd
python main.py --input tickets_label.jsonl --output output/results.jsonl --report output/report.md --verbose
```

### 3. 查看帮助
```cmd
python main.py --help
```

### 4. 运行测试
```cmd
python test_conflict_detector.py
```

或使用 pytest:
```cmd
python -m pytest test_conflict_detector.py -v
```

## 输出文件

处理完成后，会在 `output/` 目录下生成：

1. **conflict_analysis_results.jsonl** - 完整分析结果（所有样本）
2. **conflicts_only.jsonl** - 仅包含冲突样本
3. **conflict_analysis_report.md** - 详细的分析报告（Markdown格式）
4. **test_report.txt** - 测试执行报告

## 当前数据集统计

- 总样本数: 50
- 冲突样本: 7 (14%)
- 无冲突样本: 43 (86%)
- 主要冲突类型: 意图分类

## 主要功能特性

✅ **冲突检测** - 自动识别标注者之间的分歧  
✅ **原因分析** - 详细解释产生分歧的根本原因  
✅ **智能解决** - 基于多数投票+上下文分析建议最终标签  
✅ **详细报告** - 生成包含统计数据和示例的完整报告  
✅ **批处理** - 高效处理大规模数据集  
✅ **全面测试** - 21项自动化测试，100%通过率  

## 文件说明

- `conflict_detector.py` - 核心冲突检测逻辑
- `config.py` - 配置设置
- `utils.py` - 工具函数和报告生成器
- `main.py` - 命令行应用程序
- `test_conflict_detector.py` - 综合测试套件
- `requirements.txt` - Python依赖项
- `Dockerfile` - Docker配置
- `setup.sh` / `setup.bat` - 环境设置脚本

## 示例输出

### 冲突样本示例
```json
{
  "id": "TICK-0026",
  "text": "I want a refund but the app says payment failed.",
  "labels": [
    {"annotator": "ann_01", "label": "billing_issue|high"},
    {"annotator": "ann_02", "label": "bug_report|medium"},
    {"annotator": "ann_03", "label": "billing_issue|high"}
  ],
  "is_conflict": true,
  "conflict_reason": "Ambiguous text: Contains terms like 'payment failed'...",
  "suggested_label": "billing_issue|high"
}
```

## 下一步建议

1. 查看生成的报告: `output/conflict_analysis_report.md`
2. 审查冲突样本: `output/conflicts_only.jsonl`
3. 根据分析结果更新标注指南
4. 对高冲突样本进行重新标注

## 需要帮助？

运行 `python main.py --help` 查看所有可用选项。

---

**版本**: 1.0.0  
**创建日期**: 2025-12-02  
**测试状态**: ✅ 21/21 通过
