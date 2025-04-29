import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User

comment_bp = Blueprint('comment_bp', __name__, url_prefix='/api/comments')

@comment_bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    """
    Create a new comment on a task
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            task_id: {type: string}
            content: {type: string, example: "This is a comment."}
    responses:
      201:
        description: Comment created
    """
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    user_id = claims['sub']
    data = request.json
    comment = Comment(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        task_id=data['task_id'],
        author_user_id=user_id,
        content=data['content']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'id': comment.id, 'content': comment.content}), 201

@comment_bp.route('', methods=['GET'])
@jwt_required()
def list_comments():
    """
    List comments for a task
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: task_id
        type: string
        required: true
    responses:
      200:
        description: List of comments
    """
    task_id = request.args.get('task_id')
    comments = Comment.query.filter_by(task_id=task_id).all()
    return jsonify([
        {'id': c.id, 'content': c.content, 'author_user_id': c.author_user_id, 'created_at': c.created_at.isoformat()} for c in comments
    ])

@comment_bp.route('/<comment_id>', methods=['GET'])
@jwt_required()
def get_comment(comment_id):
    """
    Get comment details
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        required: true
        type: string
    responses:
      200:
        description: Comment details
    """
    comment = Comment.query.get_or_404(comment_id)
    return jsonify({'id': comment.id, 'content': comment.content, 'author_user_id': comment.author_user_id, 'created_at': comment.created_at.isoformat()})

@comment_bp.route('/<comment_id>', methods=['PATCH'])
@jwt_required()
def update_comment(comment_id):
    """
    Update a comment
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            content: {type: string}
    responses:
      200:
        description: Comment updated
    """
    comment = Comment.query.get_or_404(comment_id)
    data = request.json
    comment.content = data.get('content', comment.content)
    db.session.commit()
    return jsonify({'id': comment.id, 'content': comment.content})

@comment_bp.route('/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """
    Delete a comment
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        required: true
        type: string
    responses:
      200:
        description: Comment deleted
    """
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'msg': 'Comment deleted'})
