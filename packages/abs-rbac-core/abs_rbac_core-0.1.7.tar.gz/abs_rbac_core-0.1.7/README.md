# RBAC Core Package

A robust Role-Based Access Control (RBAC) implementation for FastAPI applications using Casbin and SQLAlchemy.

## Overview

The RBAC Core package provides a flexible and powerful implementation of Role-Based Access Control for FastAPI applications. It leverages Casbin for policy enforcement and SQLAlchemy for database operations, offering a comprehensive solution for managing user roles, permissions, and access control.

## Features

- Role management (create, update, delete, list)
- Permission management
- User-role assignments
- Role-permission mappings
- Permission checking
- Decorator-based permission enforcement
- SQLAlchemy integration
- Casbin policy enforcement

## Installation

```bash
pip install rbac-core
```

## Implementation Example

### 1. Setup Database Models

```python
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Permission(Base):
    __tablename__ = "permissions"
    uuid = Column(String, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    ...

class Role(Base):
    __tablename__ = "roles"
    uuid = Column(String, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    ...

class RolePermission(Base):
    __tablename__ = "role_permissions"
    uuid = Column(String, primary_key=True)
    role_uuid = Column(String, ForeignKey("roles.uuid"))
    permission_uuid = Column(String, ForeignKey("permissions.uuid"))
    ...

class UserRole(Base):
    __tablename__ = "user_roles"
    uuid = Column(String, primary_key=True)
    user_uuid = Column(String)
    role_uuid = Column(String, ForeignKey("roles.uuid"))
    ...
```

### 2. Initialize RBAC Service

```python
from rbac_core import RBACService
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Create database engine
engine = create_engine("postgresql://user:password@localhost/dbname")
Session = sessionmaker(bind=engine)

# Initialize RBAC service
rbac_service = RBACService(
    session=Session,
    Permission=Permission,
    Role=Role,
    RolePermission=RolePermission,
    UserRole=UserRole,
    conf_file_name="path/to/casbin_policy.conf"
)
```

### 3. Using the RBAC Service

```python
# Create a role with permissions
role = rbac_service.create_role(
    name="admin",
    description="Administrator role",
    permission_ids=["permission1_uuid", "permission2_uuid"]
)

# Assign role to user
rbac_service.bulk_assign_roles_to_user(
    user_uuid="user123_uuid",
    role_uuids=[role.uuid]
)

# Check permissions
has_permission = rbac_service.check_permission(
    user_uuid="user123",
    resource="users",
    action="read"
)
```

### 4. Using the Permission Decorator

```python
from fastapi import FastAPI, Depends
from rbac_core import rbac_require_permission

app = FastAPI()

@app.get("/users")
@rbac_require_permission("users:read")
async def get_users(current_user: dict, rbac_service: RBACService):
    # Your endpoint logic here
    return {"message": "Access granted"}
```

## Casbin Policy Configuration

Create a policy file (e.g., `casbin_policy.conf`):

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

## Error Handling

The package includes several custom exceptions:

- `DuplicateRoleError`: When attempting to create a duplicate role
- `DuplicatePermissionError`: When attempting to create a duplicate permission
- `RoleNotFoundError`: When a requested role doesn't exist
- `PermissionNotFoundError`: When a requested permission doesn't exist
- `RolePermissionNotFoundError`: When a role-permission mapping doesn't exist
- `PermissionDeniedError`: When a user lacks required permissions

## Best Practices

1. Always initialize the RBAC service with proper database models
2. Use meaningful permission names following the "resource:action" format
3. Implement proper error handling for RBAC-related operations
4. Keep the Casbin policy file updated with your access control rules
5. Use the decorator for endpoint-level permission enforcement
6. Regularly audit roles and permissions


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.