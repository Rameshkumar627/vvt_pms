# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import datetime


PROGRESS_INFO = [('draft', 'Draft'),
                 ('assigned', 'Assigned'),
                 ('developed', 'Developing'),
                 ('completed', 'Completed'),
                 ('cancelled', 'Cancelled')]


class Task(models.Model):
    _name = 'pms.task'
    _description = 'PMS Task'
    _inherit = 'mail.thread'
    _rec_name = 'task'

    date = fields.Date(string='Date', required=True)
    sequence = fields.Char(string='Sequence', readonly=True)
    task = fields.Char(string='Task', required=True)
    parent_task = fields.Many2one(comodel_name='pms.task', string='Parent Task')
    assigned_to = fields.Many2one(comodel_name='res.users', string='Assigned To', required=True)
    procedure = fields.Many2many(comodel_name='pms.procedure', string='Procedure')
    task_detail = fields.Html(string='Task Detail', required=True)
    solution = fields.Html(string='Solution')
    attachment = fields.One2many(comodel_name='note.detail', inverse_name='task_id')
    comment = fields.Text(string='Comment', track_visibility='always')

    progress = fields.Selection(PROGRESS_INFO, string='Progress', default='draft', track_visibility='always')

    task_start = fields.Datetime(string='Task Start', readonly=True)
    task_end = fields.Datetime(string='Task End', readonly=True)
    current_date = fields.Datetime(string='Current Time',
                                   compute='_get_current_time',
                                   store=False,
                                   track_visibility='always')
    current_user = fields.Many2one(comodel_name='res.users',
                                   compute='_get_current_user',
                                   store=False,
                                   string='Assigned To')

    @api.multi
    def trigger_start(self):
        obj = self.env['pms.time']
        data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'employee_id': self.env.user.id,
            'progress': 'start',
            'task_id': self.id
        }
        obj.create(data)

    @api.multi
    def trigger_stop(self):
        obj = self.env['pms.time']
        data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            'employee_id': self.env.user.id,
            'progress': 'stop',
            'task_id': self.id
        }
        obj.create(data)

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user.id

    def _get_current_time(self):
        for rec in self:
            rec.current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def check_rights(self):
        group_list = []
        if self.progress in ['draft', False]:
            group_list = ['VVTI Project - Team Leader', 'VVTI Project - Administrator']
        elif self.progress == 'assigned':
            group_list = ['VVTI Project - User', 'VVTI Project - Administrator']
        elif self.progress == 'developed':
            group_list = ['VVTI Project - User', 'VVTI Project - Administrator']

        outer_obj = self.env['check.group.access'].browse([('id', '=', 1)])
        if not outer_obj.check_group_access(group_list):
            raise exceptions.ValidationError('Error! You are not authorised to change this record')

    @api.multi
    def trigger_assigned(self):
        if not self.assigned_to:
            raise exceptions.ValidationError('Error! Need Assigned To:')
        data = {'progress': 'assigned',
                'task_start': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'sequence': self.env['ir.sequence'].sudo().next_by_code('pms.task')}

        self.write(data)

    @api.multi
    def trigger_cancelled(self):
        if not self.comment:
            raise exceptions.ValidationError('Error! Need Comment')
        data = {'progress': 'cancelled'}
        self.write(data)

    @api.multi
    def trigger_developed(self):
        if not self.procedure:
            if not self.solution:
                raise exceptions.ValidationError('Error! Need solution')
        data = {'progress': 'developed'}
        self.write(data)

    @api.multi
    def trigger_completed(self):
        data = {'progress': 'completed',
                'task_end': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
        self.write(data)

    def write(self, vals):
        self.check_rights()
        return super(Task, self).write(vals)

    def unlink(self):
        raise exceptions.ValidationError('Error! You are not authorised to delete this record')

    @api.model
    def create(self, val):
        self.check_rights()
        val['date'] = datetime.now().strftime('%Y-%m-%d')
        return super(Task, self).create(val)


class TimeSheet(models.Model):
    _name = 'pms.time'
    _description = 'PMS Time'

    date = fields.Datetime(string='Date', required=True)
    employee_id = fields.Many2one(comodel_name='res.users', string='Employee', required=True)
    progress = fields.Selection([('start', 'Start'), ('stop', 'STOP')], string='Progress', required=True)
    task_id = fields.Many2one(comodel_name='pms.task', string='Task', required=True)
