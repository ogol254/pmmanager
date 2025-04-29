from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.project import Project
from app.models.task import Task

calendar_bp = Blueprint('calendar_bp', __name__, url_prefix='/api/calendar')

@calendar_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project_calendar(project_id):
    """
    Get calendar view of tasks for a project (tasks with due/start dates)
    ---
    tags:
      - Calendar
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        required: true
        type: string
    responses:
      200:
        description: List of tasks with dates for calendar view
    """
    tasks = Task.query.filter_by(project_id=project_id).all()
    events = []
    for t in tasks:
        if t.start_date or t.due_date:
            events.append({
                'id': t.id,
                'title': t.title,
                'start': t.start_date.isoformat() if t.start_date else None,
                'end': t.due_date.isoformat() if t.due_date else None,
                'status': t.status,
                'assignee_user_id': t.assignee_user_id
            })
    return jsonify(events)
