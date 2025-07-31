#!/usr/bin/env python3
"""
EC2インスタンス作成自動化スクリプト
化学物質管理AI支援サービス MVP4用
"""

import subprocess
import json
import time

def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔄 {description}")
    print(f"実行コマンド: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功")
            return result.stdout
        else:
            print(f"❌ エラー: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ 例外: {e}")
        return None

def create_vpc():
    """VPCを作成"""
    print("\n🌐 VPCの作成")
    
    # VPC作成
    vpc_command = 'aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications ResourceType=vpc,Tags=[{Key=Name,Value=chemical-mvp4-vpc}]'
    vpc_output = run_command(vpc_command, "VPC作成")
    
    if not vpc_output:
        return None
    
    vpc_data = json.loads(vpc_output)
    vpc_id = vpc_data['Vpc']['VpcId']
    print(f"✅ VPC ID: {vpc_id}")
    
    # インターネットゲートウェイ作成
    igw_command = 'aws ec2 create-internet-gateway --tag-specifications ResourceType=internet-gateway,Tags=[{Key=Name,Value=chemical-mvp4-igw}]'
    igw_output = run_command(igw_command, "インターネットゲートウェイ作成")
    
    if not igw_output:
        return None
    
    igw_data = json.loads(igw_output)
    igw_id = igw_data['InternetGateway']['InternetGatewayId']
    print(f"✅ IGW ID: {igw_id}")
    
    # IGWをVPCにアタッチ
    attach_command = f'aws ec2 attach-internet-gateway --vpc-id {vpc_id} --internet-gateway-id {igw_id}'
    run_command(attach_command, "IGWをVPCにアタッチ")
    
    return vpc_id, igw_id

def create_subnet(vpc_id):
    """サブネットを作成"""
    print("\n🌐 サブネットの作成")
    
    # パブリックサブネット作成
    subnet_command = f'aws ec2 create-subnet --vpc-id {vpc_id} --cidr-block 10.0.1.0/24 --availability-zone ap-northeast-1a --tag-specifications ResourceType=subnet,Tags=[{{Key=Name,Value=chemical-mvp4-subnet}}]'
    subnet_output = run_command(subnet_command, "パブリックサブネット作成")
    
    if not subnet_output:
        return None
    
    subnet_data = json.loads(subnet_output)
    subnet_id = subnet_data['Subnet']['SubnetId']
    print(f"✅ サブネット ID: {subnet_id}")
    
    # ルートテーブル作成
    rt_command = f'aws ec2 create-route-table --vpc-id {vpc_id} --tag-specifications ResourceType=route-table,Tags=[{{Key=Name,Value=chemical-mvp4-rt}}]'
    rt_output = run_command(rt_command, "ルートテーブル作成")
    
    if not rt_output:
        return None
    
    rt_data = json.loads(rt_output)
    rt_id = rt_data['RouteTable']['RouteTableId']
    print(f"✅ ルートテーブル ID: {rt_id}")
    
    return subnet_id, rt_id

def create_security_group(vpc_id):
    """セキュリティグループを作成"""
    print("\n🔒 セキュリティグループの作成")
    
    # セキュリティグループ作成
    sg_command = f'aws ec2 create-security-group --group-name chemical-mvp4-sg --description "Security group for Chemical Management AI MVP4" --vpc-id {vpc_id}'
    sg_output = run_command(sg_command, "セキュリティグループ作成")
    
    if not sg_output:
        return None
    
    sg_data = json.loads(sg_output)
    sg_id = sg_data['GroupId']
    print(f"✅ セキュリティグループ ID: {sg_id}")
    
    # ルール追加
    rules = [
        ('--protocol tcp --port 22 --cidr 0.0.0.0/0', "SSH (22)"),
        ('--protocol tcp --port 80 --cidr 0.0.0.0/0', "HTTP (80)"),
        ('--protocol tcp --port 443 --cidr 0.0.0.0/0', "HTTPS (443)"),
        ('--protocol tcp --port 5001 --cidr 0.0.0.0/0', "Flask App (5001)")
    ]
    
    for rule, description in rules:
        rule_command = f'aws ec2 authorize-security-group-ingress --group-id {sg_id} {rule}'
        run_command(rule_command, f"ルール追加: {description}")
    
    return sg_id

def create_key_pair():
    """キーペアを作成"""
    print("\n🔑 キーペアの作成")
    
    key_command = 'aws ec2 create-key-pair --key-name chemical-mvp4-key --query KeyMaterial --output text > chemical-mvp4-key.pem'
    run_command(key_command, "キーペア作成")
    
    # 権限設定
    chmod_command = 'chmod 400 chemical-mvp4-key.pem'
    run_command(chmod_command, "キーファイル権限設定")
    
    print("✅ キーペアファイル: chemical-mvp4-key.pem")

