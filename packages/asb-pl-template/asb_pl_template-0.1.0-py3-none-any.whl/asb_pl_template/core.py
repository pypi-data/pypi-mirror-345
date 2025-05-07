# asb-pl-template/core.py
import os
import shutil
from .constants import PROJECT_TEMPLATE, ROLE_TEMPLATE
from .logger import logger
from .lib import check_directory_exists


def create_directory_structure(path, template, project_name=None):
    """
    创建目录结构
    """
    for key, value in template.items():
        if isinstance(value, dict):
            new_path = os.path.join(path, key)
            if not check_directory_exists(new_path):
                os.makedirs(new_path, exist_ok=True)
                logger.debug(f"Created directory: {new_path}")
            create_directory_structure(new_path, value, project_name)
        else:
            file_path = os.path.join(path, key)
            if project_name:
                content = value.format(project_name=project_name)
            else:
                content = value
            with open(file_path, 'w') as f:
                f.write(content)
            logger.debug(f"Created file: {file_path}")


def create_project(project_name, roles_path=None, role_name=None, playbook_name=None):
    """
    创建项目
    """
    logger.debug(f"Creating project: {project_name}")
    project_path = os.path.join(os.getcwd(), project_name)
    os.makedirs(project_path, exist_ok=True)

    # 创建项目结构
    create_directory_structure(project_path, PROJECT_TEMPLATE, project_name)

    if roles_path and role_name:
        # 确保角色目录创建在项目的 roles 目录下
        roles_full_path = os.path.join(project_path, 'roles')
        os.makedirs(roles_full_path, exist_ok=True)
        logger.debug(f"Created roles directory: {roles_full_path}")
        if isinstance(role_name, list):
            for role in role_name:
                role_path = os.path.join(roles_full_path, role)
                os.makedirs(role_path, exist_ok=True)
                create_directory_structure(role_path, ROLE_TEMPLATE)
                logger.debug(f"Creating role: {role} in {roles_full_path}")
        else:
            role_path = os.path.join(roles_full_path, role_name)
            os.makedirs(role_path, exist_ok=True)
            create_directory_structure(role_path, ROLE_TEMPLATE)
            logger.debug(f"Creating role: {role_name} in {roles_full_path}")

    if playbook_name:
        playbook_path = os.path.join(project_path, 'playbooks', playbook_name)
        with open(playbook_path, 'w') as f:
            f.write(f'# {playbook_name} playbook')
        logger.debug(f"Creating playbook: {playbook_name}")


def delete_project(project_name, roles_path=None, role_name=None):
    """
    删除项目
    """
    if roles_path and role_name:
        project_path = os.path.join(os.getcwd(), project_name)
        role_path = os.path.join(project_path, 'roles', role_name)
        if os.path.exists(role_path):
            shutil.rmtree(role_path)
            logger.debug(f"Deleting role: {role_name} in {roles_path}")
    else:
        logger.debug("No role path and role name specified, skipping deletion.")

