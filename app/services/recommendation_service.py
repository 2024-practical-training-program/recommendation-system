from app.services.database_service import DatabaseService
from app.services.chroma_service import ChromaService
from config.settings import RECOMMENDATION_CONFIG
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, db_service: DatabaseService):
        """初始化推荐服务"""
        self.db_service = db_service
        self.chroma_service = ChromaService()
        
    def get_recommendations(self, user_id: str, recommend_type: str, limit: int = None):
        """获取推荐内容
        
        Args:
            user_id (str): 用户ID
            recommend_type (str): 推荐类型
            limit (int, optional): 返回结果数量. 默认为配置中的默认值
            
        Returns:
            list: 推荐内容列表
        """
        try:
            # 如果未指定limit，使用默认值
            if limit is None:
                limit = RECOMMENDATION_CONFIG['default_results']
            
            # 获取用户行为数据
            user_behavior = self.db_service.get_user_behavior(user_id)
            
            # 如果用户没有行为数据，返回默认推荐
            if not user_behavior:
                logger.info(f"No behavior data found for user {user_id}, using default recommendations")
                return self.chroma_service.get_default_recommendations(recommend_type, limit)
            
            # 获取基于内容的推荐
            content_recommendations = self.chroma_service.get_content_recommendations(
                user_behavior=user_behavior,
                recommend_type=recommend_type,
                limit=int(limit * RECOMMENDATION_CONFIG['content_weight'])
            )
            
            # 获取协同过滤推荐
            collaborative_recommendations = self.chroma_service.get_collaborative_recommendations(
                user_id=user_id,
                recommend_type=recommend_type,
                limit=int(limit * RECOMMENDATION_CONFIG['collaborative_weight'])
            )
            
            # 合并推荐结果
            recommendations = self._merge_recommendations(
                content_recommendations,
                collaborative_recommendations,
                limit
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            raise
            
    def _merge_recommendations(self, content_recs, collaborative_recs, limit):
        """合并不同来源的推荐结果
        
        Args:
            content_recs (list): 基于内容的推荐结果
            collaborative_recs (list): 基于协同过滤的推荐结果
            limit (int): 最终返回的推荐数量
            
        Returns:
            list: 合并后的推荐结果
        """
        # 使用集合去重
        seen_items = set()
        merged = []
        
        # 交替添加两种推荐结果
        content_idx = 0
        collab_idx = 0
        
        while len(merged) < limit and (content_idx < len(content_recs) or collab_idx < len(collaborative_recs)):
            # 添加基于内容的推荐
            if content_idx < len(content_recs):
                item = content_recs[content_idx]
                if item['id'] not in seen_items:
                    merged.append(item)
                    seen_items.add(item['id'])
                content_idx += 1
            
            # 添加协同过滤推荐
            if collab_idx < len(collaborative_recs) and len(merged) < limit:
                item = collaborative_recs[collab_idx]
                if item['id'] not in seen_items:
                    merged.append(item)
                    seen_items.add(item['id'])
                collab_idx += 1
        
        return merged[:limit]