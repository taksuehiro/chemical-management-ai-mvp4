from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import tempfile
import random

# 現在のディレクトリ（MVP4）を基準としたパス設定
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(current_dir, 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join(current_dir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# アップロードフォルダの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(current_dir, 'static', 'temp'), exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 信頼度システム用のヘルパー関数
def get_confidence_color(confidence):
    if confidence >= 80:
        return "success"
    elif confidence >= 60:
        return "warning"
    else:
        return "danger"

def get_confidence_text(confidence):
    if confidence >= 80:
        return "高信頼度"
    elif confidence >= 60:
        return "中信頼度"
    else:
        return "低信頼度"

# 詳細な化学物質データ（信頼度、警告、代替案を含む）
SDS_CONVERSION_DATA = {
    "chemical_name": {
        "value": "エタノール",
        "confidence": 95,
        "reasoning": "SDS文書内で明確に記載されている",
        "warnings": [],
        "alternatives": [],
        "requires_human_review": False
    },
    "cas_number": {
        "value": "64-17-5",
        "confidence": 98,
        "reasoning": "標準的なCAS番号形式で正確に記載",
        "warnings": [],
        "alternatives": [],
        "requires_human_review": False
    },
    "molecular_weight": {
        "value": "46.07 g/mol",
        "confidence": 92,
        "reasoning": "分子式から計算された値と一致",
        "warnings": [],
        "alternatives": [],
        "requires_human_review": False
    },
    "hazard_class": {
        "value": "引火性液体 区分2",
        "confidence": 85,
        "reasoning": "GHS分類に基づく適切な分類",
        "warnings": ["取り扱い時の火気厳禁"],
        "alternatives": [],
        "requires_human_review": False
    },
    "concentration": {
        "value": "95%",
        "confidence": 78,
        "reasoning": "SDS記載値と推定値が近い",
        "warnings": ["高濃度のため取り扱い注意"],
        "alternatives": ["70%", "99.5%"],
        "requires_human_review": True
    },
    "flash_point": {
        "value": "13°C",
        "confidence": 65,
        "reasoning": "文献値と概ね一致するが確認推奨",
        "warnings": ["低い引火点のため厳重な管理が必要"],
        "alternatives": ["12°C", "14°C"],
        "requires_human_review": True
    },
    "boiling_point": {
        "value": "78.3°C",
        "confidence": 88,
        "reasoning": "標準的な沸点値と一致",
        "warnings": [],
        "alternatives": [],
        "requires_human_review": False
    },
    "density": {
        "value": "0.789 g/cm³",
        "confidence": 82,
        "reasoning": "文献値と一致",
        "warnings": [],
        "alternatives": [],
        "requires_human_review": False
    },
    "solubility": {
        "value": "水に易溶",
        "confidence": 55,
        "reasoning": "SDS記載が曖昧、詳細な確認が必要",
        "warnings": ["溶解度の詳細確認が必要"],
        "alternatives": ["水に可溶", "水に微溶"],
        "requires_human_review": True
    },
    "storage_conditions": {
        "value": "密閉容器、冷暗所",
        "confidence": 70,
        "reasoning": "一般的な保管条件と一致",
        "warnings": ["具体的な温度条件の確認推奨"],
        "alternatives": ["密閉容器、20°C以下", "密閉容器、換気良好"],
        "requires_human_review": True
    }
}

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
        filename_with_timestamp = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_with_timestamp)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename_with_timestamp,
            'message': 'ファイルが正常にアップロードされました'
        })
    
    return jsonify({'error': '許可されていないファイル形式です'}), 400

@app.route('/process', methods=['POST'])
def process_file():
    data = request.get_json()
    filename = data.get('filename', '')
    
    if not filename:
        return jsonify({'error': 'ファイル名が指定されていません'}), 400
    
    # 信頼度と注意事項を含む結果を返す
    result = {
        'filename': filename,
        'status': 'completed',
        'extracted_data': SDS_CONVERSION_DATA,
        'summary': {
            'total_items': len(SDS_CONVERSION_DATA),
            'high_confidence_items': len([item for item in SDS_CONVERSION_DATA.values() if item['confidence'] >= 80]),
            'medium_confidence_items': len([item for item in SDS_CONVERSION_DATA.values() if 60 <= item['confidence'] < 80]),
            'low_confidence_items': len([item for item in SDS_CONVERSION_DATA.values() if item['confidence'] < 60]),
            'requires_review_items': len([item for item in SDS_CONVERSION_DATA.values() if item['requires_human_review']]),
            'overall_confidence': sum(item['confidence'] for item in SDS_CONVERSION_DATA.values()) // len(SDS_CONVERSION_DATA)
        },
        'output_file': 'sample_imds_output.xlsx',
        'ai_disclaimer': {
            'title': 'AI支援ツールの利用について',
            'message': 'このシステムはAIによる支援ツールです。抽出された情報は参考値であり、最終的な判断は専門家による確認が必要です。特に信頼度の低い項目については、必ず人間による検証を行ってください。',
            'recommendations': [
                '信頼度60%未満の項目は専門家に相談してください',
                '警告が表示されている項目は特に注意深く確認してください',
                '代替案が提示されている場合は、用途に応じて適切な選択を行ってください',
                '最終的なIMDSデータは責任者による承認を得てから使用してください'
            ]
        }
    }
    
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'メッセージが入力されていません'}), 400
    
    # AI回答を生成
    ai_response = get_chemical_response(user_message)
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/download/<filename>')
def download_file(filename):
    # サンプルのIMDSファイルをダウンロード
    sample_file_path = os.path.join(current_dir, 'static', 'samples', filename)
    
    if os.path.exists(sample_file_path):
        return send_file(sample_file_path, as_attachment=True)
    else:
        return jsonify({'error': 'ファイルが見つかりません'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)