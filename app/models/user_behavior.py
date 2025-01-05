from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserBehavior(Base):
    """用户行为模型"""
    __tablename__ = 'user_behavior'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False)
    item_id = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True, default=func.now())
    source = Column(String(50), nullable=True)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'action': self.action,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source
        }
        
    @staticmethod
    def get_user_history(behaviors):
        """从行为列表中获取用户历史记录"""
        return {
            'items': [b.item_id for b in behaviors],
            'actions': [{'item_id': b.item_id, 'action': b.action, 'timestamp': b.timestamp} for b in behaviors],
            'sources': list(set(b.source for b in behaviors if b.source))
        } 