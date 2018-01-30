# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import datetime


PROGRESS_INFO = [('draft', 'Draft'), ('noted', 'Noted')]


class Notes(models.Model):
    _name = 'pms.note'
    _description = 'PMS Note'
    _inherit = 'mail.thread'

    date = fields.Date(string='Date')
    name = fields.Char(string='Name')
    noted_by = fields.Many2one(comodel_name='res.users', string='Noted By')
    progress = fields.Selection(PROGRESS_INFO, default='draft')
    attachment_detail = fields.One2many(comodel_name='note.detail',
                                        inverse_name='note_id')
    comment = fields.Text(string='Comment')

    @api.multi
    def trigger_noted(self):
        data = {'progress': 'noted'}
        self.write(data)


class NotesDetail(models.Model):
    _name = 'note.detail'
    _description = 'Notes Detail'
    _inherit = 'mail.thread'

    attachment = fields.Binary(string='Attachment')
    comment = fields.Text(string='Comment')
    note_id = fields.Many2one(comodel_name='pms.note', string='Note')
    task_id = fields.Many2one(comodel_name='pms.task', string='Task')

    current_date = fields.Datetime(string='Current Time',
                                   compute='_get_current_time',
                                   store=False,
                                   track_visibility='always')
    current_user = fields.Many2one(comodel_name='res.users',
                                   compute='_get_current_user',
                                   store=False,
                                   string='Assigned To')

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user.id

    def _get_current_time(self):
        for rec in self:
            rec.current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

