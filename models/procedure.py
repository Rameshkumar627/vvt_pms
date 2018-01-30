# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class Procedure(models.Model):
    _name = 'pms.procedure'
    _description = 'PMS Procedure'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', required=True)
    procedure_detail = fields.One2many(comodel_name='pms.procedure.detail',
                                       inverse_name='procedure_id',
                                       string='Procedure Detail')
    check_list = fields.One2many(comodel_name='pms.check.list',
                                 inverse_name='procedure_id',
                                 string='Check List')


class CheckList(models.Model):
    _name = 'pms.check.list'
    _description = 'PMS Check List'

    name = fields.Char(string='Check List', required=True)
    details = fields.Text(string='Detail', required=True)
    procedure_id = fields.Many2one(comodel_name='pms.procedure', string='Procedure')


class ProcedureDetail(models.Model):
    _name = 'pms.procedure.detail'
    _description = 'PMS Procedure Detail'

    name = fields.Char(string='Procedure', required=True)
    details = fields.Text(string='Detail', required=True)
    procedure_id = fields.Many2one(comodel_name='pms.procedure', string='Procedure')
