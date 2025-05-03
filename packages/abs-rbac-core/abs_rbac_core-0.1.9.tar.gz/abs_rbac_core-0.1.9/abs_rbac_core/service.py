from typing import List, Optional, Callable,Any

import casbin
from casbin_sqlalchemy_adapter import Adapter
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from abs_exception_core.exceptions import (
    DuplicatedError,
    NotFoundError,
    PermissionDeniedError
)



class RBACService:
    def __init__(self, session: Callable[...,Session],Permission:Any,Role:Any,RolePermission:Any,UserRole:any, conf_file_name:str):
        """
        Service For MAnagening the RBAC
        Args:
            session: Callable[...,Session] -> Session of the SQLAlchemy database engine
            Permission: Any -> Permission model of the system
            Role: Any -> Role model of the system
            RolePermission: Any -> RolePermission model of the system which orchestrate the relation between Role and Permission
            UserRole: Any -> UserRole model of the system which orchestrate the relationship between User and Role
            conf_file_name: str -> File path of the casbin policy's file which defines the rule.
        """
        self.Permission = Permission
        self.Role = Role
        self.RolePermission = RolePermission
        self.UserRole = UserRole
        self.db = session
        self.enforcer = None
        self._initialize_casbin(conf_file_name)

    def _initialize_casbin(self,conf_file_name:str):
        """
        Initiates the cadbin policy using the provided rules
        """
        with self.db() as session:
            engine = session.get_bind()

            adapter = Adapter(engine)
            self.enforcer = casbin.Enforcer(
                conf_file_name, adapter
            )
            self.enforcer.load_policy()

    def list_roles(self) -> Any:
        """
        Get the list of all roles
        """
        with self.db() as session:
            """List all roles"""
            total = session.query(self.Role).count()
            roles = session.query(self.Role).all()
            return {"roles": roles, "total": total}

    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permission_ids: List[str] = None,
    ) -> Any:
        """
        Create role with the provided permissions
        
        Args:
            name: Name of the role
            description: Optional description of the role
            permission_ids: Optional list of permission UUIDs to assign to the role
            
        Returns:
            The created role object
            
        Raises:
            DuplicatedError: If a role with the same name already exists
            NotFoundError: If any of the provided permission IDs don't exist
        """
        with self.db() as session:
            try:
                # Check if role with same name already exists
                existing_role = session.query(self.Role).filter(self.Role.name == name).first()
                if existing_role:
                    raise DuplicatedError(detail="Role already exists")

                # Create the role
                role = self.Role(name=name, description=description)
                session.add(role)
                session.flush()  # Get the role UUID without committing

                # If permission IDs are provided, assign them to the role
                if permission_ids:
                    # Verify all permissions exist in a single query
                    permission_count = (
                        session.query(self.Permission)
                        .filter(self.Permission.uuid.in_(permission_ids))
                        .count()
                    )
                    
                    # Check if all permissions were found
                    if permission_count != len(permission_ids):
                        # Find which permissions are missing
                        existing_permissions = (
                            session.query(self.Permission)
                            .filter(self.Permission.uuid.in_(permission_ids))
                            .all()
                        )
                        found_permission_ids = {p.uuid for p in existing_permissions}
                        missing_ids = set(permission_ids) - found_permission_ids
                        raise NotFoundError(
                            detail=f"Permissions with UUIDs '{', '.join(missing_ids)}' not found"
                        )
                    
                    # Get all permissions for Casbin policy creation
                    existing_permissions = (
                        session.query(self.Permission)
                        .filter(self.Permission.uuid.in_(permission_ids))
                        .all()
                    )
                    
                    # Bulk create role permissions using bulk_insert_mappings for better performance
                    role_permissions = [
                        {"role_uuid": role.uuid, "permission_uuid": permission_uuid}
                        for permission_uuid in permission_ids
                    ]
                    session.bulk_insert_mappings(self.RolePermission, role_permissions)

                    # Batch add Casbin policies
                    policies = [
                        (role.name, permission.resource, permission.action)
                        for permission in existing_permissions
                    ]
                    self.enforcer.add_policies(policies)
                    self.enforcer.save_policy()

                # Commit transaction
                session.commit()
                session.refresh(role)
                return role
            
            except Exception as e:
                raise e

    def get_role_with_permissions(self, role_uuid: str) -> Any:
        """Get role details including its permissions"""
        with self.db() as session:
            # Use joinedload to eagerly load permissions
            role = (
                session.query(self.Role)
                .options(joinedload(self.Role.permissions))
                .filter(self.Role.uuid == role_uuid)
                .first()
            )
            
            if not role:
                raise NotFoundError(detail="Requested role does not exist")
                
            return role

    def update_role_permissions(
        self,
        role_uuid: str,
        permissions: Optional[List[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        """Update role permissions by replacing all existing permissions with new ones"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(self.Role)
                    .options(joinedload(self.Role.permissions))
                    .filter(self.Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Update role information if provided
                if name is not None or description is not None:
                    if name:
                        # Check if new name already exists for a different role
                        existing_role = (
                            session.query(self.Role)
                            .filter(self.Role.name == name, self.Role.uuid != role_uuid)
                            .first()
                        )

                        if existing_role:
                            raise DuplicatedError(detail="Role already exists")
                        
                        if role.name != "super_admin":
                            role.name = name

                    if description is not None:
                        role.description = description

                if permissions is not None:
                    existing_permissions = role.permissions

                    # Remove Casbin policies for existing permissions
                    for existing_permission in existing_permissions:
                        self.enforcer.remove_policy(
                            role.name,
                            existing_permission.resource,
                            existing_permission.action,
                        )
                    self.enforcer.save_policy()

                    # Delete existing role permissions
                    session.query(self.RolePermission).filter(
                        self.RolePermission.role_uuid == role_uuid
                    ).delete(synchronize_session=False)

                if permissions:
                    # Fetch all permissions in a single query
                    permissions_objs = (
                        session.query(self.Permission)
                        .filter(self.Permission.uuid.in_(permissions))
                        .all()
                    )

                    found_permission_ids = {p.uuid for p in permissions_objs}
                    missing_permission_ids = set(permissions) - found_permission_ids
                    if missing_permission_ids:
                        raise NotFoundError(
                            detail=f"Permissions with UUIDs '{', '.join(missing_permission_ids)}' not found"
                        )

                    # Bulk insert role permissions
                    role_permissions = [
                        {"role_uuid": role_uuid, "permission_uuid": permission.uuid}
                        for permission in permissions_objs
                    ]
                    session.bulk_insert_mappings(self.RolePermission, role_permissions)

                    # Add Casbin policies
                    for permission in permissions_objs:
                        self.enforcer.add_policy(
                            role.name, permission.resource, permission.action
                        )

                    self.enforcer.save_policy()

                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                
                # Return the updated role with permissions
                return role

            except Exception as e:
                raise e

    def delete_role(self, role_uuid: str,exception_roles:List[str]=None):
        """Delete a role and its associated permissions"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                role = self.get_role(role_uuid,session)

                if exception_roles and len(exception_roles) > 0 and role.name in exception_roles:
                    raise PermissionDeniedError(detail="You are not allowed to delete the requested role.")
                
                # Get role name for Casbin policy removal
                role_name = role.name

                # Delete role permissions
                role_permissions = (
                    session.query(self.RolePermission)
                    .filter(self.RolePermission.role_uuid == role_uuid)
                    .all()
                )

                # Remove Casbin policies for each permission
                remove_policies =[]
                for role_permission in role_permissions:
                    permission = (
                        session.query(self.Permission)
                        .filter(self.Permission.uuid == role_permission.permission_uuid)
                        .first()
                    )
                    if permission:
                        remove_policies.append(
                            (role_name, permission.resource, permission.action)
                        )

                self.enforcer.remove_policies(remove_policies)
                self.enforcer.save_policy()
                
                # Delete role permissions
                session.query(self.RolePermission).filter(
                    self.RolePermission.role_uuid == role_uuid
                ).delete()

                # Delete user role assignments
                session.query(self.UserRole).filter(self.UserRole.role_uuid == role_uuid).delete()

                # Delete role
                session.delete(role)
                session.commit()

            except Exception as e:
                raise e

    def list_permissions(self) -> List[Any]:
        """Get all permissions with their resources and actions"""
        with self.db() as session:
            return session.query(self.Permission).all()

    def get_user_permissions(self, user_uuid: str) -> List[Any]:
        """Get all allowed permissions for a user"""
        with self.db() as session:
            # Get user roles with eager loading of roles and their permissions
            user_roles = (
                session.query(self.UserRole)
                .join(self.Role, self.UserRole.role_uuid == self.Role.uuid)
                .options(
                    joinedload(self.UserRole.role).joinedload(self.Role.permissions)
                )
                .filter(self.UserRole.user_uuid == user_uuid)
                .all()
            )
            
            if not user_roles:
                return []

            # Build response directly from the eagerly loaded data
            result = []
            for user_role in user_roles:
                role = user_role.role
                for permission in role.permissions:
                    result.append(
                        {
                            "permission_id": permission.uuid,
                            "created_at": permission.created_at,
                            "role_id": role.uuid,
                            "updated_at": permission.updated_at,
                            "role_name": role.name,
                            "name": permission.name,
                            "resource": permission.resource,
                            "action": permission.action,
                        }
                    )

            return result

    def bulk_revoke_permissions(
        self, role_uuid: str, permission_uuids: List[str]
    ) -> Any:
        """Revoke multiple permissions from a role"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(self.Role)
                    .options(joinedload(self.Role.permissions))
                    .filter(self.Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Filter permissions to revoke from the eagerly loaded permissions
                permissions_to_revoke = [
                    p for p in role.permissions 
                    if p.uuid in permission_uuids
                ]

                if not permissions_to_revoke:
                    return role

                # Get UUIDs of permissions to revoke
                permission_uuids_to_revoke = [p.uuid for p in permissions_to_revoke]

                # Delete role permissions
                session.query(self.RolePermission).filter(
                    and_(
                        self.RolePermission.role_uuid == role_uuid,
                        self.RolePermission.permission_uuid.in_(permission_uuids_to_revoke),
                    )
                ).delete(synchronize_session=False)

                # Remove Casbin policies
                policies_to_remove = [
                    (role.name, permission.resource, permission.action)
                    for permission in permissions_to_revoke
                ]
                self.enforcer.remove_policies(policies_to_remove)
                self.enforcer.save_policy()
                
                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                return role

            except Exception as e:
                raise e

    def bulk_attach_permissions(
        self, role_uuid: str, permission_uuids: List[str]
    ) -> Any:
        """Attach multiple permissions to a role"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(self.Role)
                    .options(joinedload(self.Role.permissions))
                    .filter(self.Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Get existing permission UUIDs from the eagerly loaded permissions
                existing_permission_uuids = {p.uuid for p in role.permissions}

                # Calculate new permission UUIDs to attach
                new_permission_uuids = set(permission_uuids) - existing_permission_uuids

                if not new_permission_uuids:
                    return role

                # Fetch new permissions in a single query
                new_permissions = (
                    session.query(self.Permission)
                    .filter(self.Permission.uuid.in_(new_permission_uuids))
                    .all()
                )

                # Verify all permissions were found
                if len(new_permissions) != len(new_permission_uuids):
                    found_permission_uuids = {p.uuid for p in new_permissions}
                    missing_permission_uuids = new_permission_uuids - found_permission_uuids
                    raise NotFoundError(
                        detail=f"Permissions with UUIDs '{', '.join(missing_permission_uuids)}' not found"
                    )

                # Bulk insert role permissions
                role_permissions = [
                    {"role_uuid": role_uuid, "permission_uuid": p.uuid}
                    for p in new_permissions
                ]
                session.bulk_insert_mappings(self.RolePermission, role_permissions)

                # Add Casbin policies
                policies_to_add = [
                    (role.name, permission.resource, permission.action)
                    for permission in new_permissions
                ]
                self.enforcer.add_policies(policies_to_add)
                self.enforcer.save_policy()

                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                return role

            except Exception as e:
                raise e

    def get_user_roles(self, user_uuid: str,session: Optional[Session] = None) -> List[Any]:
        """Get user roles"""
        def query_roles(session: Session) -> List[Any]:
            return (
                session.query(self.Role)
                .join(
                    self.UserRole,
                    and_(
                        self.UserRole.role_uuid == self.Role.uuid,
                        self.UserRole.user_uuid == user_uuid
                    )
                )
                .options(joinedload(self.Role.permissions))
                .all()
            )

        if session:
            return query_roles(session)
        else:
            with self.db() as new_session:
                return query_roles(new_session)
            

    def bulk_assign_roles_to_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Assign multiple roles to a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(self.UserRole)
                    .options(joinedload(self.UserRole.role))
                    .filter(self.UserRole.user_uuid == user_uuid)
                    .all()
                )

                current_role_uuids = {role.role.uuid for role in current_roles}

                new_role_uuids = set(role_uuids) - current_role_uuids

                roles_to_remove = current_role_uuids - set(role_uuids)

                if roles_to_remove:
                    session.query(self.UserRole).filter(
                        and_(
                            self.UserRole.user_uuid == user_uuid,
                            self.UserRole.role_uuid.in_(roles_to_remove),
                        )
                    ).delete(synchronize_session=False)

                if new_role_uuids:
                    new_roles = (
                        session.query(self.Role).filter(self.Role.uuid.in_(new_role_uuids)).all()
                    )

                    if len(new_roles) != len(new_role_uuids):
                        raise NotFoundError(detail="One or more roles not found")

                    user_roles = [
                        self.UserRole(user_uuid=user_uuid, role_uuid=role.uuid)
                        for role in new_roles
                    ]
                    session.bulk_save_objects(user_roles)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    # Bulk Revoke Roles From User
    def bulk_revoke_roles_from_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Revoke multiple roles from a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(self.UserRole)
                    .options(joinedload(self.UserRole.role))
                    .filter(self.UserRole.user_uuid == user_uuid)
                    .filter(self.UserRole.role_uuid.in_(role_uuids))
                    .all()
                )

                if not current_roles:
                    return self.get_user_roles(user_uuid)

                role_uuids_to_revoke = {role.role.uuid for role in current_roles}

                session.query(self.UserRole).filter(
                    and_(
                        self.UserRole.user_uuid == user_uuid,
                        self.UserRole.role_uuid.in_(role_uuids_to_revoke),
                    )
                ).delete(synchronize_session=False)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    def bulk_attach_roles_to_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Attach multiple roles to a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(self.UserRole)
                    .options(joinedload(self.UserRole.role))
                    .filter(self.UserRole.user_uuid == user_uuid)
                    .all()
                )

                current_role_uuids = {role.role.uuid for role in current_roles}

                new_role_uuids = set(role_uuids) - current_role_uuids

                if not new_role_uuids:
                    return self.get_user_roles(user_uuid)

                new_roles = (
                    session.query(self.Role).filter(self.Role.uuid.in_(new_role_uuids)).all()
                )

                if len(new_roles) != len(new_role_uuids):
                    raise NotFoundError(detail="There are some roles that does not exist.")

                user_roles = [
                    self.UserRole(user_uuid=user_uuid, role_uuid=role.uuid) for role in new_roles
                ]
                session.bulk_save_objects(user_roles)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    def check_permission(self, user_uuid: str, resource: str, action: str) -> bool:
        with self.db() as session:
            roles = (
                session.query(self.Role)
                .join(
                    self.UserRole,
                    and_(
                        self.UserRole.role_uuid == self.Role.uuid,
                        self.UserRole.user_uuid == user_uuid,
                    ),
                )
                .all()
            )
            for role in roles:
                if self.enforcer.enforce(role.name, resource, action):
                    return True
            return False

    def check_permission_by_role(
        self, role_name: str, resource: str, action: str
    ) -> bool:
        return self.enforcer.enforce(role_name, resource, action)

    def get_role(self, role_uuid: str,session: Optional[Session] = None) -> Any:
        """Get role by uuid"""
        def query_role(session: Session) -> Any:
            role =  session.query(self.Role).filter(self.Role.uuid == role_uuid).first()
            if not role:
                raise NotFoundError(detail="Requested role does not exist.")
            return role

        if session:
            return query_role(session)
        else:
            with self.db() as session:
                return query_role(session)
