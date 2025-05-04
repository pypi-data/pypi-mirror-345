# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class AppointmentSchedule(models.Model):
    _name = "appointment_schedule"
    _inherit = [
        "appointment_schedule",
    ]

    request_id = fields.Many2one(
        string="# Request",
        comodel_name="appointment_request",
        readonly=True,
    )

    @ssi_decorator.pre_cancel_check()
    def _check_request(self):
        self.ensure_one()
        if self.request_id:
            error_message = _(
                """
            Context: Cancel appointment schedule
            Database ID: %s
            Problem: There is appointment request associate with this schedule
            Solution: Cancel appointment request
            """
                % (self.id)
            )
            raise ValidationError(error_message)
