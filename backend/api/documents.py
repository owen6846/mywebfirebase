# ...existing code...
import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, redirect, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, decode_token, jwt_required
from firebase_admin import firestore
from google.cloud import storage as gcs_client

documents_bp = Blueprint('documents_bp', __name__, url_prefix='/api/documents')

# Helper: GCS client and signed URL generation
def _get_gcs_client():
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if cred_path and os.path.isfile(cred_path):
        return gcs_client.Client.from_service_account_json(cred_path)
    return gcs_client.Client()

def _generate_signed_url(blob_name, expiration_minutes=15):
    client = _get_gcs_client()
    bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
    if not bucket_name:
        raise RuntimeError("FIREBASE_STORAGE_BUCKET 未設定")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.generate_signed_url(expiration=timedelta(minutes=expiration_minutes), version='v4')

# Utility: load document record from Firestore
def _get_document_by_id(doc_id):
    db = firestore.client()
    doc_ref = db.collection('documents').document(doc_id).get()
    if not doc_ref.exists:
        return None
    data = doc_ref.to_dict()
    data['id'] = doc_ref.id
    return data

# 1) 列出公開文件
@documents_bp.route('/public', methods=['GET'])
def list_public_documents():
    try:
        db = firestore.client()
        docs_q = db.collection('documents').where('requires_login', '==', False).stream()
        results = []
        for d in docs_q:
            item = d.to_dict()
            item['id'] = d.id
            # 若 created_at 是 firestore timestamp，轉為 isoformat
            if 'created_at' in item and hasattr(item['created_at'], 'isoformat'):
                item['created_at'] = item['created_at'].isoformat()
            results.append(item)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"獲取公開文件失敗: {str(e)}"}), 500

# 2) 列出私人文件（需要登入）
@documents_bp.route('/private', methods=['GET'])
@jwt_required()
def list_private_documents():
    try:
        db = firestore.client()
        docs_q = db.collection('documents').where('requires_login', '==', True).stream()
        results = []
        for d in docs_q:
            item = d.to_dict()
            item['id'] = d.id
            if 'created_at' in item and hasattr(item['created_at'], 'isoformat'):
                item['created_at'] = item['created_at'].isoformat()
            results.append(item)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"獲取私人文件失敗: {str(e)}"}), 500

# 3) 下載文件：公開文件直接 redirect（若為 blob name 則嘗試 public_url 或簽名 URL）
#    私有文件需驗證，並由後端產生 signed URL 並 redirect
@documents_bp.route('/download/<doc_id>', methods=['GET'])
def download_document(doc_id):
    try:
        doc = _get_document_by_id(doc_id)
        if not doc:
            return jsonify({"error": "找不到文件"}), 404

        # 若為公開文件，優先使用 file_url（若為 http(s) 則直接 redirect）
        requires_login = bool(doc.get('requires_login'))
        file_url = doc.get('file_url')

        if not requires_login:
            if file_url and (file_url.startswith('http://') or file_url.startswith('https://')):
                return redirect(file_url)
            # 若公開但存的是 blob name，嘗試用 GCS 取得 public URL 或簽名 URL
            try:
                client = _get_gcs_client()
                bucket = client.bucket(os.getenv('FIREBASE_STORAGE_BUCKET'))
                blob = bucket.blob(file_url)
                # 有 public_url 屬性則 redirect
                if hasattr(blob, 'public_url') and blob.public_url:
                    return redirect(blob.public_url)
                # fallback: 產生短期簽名 URL (60 min)
                signed = _generate_signed_url(file_url, expiration_minutes=60)
                return redirect(signed)
            except Exception as e:
                return jsonify({"error": f"無法取得公開檔案 URL: {str(e)}"}), 500

        # 私有文件部分：驗證授權（支援 Authorization header 或 ?token=）
        jwt_ok = False
        try:
            # 若 header 含 Bearer token，verify_jwt_in_request 會設定 context
            verify_jwt_in_request(optional=True)
            if get_jwt_identity():
                jwt_ok = True
        except Exception:
            jwt_ok = False

        if not jwt_ok:
            token = request.args.get('token')
            if token:
                try:
                    # 嘗試 decode_token 確定 token 有效性（不會建立 request context）
                    decode_token(token)
                    jwt_ok = True
                except Exception:
                    jwt_ok = False

        if not jwt_ok:
            return jsonify({"error": "未授權，需登入以下載此文件"}), 401

        # 產生 signed URL 並 redirect（private file should have blob name stored in file_url）
        blob_name = file_url
        if not blob_name:
            return jsonify({"error": "文件路徑不存在"}), 404
        try:
            signed_url = _generate_signed_url(blob_name, expiration_minutes=15)
            return redirect(signed_url)
        except Exception as e:
            return jsonify({"error": f"產生簽名 URL 失敗: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"下載文件失敗: {str(e)}"}), 500
# ...existing code...