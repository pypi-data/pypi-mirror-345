# asb-pl-template/cli.py
import argparse
import logging
from .core import create_project, delete_project
from .logger import setup_logger


def main():
    parser = argparse.ArgumentParser(description="Ansible playbook template tool")
    subparsers = parser.add_subparsers(dest="command")

    # --verbose 参数
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    # 创建项目的子命令
    create_parser = subparsers.add_parser("create", help="Create a new project or role")
    create_parser.add_argument("project_name", help="Name of the project")
    create_parser.add_argument("--roles-path", help="Path to the roles directory")
    create_parser.add_argument("--role-name", action="append", help="Name of the role")
    create_parser.add_argument("--playbook-name", help="Name of the playbook")

    # 删除项目的子命令
    delete_parser = subparsers.add_parser("delete", help="Delete a project or role")
    delete_parser.add_argument("project_name", help="Name of the project")
    delete_parser.add_argument("--roles-path", help="Path to the roles directory")
    delete_parser.add_argument("--role-name", help="Name of the role")

    args = parser.parse_args()

    # 根据 --verbose 参数设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    global logger
    logger = setup_logger('asb_pl_template', log_level)

    if args.command == "create":
        create_project(args.project_name, args.roles_path, args.role_name, args.playbook_name)
    elif args.command == "delete":
        delete_project(args.project_name, args.roles_path, args.role_name)


if __name__ == "__main__":
    main()
