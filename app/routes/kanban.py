from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.project import Project
from app.models.task import Task

kanban_bp = Blueprint('kanban_bp', __name__, url_prefix='/api/kanban')

@kanban_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_kanban_board(project_id):
    """
    Get Kanban board (tasks grouped by status) for a project
    ---
    tags:
      - Kanban
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
    responses:
      200:
        description: Kanban board grouped by status
    """
    tasks = Task.query.filter_by(project_id=project_id).all()
    board = {'todo': [], 'in_progress': [], 'done': [], 'blocked': []}
    for t in tasks:
        board.get(t.status, []).append({
            'id': t.id,
            'title': t.title,
            'assignee_user_id': t.assignee_user_id,
            'due_date': t.due_date.isoformat() if t.due_date else None
        })
    return jsonify(board)
