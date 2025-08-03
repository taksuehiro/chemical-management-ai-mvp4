from flask import Flask, render_template, request, jsonify, session
import os
import json
from datetime import datetime
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mvp5-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads' # ファイルアップロード用フォルダ

# 許可されるファイル形式（3つのPDFファイルのみ）
ALLOWED_FILES = {
    'mk_ethanol_et9901.pdf': 'mk_ethanol',
    'kao_surfactant_ks2000.pdf': 'kao_surfactant', 
    'ico_ptfe_pt5000.pdf': 'ico_ptfe'
}

def allowed_file(filename):
    """許可されたファイルかチェック（3つのPDFファイルのみ）"""
    return filename in ALLOWED_FILES

# 許可されたファイル拡張子
ALLOWED_EXTENSIONS = {'pdf'}

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

# 複数のサンプルSDSデータ
SAMPLE_SDS_DATA = {
    "neoflon_efep": {
        "id": "neoflon_efep",
        "name": "NEOFLON EFEP RP-500845",
        "manufacturer": "DAIKIN INDUSTRIES, LTD.",
        "category": "フッ素樹脂",
        "description": "電子工業用フッ素樹脂ペレット",
        "cas_number": "1333-86-4",
        "composition": {
            "fluoropolymer": "85-95%",
            "carbon_black": "5-15%"
        },
        "physical_state": "Solid",
        "color": "Black",
        "density": "1.7-1.8 g/cm³",
        "hazard_class": "Not classified (CLP)",
        "flash_point": "Not applicable",
        "boiling_point": "Undetermined",
        "melting_point": "Undetermined",
        "solubility": "Insoluble in water",
        "storage_conditions": "Store in a cool and dry location",
        "handling_precautions": "Ensure good ventilation, avoid heat and direct sunlight"
    },
    "ethanol": {
        "id": "ethanol",
        "name": "エタノール",
        "manufacturer": "日本アルコール工業株式会社",
        "category": "有機溶剤",
        "description": "高純度エタノール（試薬特級）",
        "cas_number": "64-17-5",
        "composition": {
            "ethanol": "99.5%",
            "water": "0.5%"
        },
        "physical_state": "Liquid",
        "color": "Colorless",
        "density": "0.789 g/cm³",
        "hazard_class": "引火性液体 区分2",
        "flash_point": "13°C",
        "boiling_point": "78.3°C",
        "melting_point": "-114.1°C",
        "solubility": "Miscible with water",
        "storage_conditions": "Store in a cool, well-ventilated area away from heat sources",
        "handling_precautions": "Keep away from ignition sources, use explosion-proof equipment"
    },
    "benzene": {
        "id": "benzene",
        "name": "ベンゼン",
        "manufacturer": "三菱化学株式会社",
        "category": "芳香族化合物",
        "description": "高純度ベンゼン（試薬特級）",
        "cas_number": "71-43-2",
        "composition": {
            "benzene": "99.8%",
            "impurities": "0.2%"
        },
        "physical_state": "Liquid",
        "color": "Colorless",
        "density": "0.876 g/cm³",
        "hazard_class": "発がん性 区分1A, 引火性液体 区分1",
        "flash_point": "-11°C",
        "boiling_point": "80.1°C",
        "melting_point": "5.5°C",
        "solubility": "Slightly soluble in water",
        "storage_conditions": "Store in a cool, well-ventilated area in explosion-proof containers",
        "handling_precautions": "Use in fume hood, avoid inhalation and skin contact"
    },
    "acetone": {
        "id": "acetone",
        "name": "アセトン",
        "manufacturer": "三井化学株式会社",
        "category": "ケトン系溶剤",
        "description": "高純度アセトン（試薬特級）",
        "cas_number": "67-64-1",
        "composition": {
            "acetone": "99.9%",
            "water": "0.1%"
        },
        "physical_state": "Liquid",
        "color": "Colorless",
        "density": "0.791 g/cm³",
        "hazard_class": "引火性液体 区分1",
        "flash_point": "-20°C",
        "boiling_point": "56.1°C",
        "melting_point": "-94.7°C",
        "solubility": "Miscible with water",
        "storage_conditions": "Store in a cool, well-ventilated area away from heat and ignition sources",
        "handling_precautions": "Use explosion-proof equipment, avoid open flames"
    },
    "acetic_acid": {
        "id": "acetic_acid",
        "name": "酢酸",
        "manufacturer": "昭和電工株式会社",
        "category": "カルボン酸",
        "description": "高純度酢酸（試薬特級）",
        "cas_number": "64-19-7",
        "composition": {
            "acetic_acid": "99.7%",
            "water": "0.3%"
        },
        "physical_state": "Liquid",
        "color": "Colorless",
        "density": "1.049 g/cm³",
        "hazard_class": "腐食性物質 区分1",
        "flash_point": "39°C",
        "boiling_point": "118.1°C",
        "melting_point": "16.6°C",
        "solubility": "Miscible with water",
        "storage_conditions": "Store in a cool, well-ventilated area in corrosion-resistant containers",
        "handling_precautions": "Use appropriate protective equipment, avoid contact with skin and eyes"
    },
    "sodium_hydroxide": {
        "id": "sodium_hydroxide",
        "name": "水酸化ナトリウム",
        "manufacturer": "日本曹達株式会社",
        "category": "無機塩基",
        "description": "高純度水酸化ナトリウム（試薬特級）",
        "cas_number": "1310-73-2",
        "composition": {
            "sodium_hydroxide": "99.0%",
            "sodium_carbonate": "1.0%"
        },
        "physical_state": "Solid",
        "color": "White",
        "density": "2.13 g/cm³",
        "hazard_class": "腐食性物質 区分1",
        "flash_point": "Not applicable",
        "boiling_point": "1388°C",
        "melting_point": "318°C",
        "solubility": "Highly soluble in water",
        "storage_conditions": "Store in a dry, well-ventilated area in tightly closed containers",
        "handling_precautions": "Use appropriate protective equipment, handle with care due to corrosiveness"
    }
}

