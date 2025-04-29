import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.file_attachment import FileAttachment
from app.models.task import Task
from app.models.project import Project
from app.models.user import User

file_bp = Blueprint('file_bp', __name__, url_prefix='/api/files')

@file_bp.route('', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload a file and attach to a task or project
    ---
    tags:
      - Files
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            file_url: {type: string}
            file_name: {type: string}
            task_id: {type: string}
            project_id: {type: string}
    responses:
      201:
        description: File uploaded
    """
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    user_id = claims['sub']
    data = request.json
    file = FileAttachment(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        task_id=data.get('task_id'),
        project_id=data.get('project_id'),
        uploaded_by_user_id=user_id,
        file_url=data['file_url'],
        file_name=data['file_name']
    )
    db.session.add(file)
    db.session.commit()
    return jsonify({'id': file.id, 'file_url': file.file_url, 'file_name': file.file_name}), 201

@file_bp.route('', methods=['GET'])
@jwt_required()
def list_files():
    """
    List files for a task or project
    ---
    tags:
      - Files
    security:
      - Bearer: []
    parameters:
      - in: query
        name: task_id
        type: string
        required: false
      - in: query
        name: project_id
        type: string
        required: false
    responses:
      200:
        description: List of files
    """
    task_id = request.args.get('task_id')
    project_id = request.args.get('project_id')
    q = FileAttachment.query
    if task_id:
        q = q.filter_by(task_id=task_id)
    if project_id:
        q = q.filter_by(project_id=project_id)
    files = q.all()
    return jsonify([
        {'id': f.id, 'file_url': f.file_url, 'file_name': f.file_name, 'uploaded_by_user_id': f.uploaded_by_user_id, 'created_at': f.created_at.isoformat()} for f in files
    ])

@file_bp.route('/<file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """
    Get file details
    ---
    tags:
      - Files
    security:
      - Bearer: []
    parameters:
      - in: path
        name: file_id
        required: true
        type: string
    responses:
      200:
        description: File details
    """
    file = FileAttachment.query.get_or_404(file_id)
    return jsonify({'id': file.id, 'file_url': file.file_url, 'file_name': file.file_name, 'uploaded_by_user_id': file.uploaded_by_user_id, 'created_at': file.created_at.isoformat()})

@file_bp.route('/<file_id>', methods=['PATCH'])
@jwt_required()
def update_file(file_id):
    """
    Update a file's metadata
    ---
    tags:
      - Files
    security:
      - Bearer: []
    parameters:
      - in: path
        name: file_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            file_name: {type: string}
    responses:
      200:
        description: File updated
    """
    file = FileAttachment.query.get_or_404(file_id)
    data = request.json
    file.file_name = data.get('file_name', file.file_name)
    db.session.commit()
    return jsonify({'id': file.id, 'file_name': file.file_name})

@file_bp.route('/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """
    Delete a file
    ---
    tags:
      - Files
    security:
      - Bearer: []
    parameters:
      - in: path
        name: file_id
        required: true
        type: string
    responses:
      200:
        description: File deleted
    """
    file = FileAttachment.query.get_or_404(file_id)
    db.session.delete(file)
    db.session.commit()
    return jsonify({'msg': 'File deleted'})
