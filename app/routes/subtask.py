import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.task import Task

subtask_bp = Blueprint('subtask_bp', __name__, url_prefix='/api/subtasks')

@subtask_bp.route('', methods=['POST'])
@jwt_required()
def create_subtask():
    """
    Create a new subtask under a parent task
    ---
    tags:
      - Subtasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            parent_task_id: {type: string}
            title: {type: string, example: "Subtask title"}
            description: {type: string, example: "Subtask details"}
            status: {type: string, enum: [todo, in_progress, done, blocked], example: todo}
            priority: {type: string, enum: [high, medium, low], example: medium}
            assignee_user_id: {type: string}
            due_date: {type: string, format: date}
            start_date: {type: string, format: date}
            position: {type: integer}
    responses:
      201:
        description: Subtask created
    """
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    user_id = claims['sub']
    data = request.json
    subtask = Task(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        project_id=data.get('project_id'),
        parent_task_id=data['parent_task_id'],
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        assignee_user_id=data.get('assignee_user_id'),
        due_date=data.get('due_date'),
        start_date=data.get('start_date'),
        position=data.get('position')
    )
    db.session.add(subtask)
    db.session.commit()
    return jsonify({'id': subtask.id, 'title': subtask.title}), 201

@subtask_bp.route('', methods=['GET'])
@jwt_required()
def list_subtasks():
    """
    List subtasks for a parent task
    ---
    tags:
      - Subtasks
    security:
      - Bearer: []
    parameters:
      - in: query
        name: parent_task_id
        type: string
        required: true
    responses:
      200:
        description: List of subtasks
    """
    parent_task_id = request.args.get('parent_task_id')
    subtasks = Task.query.filter_by(parent_task_id=parent_task_id).all()
    return jsonify([
        {'id': t.id, 'title': t.title, 'status': t.status, 'assignee_user_id': t.assignee_user_id, 'due_date': t.due_date.isoformat() if t.due_date else None} for t in subtasks
    ])

@subtask_bp.route('/<subtask_id>', methods=['GET'])
@jwt_required()
def get_subtask(subtask_id):
    """
    Get subtask details
    ---
    tags:
      - Subtasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: subtask_id
        required: true
        type: string
    responses:
      200:
        description: Subtask details
    """
    subtask = Task.query.get_or_404(subtask_id)
    return jsonify({'id': subtask.id, 'title': subtask.title, 'status': subtask.status, 'assignee_user_id': subtask.assignee_user_id, 'due_date': subtask.due_date.isoformat() if subtask.due_date else None})

@subtask_bp.route('/<subtask_id>', methods=['PATCH'])
@jwt_required()
def update_subtask(subtask_id):
    """
    Update a subtask
    ---
    tags:
      - Subtasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: subtask_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title: {type: string}
            description: {type: string}
            status: {type: string, enum: [todo, in_progress, done, blocked]}
            priority: {type: string, enum: [high, medium, low]}
            assignee_user_id: {type: string}
            due_date: {type: string, format: date}
            start_date: {type: string, format: date}
            completed_at: {type: string, format: date-time}
            position: {type: integer}
    responses:
      200:
        description: Subtask updated
    """
    subtask = Task.query.get_or_404(subtask_id)
    data = request.json
    subtask.title = data.get('title', subtask.title)
    subtask.description = data.get('description', subtask.description)
    subtask.status = data.get('status', subtask.status)
    subtask.priority = data.get('priority', subtask.priority)
    subtask.assignee_user_id = data.get('assignee_user_id', subtask.assignee_user_id)
    subtask.due_date = data.get('due_date', subtask.due_date)
    subtask.start_date = data.get('start_date', subtask.start_date)
    subtask.completed_at = data.get('completed_at', subtask.completed_at)
    subtask.position = data.get('position', subtask.position)
    db.session.commit()
    return jsonify({'id': subtask.id, 'title': subtask.title})

@subtask_bp.route('/<subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(subtask_id):
    """
    Delete a subtask
    ---
    tags:
      - Subtasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: subtask_id
        required: true
        type: string
    responses:
      200:
        description: Subtask deleted
    """
    subtask = Task.query.get_or_404(subtask_id)
    db.session.delete(subtask)
    db.session.commit()
    return jsonify({'msg': 'Subtask deleted'})