def create_ec2_instance(subnet_id, sg_id):
    """EC2インスタンスを作成"""
    print("\n🖥️ EC2インスタンスの作成")
    
    # Amazon Linux 2 AMI ID (ap-northeast-1)
    ami_id = "ami-0d52744d6551d851e"
    
    instance_command = f'''aws ec2 run-instances \\
  --image-id {ami_id} \\
  --count 1 \\
  --instance-type t2.micro \\
  --key-name chemical-mvp4-key \\
  --security-group-ids {sg_id} \\
  --subnet-id {subnet_id} \\
  --tag-specifications 'ResourceType=instance,Tags=[{{Key=Name,Value=chemical-mvp4}}]' \\
  --user-data file://user_data.sh'''
    
    instance_output = run_command(instance_command, "EC2インスタンス作成")
    
    if not instance_output:
        return None
    
    instance_data = json.loads(instance_output)
    instance_id = instance_data['Instances'][0]['InstanceId']
    print(f"✅ インスタンス ID: {instance_id}")
    
    return instance_id

def get_public_ip(instance_id):
    """パブリックIPを取得"""
    print(f"\n🌐 パブリックIPの取得")
    
    # インスタンスが起動するまで待機
    print("⏳ インスタンスの起動を待機中...")
    time.sleep(30)
    
    ip_command = f'aws ec2 describe-instances --instance-ids {instance_id} --query Reservations[0].Instances[0].PublicIpAddress --output text'
    public_ip = run_command(ip_command, "パブリックIP取得")
    
    if public_ip:
        public_ip = public_ip.strip()
        print(f"✅ パブリックIP: {public_ip}")
        return public_ip
    
    return None

def create_user_data_script():
    """ユーザーデータスクリプトを作成"""
    user_data = '''#!/bin/bash
# システムアップデート
yum update -y

# Python3とpipのインストール
yum install python3 python3-pip -y

# Gitのインストール
yum install git -y

# アプリケーションのクローン
cd /home/ec2-user
git clone https://github.com/taksuehiro/chemical-management-ai-mvp4.git
cd chemical-management-ai-mvp4

# 依存関係のインストール
pip3 install -r requirements.txt

# 必要なディレクトリの作成
mkdir -p uploads
mkdir -p static/temp
mkdir -p static/samples

# アプリケーション起動
nohup python3 app.py > app.log 2>&1 &
'''
    
    with open('user_data.sh', 'w') as f:
        f.write(user_data)
    
    print("✅ ユーザーデータスクリプト作成: user_data.sh")

def main():
    print("🚀 EC2インスタンス作成自動化スクリプト")
    print("=" * 60)
    
    # AWS認証確認
    auth_output = run_command("aws sts get-caller-identity", "AWS認証確認")
    if not auth_output:
        print("❌ AWS認証に失敗しました")
        return
    
    print("✅ AWS認証成功")
    
    # ユーザーデータスクリプト作成
    create_user_data_script()
    
    # VPC作成
    vpc_result = create_vpc()
    if not vpc_result:
        print("❌ VPC作成に失敗しました")
        return
    
    vpc_id, igw_id = vpc_result
    
    # サブネット作成
    subnet_result = create_subnet(vpc_id)
    if not subnet_result:
        print("❌ サブネット作成に失敗しました")
        return
    
    subnet_id, rt_id = subnet_result
    
    # セキュリティグループ作成
    sg_id = create_security_group(vpc_id)
    if not sg_id:
        print("❌ セキュリティグループ作成に失敗しました")
        return
    
    # キーペア作成
    create_key_pair()
    
    # EC2インスタンス作成
    instance_id = create_ec2_instance(subnet_id, sg_id)
    if not instance_id:
        print("❌ EC2インスタンス作成に失敗しました")
        return
    
    # パブリックIP取得
    public_ip = get_public_ip(instance_id)
    
    print("\n" + "=" * 60)
    print("🎉 EC2インスタンス作成完了！")
    print("=" * 60)
    print(f"📋 作成されたリソース:")
    print(f"   VPC ID: {vpc_id}")
    print(f"   サブネット ID: {subnet_id}")
    print(f"   セキュリティグループ ID: {sg_id}")
    print(f"   インスタンス ID: {instance_id}")
    print(f"   パブリックIP: {public_ip}")
    print(f"   キーファイル: chemical-mvp4-key.pem")
    
    if public_ip:
        print(f"\n🌐 アクセスURL:")
        print(f"   http://{public_ip}:5001")
        
        print(f"\n🔑 SSH接続:")
        print(f"   ssh -i chemical-mvp4-key.pem ec2-user@{public_ip}")
    
    print(f"\n📝 注意事項:")
    print(f"   - インスタンスの起動には数分かかります")
    print(f"   - アプリケーションの起動には追加で数分かかります")
    print(f"   - セキュリティグループでポート5001が開放されていることを確認してください")

if __name__ == "__main__":
    main() 