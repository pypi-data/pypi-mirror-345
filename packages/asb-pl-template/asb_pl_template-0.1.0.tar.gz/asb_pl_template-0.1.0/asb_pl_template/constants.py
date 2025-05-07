#!/usr/bin/env python3
# -*- coding:utf8 -*-

# 定义项目结构模板
PROJECT_TEMPLATE = {
    'README.md': '# {project_name}\n\nThis is a description of the {project_name} project.',
    'ansible.cfg': '[defaults]\n# Add your ansible configuration here',
    'hosts': '# Add your production hosts here\n [prod]\n# Add your staging hosts here\n [stage]\n# Add your local hosts here\n [local]\nlocalhost ansible_connection=local',
    'group_vars': {
        'main.yml': '# Common variables for all environments',
        'local.yml': '# Variables for local development',
        'prod.yml': '# Variables for production environment',
        'stage.yml': '# Variables for staging environment'
    },
    'host_vars': {
        'prod.yml': '# Variables for production hosts',
        'stage.yml': '# Variables for staging hosts'
    },
    'library': {},
    'requirements.yml': '# List your role dependencies here',
    'playbooks': {
        'site.yml': '# Main playbook\n - hosts: all\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-local.yml': '# Playbook for local development\n - hosts: local\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-prod.yml': '# Playbook for production environment\n - hosts: prod\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-stage.yml': '# Playbook for staging environment\n - hosts: stage\n   roles:\n     - role: common\n     - role: web\n     - role: database'
    },
    'inventories': {
        'prod': {
            'group_vars': {},
            'host_vars': {},
            'inventory': '# Production inventory file'
        },
        'stage': {
            'group_vars': {},
            'host_vars': {},
            'inventory': '# Staging inventory file'
        }
    },
    'roles': {},
    'tests': {
        'test.yml': '# Playbook for testing'
    }
}

# 定义角色结构模板
ROLE_TEMPLATE = {
    'tasks': {
        'main.yml': '- name: Main tasks\n  debug:\n    msg: "This is the main task"'
    },
    'handlers': {
        'main.yml': '- name: Main handlers\n  debug:\n    msg: "This is the main handler"'
    },
    'templates': {
        'ntp.conf.j2': '# NTP configuration template'
    },
    'files': {
        'bar.txt': 'This is a sample text file',
        'foo.sh': '#!/bin/bash\n# This is a sample script'
    },
    'vars': {
        'main.yml': '# Variables for this role'
    },
    'defaults': {
        'main.yml': '# Default variables for this role'
    },
    'meta': {
        'main.yml': '# Role dependencies'
    }
}
