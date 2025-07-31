#!/usr/bin/env python3
"""
AWS設定自動化スクリプト
化学物質管理AI支援サービス MVP4用
"""

import subprocess
import sys
import os

def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔄 {description}")
    print(f"実行コマンド: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功: {result.stdout}")
            return True
        else:
            print(f"❌ エラー: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 例外: {e}")
        return False

def main():
    print("🚀 AWS設定自動化スクリプト")
    print("=" * 50)
    
    # AWS CLIのバージョン確認
    if not run_command("aws --version", "AWS CLIのバージョン確認"):
        print("❌ AWS CLIがインストールされていません")
        return
    
    print("\n📋 次の手順でAWS設定を行います:")
    print("1. AWSコンソールでIAMユーザーとアクセスキーを作成")
    print("2. アクセスキー情報を入力")
    print("3. リージョンを設定")
    print("4. EC2インスタンスを作成")
    
    # 設定情報の入力
    print("\n" + "=" * 50)
    print("🔑 AWS設定情報の入力")
    print("=" * 50)
    
    access_key = input("Access Key IDを入力してください: ").strip()
    secret_key = input("Secret Access Keyを入力してください: ").strip()
    region = input("リージョンを入力してください (デフォルト: ap-northeast-1): ").strip()
    
    if not region:
        region = "ap-northeast-1"
    
    # AWS設定
    print("\n" + "=" * 50)
    print("⚙️ AWS設定の実行")
    print("=" * 50)
    
    # AWS configure
    configure_command = f'aws configure set aws_access_key_id "{access_key}"'
    if not run_command(configure_command, "Access Key IDの設定"):
        return
    
    configure_command = f'aws configure set aws_secret_access_key "{secret_key}"'
    if not run_command(configure_command, "Secret Access Keyの設定"):
        return
    
    configure_command = f'aws configure set region "{region}"'
    if not run_command(configure_command, "リージョンの設定"):
        return
    
    configure_command = 'aws configure set output json'
    if not run_command(configure_command, "出力形式の設定"):
        return
    
    # 設定確認
    print("\n" + "=" * 50)
    print("✅ 設定確認")
    print("=" * 50)
    
    if run_command("aws sts get-caller-identity", "AWS認証情報の確認"):
        print("\n🎉 AWS設定が完了しました！")
        print("\n📋 次のステップ:")
        print("1. EC2インスタンスの作成")
        print("2. セキュリティグループの設定")
        print("3. アプリケーションのデプロイ")
        
        # EC2インスタンス作成の案内
        print("\n🔧 EC2インスタンス作成の準備:")
        print("以下のコマンドでEC2インスタンスを作成できます:")
        print(f"aws ec2 run-instances \\")
        print(f"  --image-id ami-0d52744d6551d851e \\")  # Amazon Linux 2
        print(f"  --count 1 \\")
        print(f"  --instance-type t2.micro \\")
        print(f"  --key-name chemical-mvp4-key \\")
        print(f"  --security-group-ids sg-xxxxxxxxx \\")
        print(f"  --subnet-id subnet-xxxxxxxxx \\")
        print(f"  --tag-specifications 'ResourceType=instance,Tags=[{{Key=Name,Value=chemical-mvp4}}]'")
        
    else:
        print("\n❌ AWS設定に失敗しました")
        print("アクセスキーとシークレットキーを確認してください")

if __name__ == "__main__":
    main() 