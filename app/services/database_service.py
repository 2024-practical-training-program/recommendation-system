from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from app.models.user_behavior import Base, UserBehavior
from config.settings import DATABASE_URL
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """初始化数据库服务"""
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def get_user_behavior(self, user_id, limit=100):
        """获取用户行为数据
        
        Args:
            user_id: 用户ID
            limit: 返回的最大行为记录数
        """
        try:
            # 获取用户最近的行为记录
            behaviors = self.session.query(UserBehavior)\
                .filter_by(user_id=user_id)\
                .order_by(desc(UserBehavior.timestamp))\
                .limit(limit)\
                .all()
                
            if not behaviors:
                return None
                
            # 转换为用户历史记录格式
            return UserBehavior.get_user_history(behaviors)
            
        except Exception as e:
            logger.error(f"Error getting user behavior: {str(e)}")
            return None
            
    def add_user_behavior(self, user_id, item_id, action, description=None, source=None):
        """添加用户行为记录
        
        Args:
            user_id: 用户ID
            item_id: 内容ID
            action: 行为类型（如：view, like, share等）
            description: 行为描述
            source: 行为来源
        """
        try:
            behavior = UserBehavior(
                user_id=user_id,
                item_id=item_id,
                action=action,
                description=description,
                timestamp=datetime.now(),
                source=source
            )
            
            self.session.add(behavior)
            self.session.commit()
            return behavior.to_dict()
            
        except Exception as e:
            logger.error(f"Error adding user behavior: {str(e)}")
            self.session.rollback()
            return None
            
    def get_user_actions(self, user_id, action_type=None, start_time=None, end_time=None):
        """获取用户特定类型的行为记录
        
        Args:
            user_id: 用户ID
            action_type: 行为类型（如：view, like, share等）
            start_time: 开始时间
            end_time: 结束时间
        """
        try:
            query = self.session.query(UserBehavior).filter_by(user_id=user_id)
            
            if action_type:
                query = query.filter_by(action=action_type)
            if start_time:
                query = query.filter(UserBehavior.timestamp >= start_time)
            if end_time:
                query = query.filter(UserBehavior.timestamp <= end_time)
                
            behaviors = query.order_by(desc(UserBehavior.timestamp)).all()
            return [behavior.to_dict() for behavior in behaviors]
            
        except Exception as e:
            logger.error(f"Error getting user actions: {str(e)}")
            return []
            
    def get_item_interactions(self, item_id):
        """获取内容的交互记录
        
        Args:
            item_id: 内容ID
        """
        try:
            behaviors = self.session.query(UserBehavior)\
                .filter_by(item_id=item_id)\
                .order_by(desc(UserBehavior.timestamp))\
                .all()
            return [behavior.to_dict() for behavior in behaviors]
            
        except Exception as e:
            logger.error(f"Error getting item interactions: {str(e)}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        self.session.close() 