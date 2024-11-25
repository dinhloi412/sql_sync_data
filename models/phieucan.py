# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError


class Weightman(models.Model):
    _name = "weightman"
    _description = "Phiếu cân phần mềm cân"
    _order = 'id'      

    name = fields.Char("Name", compute='_compute_name', store=True)
    @api.depends('warehouse_id','docnum','truckno')
    def _compute_name(self):
        for rec in self:  
            name = ''
            if rec.warehouse_id:
                name += str(rec.warehouse_id.name)

            if rec.docnum:
                name = name + " - " + str(rec.docnum)
            
            if rec.truckno:
                name = name + " - " + str(rec.truckno)

            rec.name = name

    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements") 
    active = fields.Boolean("Active", default=True)

    warehouse_id = fields.Many2one('stock.warehouse', string='Kho xuất') 

    docnum = fields.Char('docnum')
    truckno = fields.Char('truckno')
    prodname = fields.Char('prodname')
    custname = fields.Char('custname')
    date_in = fields.Date(string='date_in') 
    date_out = fields.Date(string='date_out') 
    firstweight = fields.Integer(string='firstweight')    
    secondweight = fields.Integer(string='secondweight')    
    netweight = fields.Integer(string='netweight')    
    note = fields.Char('note')
    trantype = fields.Char('trantype')
    prodcode = fields.Char('prodcode')
    custcode = fields.Char('custcode')
    time_in = fields.Char(string='time_in')
    time_out = fields.Char(string='time_out')
    date_time = fields.Datetime(string='date_time') 
    sobao = fields.Integer(string='sobao')  
    tlbao = fields.Integer(string='tlbao')  
    tlbi = fields.Integer(string='tlbi')  
    tlthucte = fields.Integer(string='tlthucte')  
    status = fields.Char('status')

