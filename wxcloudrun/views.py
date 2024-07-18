from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from flask import Flask, request, jsonify

APPID = 'wxa68a9f29cd2a5987'
APP_SECRET = '1e10f7573276eb86c4c021a508a248b5'

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

@app.route('/login', methods=['POST'])
def login():
    # 获取小程序发送的 code
    code = request.json.get('code')
    
    if not code:
        return jsonify({'error': 'Missing code'}), 400

    # 构造请求 URL
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={APP_SECRET}&js_code={code}&grant_type=authorization_code'

    # 发送请求到微信服务器
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to connect to WeChat server'}), 500

    data = response.json()

    if 'errcode' in data:
        return jsonify({'error': f"WeChat API error: {data['errmsg']}"}), 400

    # 获取 openid 和 session_key
    openid = data.get('openid')
    session_key = data.get('session_key')
    unionid = data.get('unionid')  # 如果有的话

    # 这里你可以根据 openid 生成自定义登录态
    # 例如，你可以创建一个 JWT token
    custom_token = generate_custom_token(openid)

    # 返回自定义登录态给小程序
    # return jsonify({
    #     'custom_token': custom_token,
    #     'openid': openid,
    #     'unionid': unionid
    # })
    data = {
        'custom_token': custom_token,
        'openid': openid,
        'unionid': unionid
    }
    return make_succ_response(data)

def generate_custom_token(openid):
    # 这里实现你的自定义登录态生成逻辑
    # 可以使用 JWT 或其他方式
    # 这里只是一个示例，实际应用中应该使用更安全的方法
    return f"custom_token_{openid}"