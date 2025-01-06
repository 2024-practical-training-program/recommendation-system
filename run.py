from flask import Flask
from app.api.routes import recommend_bp
from app.extensions import swagger
from config.settings import API_CONFIG
from app.services.chroma_service import ChromaService
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_data():
    """初始化数据"""
    try:
        logger.info("Initializing Chroma database...")
        chroma_service = ChromaService()
        chroma_service.initialize_data()
        logger.info("Data initialization completed")
    except Exception as e:
        logger.error(f"Error initializing data: {str(e)}")
        raise

def create_app():
    """创建并配置 Flask 应用"""
    # 初始化数据
    initialize_data()
    
    app = Flask(__name__)
    
    # 注册蓝图
    app.register_blueprint(recommend_bp, url_prefix='/api/v1')
    
    # 初始化 Swagger
    swagger.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting recommendation system...")
    app.run(debug=True, port=8888,host='0.0.0.0')