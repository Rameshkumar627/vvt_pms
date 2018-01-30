# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, exceptions
from datetime import datetime
import math


class CheckGroupAccess(models.Model):
    _name = 'check.group.access'
    _description = 'Check Group Access'

    name = fields.Char(string='Name')

    def check_group_access(self, group_list):
        ''' Check if current user in the group list return True'''
        group_ids = self.env.user.groups_id
        status = False
        for group in group_ids:
            if group.name in group_list:
                status = True
        return status




