from flask import Blueprint, request, jsonify, Response
import requests
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

COZE_API_URL = 'https://api.coze.com/v3/chat'
COZE_API_TOKEN = 'pat_46lwbTaFlf0a2T4ifTN7eFlNXfmpV49GyA2eAikUEdPdUr17WVlCrjpHHhTCGiS6'
BOT_ID = '7583976391813709834'

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """代理转发Coze聊天请求"""
    try:
        data = request.get_json()
        user_query = data.get('query')
        user_id = data.get('user_id', 'guest')
        user_profile = data.get('user_profile', {})
        
        # 构建消息
        messages = []
        if user_profile:
            profile_context = f"""当前用户资料：
用户名：{user_profile.get('username', '未知')}
年龄：{user_profile.get('age', '未知')}
职业：{user_profile.get('occupation', '未知')}
个人简介：{user_profile.get('bio', '无')}
请根据这些信息为用户推荐合适的旅游路线或回答问题。"""
            messages.append({
                'role': 'user',
                'content': profile_context,
                'content_type': 'text'
            })
        
        messages.append({
            'role': 'user',
            'content': user_query,
            'content_type': 'text'
        })
        
        # 调用Coze API
        resp = requests.post(
            COZE_API_URL,
            headers={
                'Authorization': f'Bearer {COZE_API_TOKEN}',
                'Content-Type': 'application/json'
            },
            json={
                'bot_id': BOT_ID,
                'user_id': user_id,
                'stream': True,
                'auto_save_history': True,
                'additional_messages': messages
            },
            stream=True,
            timeout=30
        )
        
        if resp.status_code != 200:
            return jsonify({'error': f'Coze API返回错误: {resp.status_code}'}), resp.status_code
        
        # 流式返回
        def generate():
            try:
                for line in resp.iter_lines():
                    if line:
                        yield line + b'\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)})}\n\n'.encode()
        
        return Response(generate(), content_type='text/event-stream')
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Coze API请求超时'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '无法连接到Coze API'}), 503
    except Exception as e:
        print(f'[AI] Chat error: {e}')
        return jsonify({'error': str(e)}), 500
