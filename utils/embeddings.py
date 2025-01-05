import torch
from transformers import AutoTokenizer, AutoModel
from config.settings import MODEL_CONFIG
import logging
import numpy as np
from pathlib import Path
import os
import shutil
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        """初始化嵌入服务"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # 设置模型缓存目录
        self.cache_dir = Path("models_cache")
        self.model_name = MODEL_CONFIG['name']
        self.model_cache_dir = self.cache_dir / self.model_name.replace('/', '_')
        
        # 加载模型和分词器
        self._load_model()
        
    def _load_model(self):
        """加载或下载模型"""
        try:
            # 确保缓存目录存在
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            if self.model_cache_dir.exists():
                logger.info("Loading model from local cache...")
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_cache_dir))
                    self.model = AutoModel.from_pretrained(str(self.model_cache_dir))
                    logger.info("Successfully loaded model from cache")
                except Exception as e:
                    logger.error(f"Error loading from cache: {str(e)}")
                    # 如果加载缓存失败，删除可能损坏的缓存
                    shutil.rmtree(self.model_cache_dir, ignore_errors=True)
                    # 尝试重新下载
                    self._download_model()
            else:
                self._download_model()
                
            # 将模型移到正确的设备并设置为评估模式
            self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            logger.error(f"Error in model loading: {str(e)}")
            raise
            
    def _download_model(self):
        """下载并缓存模型"""
        try:
            logger.info("Downloading model from Hugging Face...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # 保存到本地缓存
            logger.info("Saving model to local cache...")
            self.tokenizer.save_pretrained(str(self.model_cache_dir))
            self.model.save_pretrained(str(self.model_cache_dir))
            logger.info(f"Model cached at: {self.model_cache_dir}")
            
        except Exception as e:
            logger.error(f"Error downloading model: {str(e)}")
            raise
            
    def get_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入向量
        
        Args:
            text (str): 输入文本
            
        Returns:
            np.ndarray: 768维的嵌入向量
        """
        try:
            # 文本预处理
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=MODEL_CONFIG['max_length'],
                padding=True
            )
            
            # 移动到正确的设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 生成嵌入向量
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # 获取最后一层的平均池化结果
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
            
            # 移动到 CPU 并转换为 numpy 数组
            return embedding.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # 返回零向量作为后备
            return np.zeros(768)
            
    def get_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """批量生成文本嵌入向量
        
        Args:
            texts (List[str]): 输入文本列表
            
        Returns:
            List[np.ndarray]: 嵌入向量列表
        """
        try:
            embeddings = []
            batch_size = MODEL_CONFIG['batch_size']
            
            # 批量处理
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    truncation=True,
                    max_length=MODEL_CONFIG['max_length'],
                    padding=True
                )
                
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                batch_embeddings = outputs.last_hidden_state.mean(dim=1)
                embeddings.extend(batch_embeddings.cpu().numpy())
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return [np.zeros(768) for _ in texts] 