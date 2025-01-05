from flasgger import Swagger, swag_from
from config.settings import API_CONFIG

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": API_CONFIG['title'],
        "description": API_CONFIG['description'],
        "version": API_CONFIG['version'],
        "contact": {
            "name": "智慧语言推荐系统",
            "url": "https://zhihuiyuyan.com",
        }
    },
    "basePath": "/api/v1",
    "tags": [
        {
            "name": "recommend",
            "description": "推荐系统接口"
        }
    ],
    "definitions": {
        "Error": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "integer",
                    "description": "错误代码"
                },
                "message": {
                    "type": "string",
                    "description": "错误信息"
                }
            }
        },
        "Author": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "作者姓名"
                },
                "institution": {
                    "type": "string",
                    "description": "所属机构"
                }
            }
        },
        "Content": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "内容ID"
                },
                "title": {
                    "type": "string",
                    "description": "标题"
                },
                "content": {
                    "type": "string",
                    "description": "内容"
                },
                "abstract": {
                    "type": "string",
                    "description": "摘要"
                },
                "authors": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Author"
                    },
                    "description": "作者信息"
                },
                "date": {
                    "type": "string",
                    "description": "日期"
                },
                "url": {
                    "type": "string",
                    "description": "链接"
                }
            }
        }
    }
}

swagger = Swagger(template=swagger_template, config=swagger_config) 