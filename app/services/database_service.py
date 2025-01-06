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
        
    def get_user_behavior(self, user_id: str, limit: int = 100) -> list:
        """获取用户行为数据
        
        Args:
            user_id (str): 用户ID
            limit (int, optional): 返回的记录数量限制. 默认为 100.
            
        Returns:
            list: 用户行为记录列表
        """
        try:
            behaviors = self.session.query(UserBehavior)\
                .filter_by(user_id=user_id)\
                .order_by(desc(UserBehavior.timestamp))\
                .limit(limit)\
                .all()
            return [behavior.to_dict() for behavior in behaviors]
        except Exception as e:
            logger.error(f"Error getting user behavior: {str(e)}")
            return []
            
    def add_user_behavior(self, user_id: str, item_id: str, action: str,
                         description: str = None, source: str = None) -> dict:
        """添加用户行为记录
        
        Args:
            user_id (str): 用户ID
            item_id (str): 内容ID
            action (str): 行为类型
            description (str, optional): 行为描述
            source (str, optional): 行为来源
            
        Returns:
            dict: 新增的行为记录
        """
        try:
            # 创建新的行为记录
            behavior = UserBehavior(
                user_id=user_id,
                item_id=item_id,
                action=action,
                description=description,
                timestamp=datetime.now(),
                source=source
            )
            
            # 添加到数据库
            self.session.add(behavior)
            self.session.commit()
            
            return behavior.to_dict()
            
        except Exception as e:
            logger.error(f"Error adding user behavior: {str(e)}")
            self.session.rollback()
            return None
            
    def get_user_actions(self, user_id: str, start_time: datetime = None,
                        end_time: datetime = None, action_type: str = None) -> list:
        """获取用户特定时间段的行为
        
        Args:
            user_id (str): 用户ID
            start_time (datetime, optional): 开始时间
            end_time (datetime, optional): 结束时间
            action_type (str, optional): 行为类型
            
        Returns:
            list: 行为记录列表
        """
        try:
            query = self.session.query(UserBehavior).filter_by(user_id=user_id)
            
            if start_time:
                query = query.filter(UserBehavior.timestamp >= start_time)
            if end_time:
                query = query.filter(UserBehavior.timestamp <= end_time)
            if action_type:
                query = query.filter_by(action=action_type)
                
            behaviors = query.order_by(desc(UserBehavior.timestamp)).all()
            return [behavior.to_dict() for behavior in behaviors]
            
        except Exception as e:
            logger.error(f"Error getting user actions: {str(e)}")
            return []
            
    def close(self):
        """关闭数据库连接"""
        self.session.close()