# AI抽出結果の生成（どのファイルでも同じ動き）
def generate_ai_extraction(sample_id=None):
    """AI抽出結果を生成（どのファイルでも同じ動き）"""
    
    # どのファイルでも同じ抽出結果を返す
    extraction_result = {
        "chemical_name": {
            "value": "サンプル化学物質",
            "confidence": 95,
            "reasoning": "SDS文書から明確に抽出",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "cas_number": {
            "value": "123-45-6",
            "confidence": 98,
            "reasoning": "SDS記載値と完全一致",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "molecular_weight": {
            "value": "78.11 g/mol",
            "confidence": 92,
            "reasoning": "計算値とSDS記載値が一致",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "hazard_class": {
            "value": "GHS Category 2",
            "confidence": 88,
            "reasoning": "SDS記載の危険有害性分類",
            "warnings": ["現場での確認推奨"],
            "alternatives": ["GHS Category 1", "GHS Category 3"],
            "requires_human_review": True
        },
        "concentration": {
            "value": "100%",
            "confidence": 78,
            "reasoning": "SDS記載値と推定値が近い",
            "warnings": ["純度の確認推奨"],
            "alternatives": ["99.5%", "99.9%"],
            "requires_human_review": True
        },
        "flash_point": {
            "value": "-11°C",
            "confidence": 82,
            "reasoning": "SDS記載値と一致",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "boiling_point": {
            "value": "80.1°C",
            "confidence": 88,
            "reasoning": "標準的な沸点値と一致",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "density": {
            "value": "0.879 g/cm³",
            "confidence": 90,
            "reasoning": "SDS記載値と一致",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "physical_state": {
            "value": "液体",
            "confidence": 95,
            "reasoning": "SDS文書内で明確に記載",
            "warnings": [],
            "alternatives": [],
            "requires_human_review": False
        },
        "storage_conditions": {
            "value": "火気厳禁、換気良好な場所",
            "confidence": 85,
            "reasoning": "SDS記載の保管条件",
            "warnings": ["現場条件との適合性確認推奨"],
            "alternatives": [],
            "requires_human_review": True
        }
    }
    
    return extraction_result

# IMDS階層構造の生成（どのファイルでも同じ動き）
def generate_imds_hierarchy(sample_id=None):
    """IMDS階層構造を生成（どのファイルでも同じ動き）"""
    
    # どのファイルでも同じIMDS構造を返す
    imds_structure = {
        "component": {
            "name": "サンプルコンポーネント",
            "component_number": "COMP-SAMPLE-001",
            "weight": 1000,
            "application": "工業用材料",
            "supplier_name": "サンプル企業株式会社",
            "supplier_code": "DUNS:123456789",
            "creation_date": "2024-01-15",
            "version": "1.0",
            "status": "Draft",
            "confidence": 95
        },
        "semi_components": [
            {
                "name": "サンプル準部品",
                "weight": 1000,
                "processing_method": "標準加工",
                "surface_treatment": "なし",
                "content_percentage": 100,
                "mass": 1000,
                "confidence": 90
            }
        ],
        "materials": [
            {
                "name": "サンプル材料",
                "category": "Polymer",
                "material_number": "MAT-SAMPLE-001",
                "supplier": "サンプル企業株式会社",
                "density": 1.2,
                "melting_point": 150,
                "content_percentage": 100,
                "mass": 1000,
                "confidence": 88
            }
        ],
        "substances": [
            {
                "name": "サンプル物質",
                "cas_number": "123-45-6",
                "ec_number": "200-000-0",
                "molecular_formula": "C6H6",
                "molecular_weight": 78.11,
                "gadsl_classification": "None",
                "reach_registration": "01-2119458958-27-0000",
                "svhc_status": "Not Listed",
                "rohs_compliance": "Compliant",
                "content_percentage": 95,
                "mass": 950,
                "concentration_range": "90-100%",
                "data_source": "SDS",
                "confidence": 95,
                "hazard_classification": "GHS Category 2",
                "hazard_codes": ["H225", "H319"]
            },
            {
                "name": "添加剤",
                "cas_number": "456-78-9",
                "ec_number": "200-000-1",
                "molecular_formula": "C3H6O",
                "molecular_weight": 58.08,
                "gadsl_classification": "None",
                "reach_registration": "01-2119458958-27-0001",
                "svhc_status": "Not Listed",
                "rohs_compliance": "Compliant",
                "content_percentage": 5,
                "mass": 50,
                "concentration_range": "0-10%",
                "data_source": "SDS",
                "confidence": 92,
                "hazard_classification": "Not Classified",
                "hazard_codes": []
            }
        ],
        "total_concentration": 100,
        "data_quality": {
            "analytical_method": "GC-MS",
            "verification_date": "2024-01-10",
            "approver": "品質管理部 田中",
            "recyclability": "Possible"
        }
    }
    
    return imds_structure

# 化学物質相談チャットボット
def get_chemical_response(user_message):
    responses = {
        "有害性": "この化学物質の有害性について説明いたします。詳細な安全データシートを確認し、適切な保護措置を講じてください。",
        "保管方法": "保管方法については、温度・湿度管理、火気厳禁、換気など、物質の特性に応じた適切な条件で保管してください。",
        "廃棄方法": "廃棄方法は、適切な処理業者に委託するか、自治体の廃棄物処理基準に従って処理してください。",
        "代替物質": "代替物質の検討については、用途・性能・安全性を総合的に判断して選択してください。",
        "規制対応": "REACH、RoHS等の規制対応については、最新の法規制を確認し、必要に応じて専門家に相談してください。"
    }
    
    for keyword, response in responses.items():
        if keyword in user_message:
            return response
    
    return "申し訳ございませんが、より具体的な質問をいただけますでしょうか？有害性、保管方法、廃棄方法、代替物質、規制対応などについてお答えできます。"

@app.route('/')
def index():
    return render_template('index.html', samples=SAMPLE_SDS_DATA)

@app.route('/upload_sds', methods=['POST'])
def upload_sds():
    """SDSファイルアップロード処理（どのファイルでも同じ動き）"""
    if 'file' not in request.files:
        return jsonify({"error": "ファイルが選択されていません"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "ファイルが選択されていません"}), 400
    
    # どのファイルでも同じ処理を行う
    filename = secure_filename(file.filename)
    
    # ファイル保存（実際には不要だが、デモ用に保存）
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)
    
    # IMDS変換を自動開始（どのファイルでも同じ結果）
    extraction_result = generate_ai_extraction()
    imds_hierarchy = generate_imds_hierarchy()
    
    session['extraction_result'] = extraction_result
    session['imds_hierarchy'] = imds_hierarchy
    session['uploaded_file'] = filename
    session['selected_company'] = None
    session['selected_sds'] = None
    session['sample_id'] = 'sample'
    
    return jsonify({
        "success": True,
        "extraction_result": extraction_result,
        "imds_hierarchy": imds_hierarchy,
        "uploaded_file": filename,
        "sample_id": 'sample',
        "auto_convert": True
    })

@app.route('/view_sds/<company>/<sds_type>')
def view_sds(company, sds_type):
    """SDSファイルの確認ページ"""
    
    # 会社とSDSタイプに基づいてデータを取得
    sds_data = None
    
    if company == 'mk_chemical' and sds_type == 'ethanol':
        sds_data = {
            'name': '精製エタノール（ET-9901）',
            'supplier': 'MKケミカル株式会社',
            'filename': 'mk_ethanol_et9901.pdf'
        }
    elif company == 'kao_chemical' and sds_type == 'surfactant':
        sds_data = {
            'name': '界面活性剤（KS-2000）',
            'supplier': 'KAOChemical株式会社',
            'filename': 'kao_surfactant_ks2000.pdf'
        }
    elif company == 'ico_rally' and sds_type == 'ptfe':
        sds_data = {
            'name': 'PTFE樹脂（PT-5000）',
            'supplier': 'ICO RALLY Inc.',
            'filename': 'ico_ptfe_pt5000.pdf'
        }
    
    if not sds_data:
        return "SDS not found", 404
    
    return render_template('view_sds.html', sds_data=sds_data)

@app.route('/process_sample', methods=['POST'])
def process_sample():
    data = request.get_json()
    sample_id = data.get('sample_id')
    
    if sample_id not in SAMPLE_SDS_DATA:
        return jsonify({"error": "Invalid sample ID"}), 400
    
    # AI抽出処理のシミュレーション
    extraction_result = generate_ai_extraction(sample_id)
    
    # セッションに結果を保存
    session['extraction_result'] = extraction_result
    session['selected_sample'] = sample_id
    
    return jsonify({
        "success": True,
        "extraction_result": extraction_result,
        "sample_info": SAMPLE_SDS_DATA[sample_id]
    })

@app.route('/accept_reject', methods=['POST'])
def accept_reject():
    data = request.get_json()
    field_name = data.get('field_name')
    action = data.get('action')  # 'accept', 'reject', 'modify'
    modified_value = data.get('modified_value')
    
    if 'extraction_result' not in session:
        return jsonify({"error": "No extraction result found"}), 400
    
    extraction_result = session['extraction_result']
    
    if field_name in extraction_result:
        if action == 'accept':
            extraction_result[field_name]['user_action'] = 'accepted'
        elif action == 'reject':
            extraction_result[field_name]['user_action'] = 'rejected'
        elif action == 'modify':
            extraction_result[field_name]['user_action'] = 'modified'
            extraction_result[field_name]['modified_value'] = modified_value
    
    session['extraction_result'] = extraction_result
    
    return jsonify({"success": True, "extraction_result": extraction_result})

@app.route('/generate_imds_preview')
def generate_imds_preview():
    if 'extraction_result' not in session:
        return jsonify({"error": "No extraction result found"}), 400
    
    extraction_result = session['extraction_result']
    selected_sample = session.get('selected_sample')
    sample_info = SAMPLE_SDS_DATA.get(selected_sample, {})
    
    # 新しいIMDS階層構造を生成
    imds_hierarchy = generate_imds_hierarchy(selected_sample)
    
    return jsonify({
        "success": True,
        "imds_hierarchy": imds_hierarchy,
        "sample_info": sample_info
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    response = get_chemical_response(user_message)
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().strftime("%H:%M")
    })

@app.route('/static/samples/<filename>')
def serve_pdf(filename):
    """PDFファイルを配信する専用ルート"""
    try:
        response = app.send_static_file(f'samples/{filename}')
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename={filename}'
        return response
    except Exception as e:
        return f"PDF file not found: {filename}", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 