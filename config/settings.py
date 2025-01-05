import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = os.path.join(BASE_DIR, 'data')
CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
MODELS_CACHE_DIR = os.path.join(BASE_DIR, 'models_cache')

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///recommendation.db')

# 模型配置
MODEL_CONFIG = {
    'name': 'hfl/chinese-roberta-wwm-ext',
    'max_length': 512,
    'batch_size': 32,
    'cache_dir': MODELS_CACHE_DIR
}

# 数据文件配置
DATA_FILES = {
    'academic': os.path.join(DATA_DIR, 'academic_papers.json'),
    'conference': os.path.join(DATA_DIR, 'conference.json'),
    'douban': os.path.join(DATA_DIR, 'douban_topics.json'),
    'news': os.path.join(DATA_DIR, 'news_results.json'),
    'weibo': os.path.join(DATA_DIR, 'weibo_data.json'),
    'white_paper': os.path.join(DATA_DIR, 'white_paper.json')
}

# 推荐系统配置
RECOMMENDATION_CONFIG = {
    'content_weight': 0.6,
    'collaborative_weight': 0.4,
    'min_results': 1,
    'max_results': 20,
    'default_results': 5
}

# 内容类型描述
CONTENT_TYPES = {
    'academic': '学术论文',
    'conference': '学术会议',
    'douban': '豆瓣话题',
    'news': '新闻资讯',
    'weibo': '微博内容',
    'white_paper': '白皮书'
}

# API配置
API_CONFIG = {
    'title': '智能推荐系统 API',
    'description': '''
    基于中文 RoBERTa 和 Chroma 向量数据库的智能推荐系统。
    
    特点：
    - 使用中文 RoBERTa 模型进行文本嵌入
    - Chroma 向量数据库支持高效相似度搜索
    - 支持 6 种不同类型的内容推荐
    - 自动去重和增量更新
    ''',
    'version': '1.0',
    'doc_url': '/apidocs'
}

# Chroma配置
CHROMA_CONFIG = {
    'CHROMA_HOST': "124.222.113.16",  # 移除 http:// 前缀
    'CHROMA_PORT': 8000,              # 改为数字类型
    'CHROMA_KEY': "HgNJZah5697K2JByYWxE4sBzEp0I9Z2Xi2xf0ynagm0=",
    'CHROMA_TENANT': "zhihuiyuyan",
    'CHROMA_DATABASE': "default",
    'CHROMA_COLLECTION_NAME': "recommendation_store"
} 