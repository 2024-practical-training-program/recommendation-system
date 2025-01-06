from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.services.recommendation_service import RecommendationService
from app.services.database_service import DatabaseService
from config.settings import CONTENT_TYPES, RECOMMENDATION_CONFIG
import logging
from datetime import datetime

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

@recommend_bp.route('/behavior', methods=['POST'])
@swag_from({
    'tags': ['behavior'],
    'summary': '记录用户行为',
    'description': '记录用户的交互行为，包括浏览、点赞、分享、评论和收藏等操作',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': '用户行为数据',
            'schema': {
                'type': 'object',
                'required': ['user_id', 'item_id', 'action'],
                'properties': {
                    'user_id': {
                        'type': 'string',
                        'description': '用户ID',
                        'example': 'user123'
                    },
                    'item_id': {
                        'type': 'string',
                        'description': '内容ID',
                        'example': 'article456'
                    },
                    'action': {
                        'type': 'string',
                        'description': '行为类型',
                        'enum': ['view', 'like', 'share', 'comment', 'save'],
                        'example': 'view'
                    },
                    'description': {
                        'type': 'string',
                        'description': '行为描述（可选）',
                        'example': '用户浏览了文章《人工智能发展趋势》'
                    },
                    'source': {
                        'type': 'string',
                        'description': '行为来源（可选），如 web、app 等',
                        'example': 'web'
                    }
                }
            },
            'examples': {
                'view': {
                    'summary': '浏览行为示例',
                    'value': {
                        'user_id': 'user123',
                        'item_id': 'article456',
                        'action': 'view',
                        'description': '用户浏览了文章《人工智能发展趋势》',
                        'source': 'web'
                    }
                },
                'like': {
                    'summary': '点赞行为示例',
                    'value': {
                        'user_id': 'user123',
                        'item_id': 'article456',
                        'action': 'like',
                        'description': '用户点赞了文章',
                        'source': 'app'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': '成功记录用户行为',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'integer',
                        'description': '状态码',
                        'example': 200
                    },
                    'message': {
                        'type': 'string',
                        'description': '响应消息',
                        'example': 'Success'
                    },
                    'data': {
                        'type': 'object',
                        'properties': {
                            'behavior_id': {
                                'type': 'integer',
                                'description': '行为记录ID',
                                'example': 12345
                            },
                            'timestamp': {
                                'type': 'string',
                                'description': '记录时间（ISO 8601格式）',
                                'example': '2024-01-05T16:30:00.123456'
                            }
                        }
                    }
                }
            }
        },
        '400': {
            'description': '请求参数错误',
            'schema': {
                '$ref': '#/definitions/Error'
            },
            'examples': {
                'missing_field': {
                    'summary': '缺少必需字段',
                    'value': {
                        'code': 400,
                        'message': 'Missing required field: user_id'
                    }
                },
                'invalid_action': {
                    'summary': '无效的行为类型',
                    'value': {
                        'code': 400,
                        'message': 'Invalid action. Must be one of: view, like, share, comment, save'
                    }
                }
            }
        },
        '500': {
            'description': '服务器内部错误',
            'schema': {
                '$ref': '#/definitions/Error'
            },
            'example': {
                'code': 500,
                'message': 'Internal server error'
            }
        }
    }
})
def track_behavior():
    """记录用户行为"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['user_id', 'item_id', 'action']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # 验证行为类型
        valid_actions = ['view', 'like', 'share', 'comment', 'save']
        if data['action'] not in valid_actions:
            return jsonify({
                'code': 400,
                'message': f'Invalid action. Must be one of: {", ".join(valid_actions)}'
            }), 400
        
        # 记录用户行为
        behavior = db_service.add_user_behavior(
            user_id=data['user_id'],
            item_id=data['item_id'],
            action=data['action'],
            description=data.get('description'),
            source=data.get('source')
        )
        
        if behavior:
            return jsonify({
                'code': 200,
                'message': 'Success',
                'data': {
                    'behavior_id': behavior['id'],
                    'timestamp': behavior['timestamp']
                }
            })
        else:
            return jsonify({
                'code': 500,
                'message': 'Failed to record behavior'
            }), 500
            
    except Exception as e:
        logger.error(f"Error tracking behavior: {str(e)}")
        return jsonify({
            'code': 500,
            'message': 'Internal server error'
        }), 500