# 智能推荐系统

基于中文 RoBERTa 和 Chroma 向量数据库的智能推荐系统，专注于语言文字研究领域的个性化内容推荐。

## 项目简介

本项目是一个专门面向语言文字研究领域的智能推荐系统，通过结合深度学习和向量检索技术，为用户提供个性化的内容推荐。系统支持学术论文、会议信息、研究讨论、行业新闻和研究报告等多种类型的内容推荐。

## 功能特点

### 1. 多样化内容推荐
- **学术论文**：语言学研究论文、计算语言学论文等
- **学术会议**：语言学会议、研讨会信息
- **研究讨论**：语言研究相关话题讨论
- **行业新闻**：语言政策、研究动态
- **研究报告**：语言服务行业报告、白皮书

### 2. 智能推荐算法
- 基于 RoBERTa 的语义理解
- 混合推荐策略（协同过滤 + 基于内容的推荐）
- 实时用户行为分析
- 个性化推荐结果

### 3. 高效检索系统
- Chroma 向量数据库支持
- 高效的相似度搜索
- 实时内容更新
- 自动去重功能

## 技术架构

### 1. 后端框架
- Flask + Flask-RESTX
- Swagger UI 接口文档

### 2. 数据存储
- SQLite（用户行为数据）
- Chroma（向量数据库）

### 3. AI 模型
- 中文 RoBERTa 预训练模型
- PyTorch 深度学习框架

### 4. 开发语言
- Python 3.8+

## 项目结构

```
recommendation-system/
├── app/                    # 应用主目录
│   ├── api/               # API 接口
│   │   └── routes.py      # 路由定义
│   ├── models/            # 数据模型
│   │   └── user_behavior.py
│   └── services/          # 业务服务
│       ├── database_service.py
│       ├── recommendation_service.py
│       └── chroma_service.py
├── config/                # 配置文件
│   └── settings.py        # 系统配置
├── utils/                 # 工具函数
│   └── embeddings.py      # 向量嵌入
├── data/                  # 数据文件
│   ├── academic_papers.json
│   ├── conference.json
│   ├── douban_topics.json
│   ├── news_results.json
│   └── white_paper.json
├── requirements.txt       # 依赖包
├── run.py                # 启动文件
└── README.md             # 项目文档
```

## 环境要求

- Python 3.8+
- PyTorch 1.8+
- CUDA（可选，用于 GPU 加速）

## 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/recommendation-system.git
cd recommendation-system
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
创建 `.env` 文件：
```
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///recommendation.db
```

## 运行说明

1. **启动服务**
```bash
python run.py
```

2. **访问接口**
- API 服务：http://localhost:5000
- Swagger 文档：http://localhost:5000/docs

## API 接口

### 1. 获取推荐内容
- **端点**：`GET /api/recommend`
- **参数**：
  - `user_id`: 用户ID（必需）
  - `recommend_type`: 推荐类型（必需）
  - `limit`: 返回结果数量（可选）
- **示例**：
```bash
curl -X GET "http://localhost:5000/api/recommend?user_id=1&recommend_type=academic&limit=5"
```

### 2. 记录用户行为
- **端点**：`POST /api/behavior`
- **参数**：
  ```json
  {
    "user_id": "用户ID",
    "item_id": "内容ID",
    "action": "行为类型",
    "description": "行为描述",
    "source": "来源"
  }
  ```
- **示例**：
```bash
curl -X POST "http://localhost:5000/api/behavior" \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "1",
           "item_id": "academic_001",
           "action": "view",
           "description": "浏览了论文《汉语方言语音特征的计算机识别研究》",
           "source": "web"
         }'
```

## 数据格式

### 1. 学术论文 (academic_papers.json)
```json
{
    "id": "论文ID",
    "title": "论文标题",
    "abstract": "论文摘要",
    "keywords": ["关键词1", "关键词2"],
    "authors": ["作者1", "作者2"],
    "publication": "发表期刊/会议",
    "year": "发表年份"
}
```

### 2. 研究报告 (white_paper.json)
```json
{
    "id": "报告ID",
    "title": "报告标题",
    "abstract": "报告摘要",
    "content": "报告内容",
    "publish_date": "发布日期",
    "publisher": "发布机构"
}
```

## 更新日志

### v1.0.0 (2024-01-05)
- 初始版本发布
- 实现基础推荐功能
- 支持用户行为跟踪
- 集成 Swagger UI 文档