# ProjectManager Flask Application

## Features
- User authentication (JWT-based)
- Role-based access control (superadmin, superadmin_readonly, admin, manager, user, viewer)
- Customer management (create, list, update, delete)
- User management (create, list, update, delete, per-customer)
- Access control matrix for endpoints
- Swagger/OpenAPI documentation ([http://localhost:5000/apidocs](http://localhost:5000/apidocs))
- Secure password hashing
- Multi-tenant support
- Database migrations (Flask-Migrate/Alembic)
- Error handling (400, 401, 403, 404, 405, 500)

## API Endpoints

### Authentication
- `POST /api/auth/login` — Obtain JWT access token

### User Management
- `GET /api/users/list` — List users for current customer (admin/manager only)

### Subtasks
- `POST /api/subtasks` — Create a new subtask under a parent task
- `GET /api/subtasks?parent_task_id=xxx` — List subtasks for a parent task
- `GET /api/subtasks/<subtask_id>` — Retrieve subtask details
- `PATCH /api/subtasks/<subtask_id>` — Update subtask details
- `DELETE /api/subtasks/<subtask_id>` — Delete a subtask

### Comments
- `POST /api/comments` — Add a comment to a task
- `GET /api/comments?task_id=xxx` — List comments for a task
- `GET /api/comments/<comment_id>` — Retrieve comment details
- `PATCH /api/comments/<comment_id>` — Update a comment
- `DELETE /api/comments/<comment_id>` — Delete a comment

### File Attachments
- `POST /api/files` — Upload a file and attach to a task or project
- `GET /api/files?task_id=xxx&project_id=yyy` — List files for a task or project
- `GET /api/files/<file_id>` — Retrieve file details
- `PATCH /api/files/<file_id>` — Update file metadata
- `DELETE /api/files/<file_id>` — Delete a file

### Kanban View
- `GET /api/kanban/<project_id>` — Get Kanban board (tasks grouped by status) for a project

### Calendar View
- `GET /api/calendar/<project_id>` — Get calendar view of tasks for a project (tasks with due/start dates)
- `POST /api/users/` — Create user (admin only)
- `GET /api/users/<user_id>` — Get user details (admin/manager/user)
- `PUT /api/users/<user_id>` — Update user (admin only)
- `DELETE /api/users/<user_id>` — Delete user (admin only)

### Customer Management
- `GET /api/customers` — List customers (superadmin/all, others see only their customer)
- `POST /api/customers` — Create a new customer and first admin user
- `GET /api/customers/<customer_id>` — Get customer details
- `PATCH /api/customers/<customer_id>` — Update customer
- `DELETE /api/customers/<customer_id>` — Soft delete (suspend) customer
- `GET /api/customers/<customer_id>/users` — List users for a customer

### Project Management
- `POST /api/projects` — Create a new Project
- `GET /api/projects` — List all Projects for current Customer
- `GET /api/projects/<project_id>` — Get Project Details
- `PATCH /api/projects/<project_id>` — Update Project Details
- `DELETE /api/projects/<project_id>` — Archive Project (soft delete)

### Task Management
- `POST /api/tasks` — Create Task under a Project
- `GET /api/tasks?project_id=xxx` — List Tasks for a Project (with filters)
- `GET /api/tasks/<task_id>` — Get Task Details
- `PATCH /api/tasks/<task_id>` — Update Task Details
- `DELETE /api/tasks/<task_id>` — Delete Task (soft delete)

### Access Control Matrix (Summary)
- **Superadmin/Superadmin Readonly:** Full access to all customers and users
- **Admin/Manager:** Access only to their own customer and users
- **User/Viewer:** Limited to their own data

### Other
- `/apidocs` — Swagger API documentation

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and update the `DATABASE_URL` environment variable if needed.
4. Run database migrations:
   ```bash
   flask db upgrade
   ```
5. Run the application:
   ```bash
   python run.py
   ```
6. Access Swagger docs at [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

## Notes
- Default admin password for new customers: `secret123`

