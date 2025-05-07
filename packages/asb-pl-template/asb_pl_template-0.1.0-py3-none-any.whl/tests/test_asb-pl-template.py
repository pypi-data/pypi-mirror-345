#!/usr/bin/env python
# -*- coding:utf8 -*-
import unittest
from asb_pl_template import create_project, delete_project


class TestASBPLTemplate(unittest.TestCase):
    def test_create_project(self):
        # 测试创建项目的功能
        project_name = "test_project"
        create_project(project_name)
        self.assertEqual(True, True)

    def test_delete_project(self):
        # 测试删除项目的功能
        project_name = "test_project"
        delete_project(project_name)
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
