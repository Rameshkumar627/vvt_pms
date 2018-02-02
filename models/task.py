# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import datetime
import xmlrpclib
import os

url = 'http://10.0.5.11:8095'
db = 'vvti_v_7'
username = 'admin'
password = 'admin'

sock_common = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(url))
uid = sock_common.login(db, username, password)

sock = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))

py_template_string = '''# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import datetime


class {0}(models.Model)
    _name = '{1}'
    _description = '{2}'

{3}
        '''

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


class RamV(models.Model):
    _name = 'ra.ra'

    name = fields.Char(string='Name')

    py_template = fields.Text(string='Py Template', default=py_template_string)
    directory = fields.Char(string='Directory', default="/home/sarpam/vvti_program/models")
    field_binary = fields.Text(string='Binary', default="{0} = fields.Binary(string='{1}', required={2}, readonly={3})")
    field_boolean = fields.Text(string='Boolean', default="{0} = fields.Boolean(string='{1}', required={2}, readonly={3})")
    field_char = fields.Text(string='Char', default="{0} = fields.Char(string='{1}', required={2}, readonly={3})")
    field_date = fields.Text(string='Date', default="{0} = fields.Date(string='{1}', required={2}, readonly={3})")
    field_datetime = fields.Text(string='Date Time', default="{0} = fields.Datetime(string='{1}', required={2}, readonly={3})")
    field_float = fields.Text(string='Float', default = "{0} = fields.Float(string='{1}', required={2}, readonly={3})")
    field_integer = fields.Text(string='Integer', default="{0} = fields.Integer(string='{1}', required={2}, readonly={3})")
    field_html = fields.Text(string='Html', default="{0} = fields.Html(string='{1}', required={2}, readonly={3})")
    field_many2one = fields.Text(string='Many2one', default="{0} = fields.Many2one(comodel_name='{1}', string='{2}' ,required={3}, readonly={4})")
    field_many2many = fields.Text(string='Many2many', default="{0} = fields.Many2many(comodel_name='{1}', inverse_name='{2}', string='{3}' ,required={4}, readonly={5})")
    field_one2many = fields.Text(string='One2many', default="{0} = fields.Many2many(comodel_name='{1}', inverse_name='{2}', string='{3}' ,required={4}, readonly={5})")
    field_selection = fields.Text(string='Selection', default="{0} = fields.Selection(selection={1}, string='{2}', required={3}, readonly={4})")
    field_text = fields.Text(string='Text', default="{0} = fields.Text(string='{1}', required={2}, readonly={3})")

    def model_data(self, model_id):
        ir_model = sock.execute_kw(db,
                                   uid,
                                   password,
                                   'ir.model',
                                   'read',
                                   [model_id],
                                   {'fields': ['name', 'model']})

        class_name = ir_model['model']
        model_name = ir_model['model'].title().replace(".", "")
        model_description = ir_model['name'].title().replace(".", " ")
        model_file = ir_model['model'].lower().replace(".", "_")

        return model_name, class_name, model_description, model_file

    def field_vals_data(self, model_id):

        field_ids = sock.execute_kw(db, uid, password,
                                    'ir.model.fields', 'search',
                                    [[['model_id', '=', model_id]]])

        fields_vals = None
        error = False

        for ids in field_ids:
            data = None
            rec = sock.execute_kw(db, uid, password,
                                  'ir.model.fields', 'read',
                                  [ids],
                                  {'fields': ['name',
                                              'field_description',
                                              'ttype',
                                              'relation',
                                              'relation_field',
                                              'selection',
                                              'domain',
                                              'required',
                                              'readonly',
                                              'on_delete']})

            if rec['ttype'] == 'binary':
                data = self.field_binary.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'boolean':
                data = self.field_boolean.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'char':
                data = self.field_char.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'date':
                data = self.field_date.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'datetime':
                data = self.field_datetime.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'float':
                data = self.field_float.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'html':
                data = self.field_html.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'integer':
                data = self.field_integer.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'many2one':
                data = self.field_many2one.format(
                    rec['name'],
                    rec['relation'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'one2many':
                data = self.field_one2many.format(
                    rec['name'],
                    rec['relation'],
                    rec['relation_field'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'many2many':
                data = self.field_many2many.format(
                    rec['name'],
                    rec['relation'],
                    rec['relation_field'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'selection':
                data = self.field_selection.format(
                    rec['name'],
                    rec['selection'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            elif rec['ttype'] == 'text':
                data = self.field_text.format(
                    rec['name'],
                    rec['field_description'],
                    rec['required'],
                    rec['readonly'])

            else:
                error = True

            if fields_vals:
                fields_vals = "{0}\n    {1}".format(fields_vals, data)
            else:
                fields_vals = "    {0}".format(data)

        return fields_vals, error

    def file_creation(self, template, model_file, error):
        if error:
            model_location = 'Error_{0}/{1}.py'.format(self.directory, model_file)
        else:
            model_location = '{0}/{1}.py'.format(self.directory, model_file)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(model_location, 'w+') as model_file:
            model_file.write(template)

    def trigger_noted(self):

        model_id = 299
        template = self.py_template
        model_name, class_name, model_description, model_file = self.model_data(model_id)
        fields_vals, error = self.field_vals_data(model_id)
        file_data = template.format(model_name, class_name, model_description, fields_vals)

        self.file_creation(file_data, model_file, error)
