import chromadb
from chromadb.config import Settings
from config.settings import CHROMA_CONFIG, DATA_FILES, CONTENT_TYPES
from utils.embeddings import EmbeddingService
import json
import logging
import hashlib
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        """初始化 Chroma 服务"""
        self.client = chromadb.HttpClient(
            host=CHROMA_CONFIG['CHROMA_HOST'],
            port=CHROMA_CONFIG['CHROMA_PORT'],
            ssl=False,
            headers={
                "X-Chroma-Token": CHROMA_CONFIG['CHROMA_KEY'],
                "X-Chroma-Tenant": CHROMA_CONFIG['CHROMA_TENANT'],
                "X-Chroma-Database": CHROMA_CONFIG['CHROMA_DATABASE']
            }
        )
        self.collection_name = CHROMA_CONFIG['CHROMA_COLLECTION_NAME']
        self.embedding_service = EmbeddingService()
        
    def initialize_data(self):
        """初始化数据"""
        try:
            collection = self._get_or_create_collection()
            
            for data_type, file_path in DATA_FILES.items():
                logger.info(f"Processing {data_type} data from {file_path}")
                self._process_file(file_path, collection, data_type)
                
        except Exception as e:
            logger.error(f"Error initializing data: {str(e)}")
            raise
            
    def get_default_recommendations(self, recommend_type: str, limit: int) -> List[Dict[str, Any]]:
        """获取默认推荐"""
        try:
            collection = self._get_collection()
            
            # 构建查询文本
            type_desc = CONTENT_TYPES.get(recommend_type, recommend_type)
            query_text = f"推荐{type_desc}相关内容"
            query_embedding = self.embedding_service.get_embedding(query_text)
            
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where={"type": recommend_type}
            )
            return [json.loads(doc) for doc in results['documents'][0]]
        except Exception as e:
            logger.error(f"Error getting default recommendations: {str(e)}")
            return []
            
    def get_content_recommendations(self, user_behavior: Dict, recommend_type: str, limit: int) -> List[Dict[str, Any]]:
        """基于内容的推荐"""
        try:
            collection = self._get_collection()
            
            # 构建用户画像文本
            profile_text = self._build_user_profile_text(user_behavior, recommend_type)
            if not profile_text:
                return self.get_default_recommendations(recommend_type, limit)
            
            # 生成用户画像向量
            query_embedding = self.embedding_service.get_embedding(profile_text)
            
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where={"type": recommend_type}
            )
            
            return [json.loads(doc) for doc in results['documents'][0]]
            
        except Exception as e:
            logger.error(f"Error getting content recommendations: {str(e)}")
            return []
            
    def get_collaborative_recommendations(self, user_id: str, recommend_type: str, limit: int) -> List[Dict[str, Any]]:
        """基于协同过滤的推荐"""
        try:
            collection = self._get_collection()
            
            # 获取用户历史行为
            user_history = self.db_service.get_user_behavior(user_id)
            if not user_history:
                return self.get_default_recommendations(recommend_type, limit)
            
            # 构建用户历史行为文本
            history_text = self._build_user_history_text(user_history)
            query_embedding = self.embedding_service.get_embedding(history_text)
            
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where={"type": recommend_type}
            )
            
            return [json.loads(doc) for doc in results['documents'][0]]
            
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {str(e)}")
            return []
            
    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
    def _get_collection(self):
        """获取集合"""
        return self.client.get_collection(name=self.collection_name)
        
    def _process_file(self, file_path: str, collection, data_type: str):
        """处理数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 获取现有的ID列表
            try:
                existing_ids = set(collection.get()['ids'])
                logger.info(f"Found {len(existing_ids)} existing items in collection")
            except Exception as e:
                logger.warning(f"Error getting existing IDs, assuming empty collection: {str(e)}")
                existing_ids = set()
            
            # 批量处理数据
            batch_size = 100
            current_batch = {
                'ids': [],
                'embeddings': [],
                'metadatas': [],
                'documents': []
            }
            
            for item in data:
                try:
                    # 生成唯一ID
                    item_str = json.dumps(item, sort_keys=True)
                    item_id = hashlib.md5(item_str.encode()).hexdigest()
                    
                    # 添加类型信息
                    item['type'] = data_type
                    
                    # 如果ID不存在，添加到批次
                    if item_id not in existing_ids:
                        # 准备文本
                        text = self._prepare_item_text(item, data_type)
                        
                        # 生成嵌入向量
                        embedding = self.embedding_service.get_embedding(text)
                        
                        # 添加到当前批次
                        current_batch['ids'].append(item_id)
                        current_batch['embeddings'].append(embedding.tolist())
                        current_batch['metadatas'].append({"type": data_type})
                        current_batch['documents'].append(json.dumps(item, ensure_ascii=False))
                        
                        # 如果达到批处理大小，执行添加
                        if len(current_batch['ids']) >= batch_size:
                            self._add_batch(collection, current_batch)
                            # 重置批次
                            current_batch = {
                                'ids': [],
                                'embeddings': [],
                                'metadatas': [],
                                'documents': []
                            }
                            
                except Exception as e:
                    logger.error(f"Error processing item: {str(e)}")
                    continue
            
            # 处理剩余的批次
            if current_batch['ids']:
                self._add_batch(collection, current_batch)
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise
            
    def _add_batch(self, collection, batch):
        """添加批量数据到集合"""
        try:
            collection.add(
                ids=batch['ids'],
                embeddings=batch['embeddings'],
                metadatas=batch['metadatas'],
                documents=batch['documents']
            )
            logger.info(f"Successfully added batch of {len(batch['ids'])} items")
        except Exception as e:
            logger.error(f"Error adding batch: {str(e)}")
            # 如果批量添加失败，尝试逐个添加
            for i in range(len(batch['ids'])):
                try:
                    collection.add(
                        ids=[batch['ids'][i]],
                        embeddings=[batch['embeddings'][i]],
                        metadatas=[batch['metadatas'][i]],
                        documents=[batch['documents'][i]]
                    )
                except Exception as e:
                    logger.error(f"Error adding item {batch['ids'][i]}: {str(e)}")
                    continue
            
    def _prepare_item_text(self, item: Dict, data_type: str) -> str:
        """准备项目文本
        
        Args:
            item (Dict): 项目数据
            data_type (str): 数据类型
            
        Returns:
            str: 处理后的文本
        """
        if data_type == 'academic':
            title = item.get('title', '')
            abstract = item.get('abstract', '')
            keywords = ' '.join(item.get('keywords', []))
            authors = ' '.join([a.get('name', '') for a in item.get('authors', [])])
            return f"{title} {abstract} {keywords} {authors}"
            
        elif data_type == 'conference':
            name = item.get('name', '')
            topics = ' '.join([a.get('topic', '') for a in item.get('agenda', [])])
            speakers = ' '.join([s.get('name', '') for s in item.get('speakers', [])])
            return f"{name} {topics} {speakers}"
            
        else:
            title = item.get('title', '')
            content = item.get('content', '')
            tags = ' '.join(item.get('tags', []))
            return f"{title} {content} {tags}"
            
    def _build_user_profile_text(self, user_behavior: Dict, recommend_type: str) -> str:
        """构建用户画像文本
        
        Args:
            user_behavior (Dict): 用户行为数据
            recommend_type (str): 推荐类型
            
        Returns:
            str: 用户画像文本
        """
        texts = []
        
        # 添加用户偏好
        if user_behavior.get('preferences'):
            texts.extend(user_behavior['preferences'])
            
        # 添加历史记录
        if user_behavior.get('history'):
            texts.extend(user_behavior['history'])
            
        # 添加推荐类型
        texts.append(f"推荐{CONTENT_TYPES[recommend_type]}")
        
        return ' '.join(texts)
        
    def _build_user_history_text(self, user_history: Dict) -> str:
        """构建用户历史行为文本
        
        Args:
            user_history (Dict): 用户历史行为数据
            
        Returns:
            str: 历史行为文本
        """
        texts = []
        
        # 添加历史交互
        if user_history.get('interactions'):
            for interaction in user_history['interactions']:
                action = interaction.get('action', '')
                item_text = self._prepare_item_text(interaction.get('item', {}), interaction.get('type', ''))
                texts.append(f"{action} {item_text}")
                
        # 添加用户标签
        if user_history.get('tags'):
            texts.extend(user_history['tags'])
            
        return ' '.join(texts) 