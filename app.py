from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import tempfile
import random

# 現在のディレクトリ（MVP2）を基準としたパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(current_dir, 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join(current_dir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# アップロードフォルダの作成（MVP2内に作成）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(current_dir, 'static', 'temp'), exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 化学物質相談用のサンプル回答データ
CHEMICAL_QA_DATA = {
    "有害性": {
        "keywords": ["有害", "危険", "毒性", "安全", "危険性"],
        "responses": [
            "この化学物質は有害性区分2に分類されています。皮膚刺激性があり、取り扱い時は保護具の着用が必要です。",
            "毒性は中程度で、大量摂取や長期暴露を避ける必要があります。",
            "環境への影響も考慮し、適切な廃棄処理が必要です。"
        ]
    },
    "保管方法": {
        "keywords": ["保管", "保存", "貯蔵", "温度", "湿度"],
        "responses": [
            "密閉容器で冷暗所に保管してください。温度は25℃以下、湿度は60%以下を推奨します。",
            "直射日光を避け、換気の良い場所に保管してください。",
            "他の化学物質との接触を避け、専用の保管庫を使用してください。"
        ]
    },
    "廃棄方法": {
        "keywords": ["廃棄", "処分", "ゴミ", "環境", "処理"],
        "responses": [
            "専門の廃棄業者に依頼して適切に処理してください。",
            "自治体の有害廃棄物収集に出すか、専門業者に相談してください。",
            "環境への影響を最小限に抑えるため、適切な処理方法を選択してください。"
        ]
    },
    "代替物質": {
        "keywords": ["代替", "代わり", "別の", "類似", "代替品"],
        "responses": [
            "より安全な代替物質として、[代替物質名]が考えられます。",
            "機能を維持しながら、環境負荷の低い物質への置き換えが可能です。",
            "具体的な代替案については、用途や要件を詳しく教えていただけますか？"
        ]
    },
    "規制対応": {
        "keywords": ["規制", "法律", "REACH", "RoHS", "法規制"],
        "responses": [
            "REACH規制の対象物質です。登録・評価・認可の手続きが必要です。",
            "RoHS指令の制限物質には含まれていませんが、継続的な監視が必要です。",
            "最新の規制動向を確認し、適切な対応を行ってください。"
        ]
    }
}

def get_chemical_response(user_message):
    """ユーザーメッセージに基づいて化学物質相談の回答を生成"""
    user_message_lower = user_message.lower()
    
    # キーワードマッチング
    for category, data in CHEMICAL_QA_DATA.items():
        for keyword in data["keywords"]:
            if keyword in user_message_lower:
                return random.choice(data["responses"])
    
    # デフォルト回答
    default_responses = [
        "化学物質に関するご質問ですね。より具体的な内容を教えていただけますか？",
        "安全性、保管方法、廃棄方法など、どのような点についてお知りになりたいですか？",
        "この化学物質について、どのような情報をお探しでしょうか？",
        "専門的なアドバイスが必要でしたら、詳細をお聞かせください。"
    ]
    
    return random.choice(default_responses)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'ファイルがアップロードされました'
        })
    
    return jsonify({'error': '許可されていないファイル形式です'}), 400

@app.route('/process', methods=['POST'])
def process_file():
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'ファイル名が指定されていません'}), 400
    
    # 処理のシミュレーション
    import time
    time.sleep(2)
    
    result = {
        'filename': filename,
        'status': 'completed',
        'extracted_data': {
            'chemical_name': 'サンプル化学物質',
            'cas_number': '123-45-6',
            'molecular_weight': '100.0 g/mol',
            'hazard_class': '有害性区分2',
            'concentration': '10%'
        },
        'output_file': 'sample_imds_output.xlsx'
    }
    
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    """チャットボットAPI"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'メッセージが入力されていません'}), 400
    
    # 化学物質相談の回答を生成
    response = get_chemical_response(user_message)
    
    # タイムスタンプ
    timestamp = datetime.now().strftime('%H:%M')
    
    return jsonify({
        'response': response,
        'timestamp': timestamp,
        'type': 'bot'
    })

@app.route('/download/<filename>')
def download_file(filename):
    # サンプルのIMDSファイルをダウンロード
    sample_file = os.path.join(current_dir, 'static', 'samples', 'sample_imds_output.xlsx')
    
    if os.path.exists(sample_file):
        return send_file(sample_file, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': f'ファイルが見つかりません: {sample_file}'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)