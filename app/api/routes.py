from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.services.recommendation_service import RecommendationService
from app.services.database_service import DatabaseService
from config.settings import CONTENT_TYPES, RECOMMENDATION_CONFIG
import logging

logger = logging.getLogger(__name__)
recommend_bp = Blueprint('recommend', __name__)

# 初始化服务
db_service = DatabaseService()
recommendation_service = RecommendationService(db_service)

@recommend_bp.route('/recommend', methods=['GET'])
@swag_from({
    'tags': ['recommend'],
    'summary': '获取推荐内容',
    'description': '根据用户ID和推荐类型获取个性化推荐内容',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': '用户ID'
        },
        {
            'name': 'recommend_type',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': '推荐类型',
            'enum': list(CONTENT_TYPES.keys())
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': '返回结果数量',
            'default': RECOMMENDATION_CONFIG['default_results'],
            'minimum': RECOMMENDATION_CONFIG['min_results'],
            'maximum': RECOMMENDATION_CONFIG['max_results']
        }
    ],
    'responses': {
        '200': {
            'description': '成功获取推荐内容',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'example': 200
                    },
                    'message': {
                        'type': 'string',
                        'example': 'Success'
                    },
                    'data': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/definitions/Content'
                        }
                    }
                }
            }
        },
        '400': {
            'description': '请求参数错误',
            'schema': {
                '$ref': '#/definitions/Error'
            }
        },
        '500': {
            'description': '服务器内部错误',
            'schema': {
                '$ref': '#/definitions/Error'
            }
        }
    }
})
def get_recommendations():
    """获取推荐内容"""
    try:
        # 获取请求参数
        user_id = request.args.get('user_id')
        recommend_type = request.args.get('recommend_type')
        limit = request.args.get('limit', RECOMMENDATION_CONFIG['default_results'], type=int)
        
        # 参数验证
        if not user_id or not recommend_type:
            return jsonify({
                'code': 400,
                'message': 'Missing required parameters'
            }), 400
            
        if recommend_type not in CONTENT_TYPES:
            return jsonify({
                'code': 400,
                'message': f'Invalid recommend_type. Must be one of: {", ".join(CONTENT_TYPES.keys())}'
            }), 400
            
        if not RECOMMENDATION_CONFIG['min_results'] <= limit <= RECOMMENDATION_CONFIG['max_results']:
            return jsonify({
                'code': 400,
                'message': f'Limit must be between {RECOMMENDATION_CONFIG["min_results"]} and {RECOMMENDATION_CONFIG["max_results"]}'
            }), 400
        
        # 获取推荐结果
        recommendations = recommendation_service.get_recommendations(
            user_id=user_id,
            recommend_type=recommend_type,
            limit=limit
        )
        
        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({
            'code': 500,
            'message': 'Internal server error'
        }), 500