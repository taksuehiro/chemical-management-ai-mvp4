# IMDS (International Material Data Sheet) 階層構造と項目定義

## 📊 IMDS 4階層構造

IMDSは自動車業界で使用される材料データシステムで、以下の4階層で構成されます：

```
🏗️ Component (部品)
  └── 🔧 Semi-Component (準部品)
      └── 🧪 Material (材料)
          └── ⚛️ Basic Substance (基本物質)
```

---

## 🏗️ Level 1: Component (部品)

### 基本情報
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 部品名 | Component Name | ✅ | 製品・部品の正式名称 |
| 部品番号 | Component Number | ✅ | OEM指定の部品番号 |
| 部品重量 | Component Weight | ✅ | 総重量 (g) |
| 用途・機能 | Application/Function | ✅ | 部品の機能説明 |
| 供給者名 | Supplier Name | ✅ | 製造・供給会社名 |
| 供給者コード | Supplier Code | ✅ | DUNS番号等 |

### メタデータ
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 作成日 | Creation Date | ✅ | IMDS作成日 |
| 最終更新日 | Last Modified | ✅ | 最終変更日 |
| バージョン | Version | ✅ | データシートバージョン |
| ステータス | Status | ✅ | Draft/Released/Archived |

---

## 🔧 Level 2: Semi-Component (準部品)

### 基本情報
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 準部品名 | Semi-Component Name | ✅ | 加工済み材料・中間製品名 |
| 準部品重量 | Semi-Component Weight | ✅ | 重量 (g) |
| 加工プロセス | Processing Method | ○ | 射出成形、押出成形等 |
| 表面処理 | Surface Treatment | ○ | 塗装、メッキ、コーティング等 |

### 構成比率
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 含有率 | Content Percentage | ✅ | 部品全体に占める重量% |
| 質量 | Mass | ✅ | 実重量 (g) |

---

## 🧪 Level 3: Material (材料)

### 基本情報
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 材料名 | Material Name | ✅ | 樹脂、金属、繊維等の材料名 |
| 材料分類 | Material Category | ✅ | Polymer/Metal/Ceramic/Composite等 |
| 材料番号 | Material Number | ○ | 材料グレード番号 |
| 供給者 | Material Supplier | ✅ | 材料メーカー名 |

### 物性データ
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 密度 | Density | ○ | g/cm³ |
| 融点 | Melting Point | ○ | °C |
| ガラス転移点 | Glass Transition Temp | ○ | °C (樹脂の場合) |
| 引張強度 | Tensile Strength | ○ | MPa |
| 硬度 | Hardness | ○ | Shore A/D, HRC等 |

### 構成比率
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 含有率 | Content Percentage | ✅ | 準部品に占める重量% |
| 質量 | Mass | ✅ | 実重量 (g) |

---

## ⚛️ Level 4: Basic Substance (基本物質)

### 化学物質情報
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 物質名 | Substance Name | ✅ | 化学物質名（IUPAC名推奨） |
| CAS番号 | CAS Number | ✅ | Chemical Abstracts Service登録番号 |
| EC番号 | EC Number | ○ | European Community番号 |
| 分子式 | Molecular Formula | ○ | 化学式 |
| 分子量 | Molecular Weight | ○ | g/mol |

### 規制・コンプライアンス
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| GADSL分類 | GADSL Classification | ✅ | Prohibited/Declarable/None |
| GADSL番号 | GADSL ID | ○ | GADSL物質番号 |
| REACH登録 | REACH Registration | ○ | 登録番号 |
| SVHCステータス | SVHC Status | ○ | 高懸念物質該当有無 |
| RoHS該当 | RoHS Compliance | ○ | 該当物質の有無 |
| TSCA登録 | TSCA Status | ○ | 米国TSCAインベントリ登録 |

### 含有量・濃度
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 含有率 | Content Percentage | ✅ | 材料中の重量% |
| 質量 | Mass | ✅ | 実重量 (g) |
| 濃度範囲 | Concentration Range | ○ | ppm, %等の範囲 |
| 不純物レベル | Impurity Level | ○ | 不純物として含有するppm |

---

## 🔍 追加メタデータ項目

### データ品質・トレーサビリティ
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| データソース | Data Source | ✅ | SDS/分析結果/推定値 |
| 信頼度 | Confidence Level | ○ | High/Medium/Low |
| 分析方法 | Analytical Method | ○ | XRF/GC-MS/FTIR等 |
| 検証日 | Verification Date | ○ | データ検証実施日 |
| 承認者 | Approver | ○ | データ承認責任者 |

### 安全性・環境
| 項目名 | 英語名 | 必須 | 説明 |
|--------|--------|------|------|
| 危険有害性分類 | Hazard Classification | ○ | GHS分類 |
| 危険有害性コード | Hazard Code | ○ | H200番台等 |
| 注意書き | Precautionary Statement | ○ | P番台コード |
| 廃棄方法 | Disposal Method | ○ | 廃棄時の注意事項 |
| リサイクル可能性 | Recyclability | ○ | リサイクル可能/不可能 |

---

## 📋 GADSL (Global Automotive Declarable Substance List) 関連項目

### GADSL分類詳細
| 分類 | 英語名 | 説明 |
|------|--------|------|
| P | Prohibited | 使用禁止物質 |
| D | Declarable | 申告必要物質 |
| CRM | Critical Raw Materials | 重要原材料 |
| - | Not Listed | GADSL非該当 |

### 申告必要情報
| 項目名 | 英語名 | 説明 |
|--------|--------|------|
| 申告理由 | Declaration Reason | REACH SVHC/RoHS等 |
| 適用法規 | Applicable Regulation | EU RoHS/REACH/ELV等 |
| 閾値 | Threshold Value | 申告が必要な最小濃度 |
| 期限 | Deadline | フェーズアウト期限 |

---

## 🔗 関連システム連携項目

### ERP/PLM連携
| 項目名 | 英語名 | 説明 |
|--------|--------|------|
| ERP品番 | ERP Part Number | 社内管理番号 |
| PLM ID | PLM Identifier | PLMシステム連携ID |
| 図面番号 | Drawing Number | CAD図面番号 |
| 仕様書番号 | Specification Number | 技術仕様書番号 |

この構造により、SDSから抽出したデータを適切なIMDS階層に自動マッピングできるようになります。