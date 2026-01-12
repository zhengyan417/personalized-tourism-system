from flask import Blueprint, request, jsonify, Response
import requests
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

COZE_API_URL = 'https://api.coze.cn/v3/chat'
COZE_API_TOKEN = 'pat_VdoKRNpNXnmrTo1iLIhYOKwjPs4tODFglzKKfgQPsYNWVUD4owrKSc8UWPHXAqJQ'
BOT_ID = '7583976391813709834'

@ai_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_query = data.get('query')
        user_id = data.get('user_id', 'guest')
        user_profile = data.get('user_profile', {})
        
        messages = []
        if user_profile:
            profile_parts = []
            if user_profile.get('username'):
                profile_parts.append(f"用户名：{user_profile.get('username')}")
            if user_profile.get('age'):
                profile_parts.append(f"年龄：{user_profile.get('age')}岁")
            if user_profile.get('occupation'):
                profile_parts.append(f"职业：{user_profile.get('occupation')}")
            if user_profile.get('travel_persona'):
                profile_parts.append(f"旅行画像：{user_profile.get('travel_persona')}")
            if user_profile.get('favorite_cities'):
                profile_parts.append(f"偏好城市：{user_profile.get('favorite_cities')}")
            
            if profile_parts:
                profile_context = "当前用户资料：\n" + "\n".join(profile_parts)
                messages.append({'role': 'user', 'content': profile_context, 'content_type': 'text'})
        
        messages.append({'role': 'user', 'content': user_query, 'content_type': 'text'})
        
        payload = {
            'bot_id': BOT_ID,
            'user_id': user_id,
            'stream': True,
            'auto_save_history': True,
            'additional_messages': messages
        }
        
        resp = requests.post(
            COZE_API_URL,
            headers={'Authorization': f'Bearer {COZE_API_TOKEN}', 'Content-Type': 'application/json'},
            json=payload,
            stream=True,
            timeout=(10, 120)
        )
        
        if resp.status_code != 200:
            return jsonify({'error': f'Coze API错误 ({resp.status_code})'}), resp.status_code
        
        def generate():
            try:
                for line in resp.iter_lines(decode_unicode=False):
                    if line:
                        yield line + b'\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'.encode('utf-8')
        
        return Response(generate(), content_type='text/event-stream')
        
    except requests.exceptions.Timeout as e:
        return jsonify({'error': 'API超时'}), 504
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': '无法连接到AI服务'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500
