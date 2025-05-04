# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class AppointmentRequest(models.Model):
    _name = "appointment_request"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
    ]
    _description = "Appointment Request"
    _order = "date"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    _statusbar_visible_label = "draft,confirm,open,done"

    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "open_ok",
        "restart_approval_ok",
        "cancel_ok",
        "terminate_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_done",
        "dom_terminate",
        "dom_cancel",
        "dom_reject",
    ]

    _create_sequence_state = "open"

    title = fields.Char(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="-",
    )
    partner_id = fields.Many2one(
        string="Contact",
        comodel_name="res.partner",
        domain=[
            ("is_company", "=", False),
            ("parent_id", "!=", False),
        ],
        ondelete="restrict",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    commercial_partner_id = fields.Many2one(
        string="Commercial Contact",
        comodel_name="res.partner",
        related="partner_id.commercial_partner_id",
        store=True,
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="appointment_type",
        ondelete="restrict",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_appointee_ids = fields.Many2many(
        string="Allowed Appointee on Request",
        comodel_name="res.users",
        related="type_id.allowed_appointee_ids",
        store=False,
    )
    appointee_id = fields.Many2one(
        string="Appointee",
        comodel_name="res.users",
        required=False,
        readonly=True,
        states={
            "open": [
                ("readonly", False),
            ],
        },
    )
    appointment_method = fields.Selection(
        string="Method",
        selection=[
            ("online", "Online"),
            ("offline", "Offline"),
        ],
        copy=False,
        default="online",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.model
    def _default_date(self):
        return fields.Date.today()

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self._default_date(),
    )
    date_offset = fields.Integer(
        string="Days Offset",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_appointment_ids = fields.Many2many(
        string="Allowed Appointments",
        comodel_name="appointment_schedule",
        compute="_compute_allowed_appointment_ids",
        store=False,
    )
    appointment_id = fields.Many2one(
        string="# Appointment",
        comodel_name="appointment_schedule",
        readonly=True,
        states={
            "open": [
                ("readonly", False),
            ],
        },
    )
    appointment_date = fields.Date(
        string="Appointment Date",
        related="appointment_id.date",
        readonly=True,
        store=True,
    )
    appointment_time_slot_id = fields.Many2one(
        string="Appointment Time Slot",
        comodel_name="appointment_time_slot",
        related="appointment_id.time_slot_id",
        store=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "Waiting for Schedule"),
            ("done", "Schedule"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        copy=False,
        default="draft",
        required=True,
        readonly=True,
    )

    @api.depends(
        "type_id",
        "appointee_id",
        "date",
        "date_offset",
        "state",
    )
    def _compute_allowed_appointment_ids(self):
        Schedule = self.env["appointment_schedule"]
        for document in self:
            result = []
            if document.date and document.state == "open":
                date_min = document.date
                date_min = date_min + relativedelta(days=document.date_offset)
                criteria = [
                    ("date", ">=", date_min),
                    ("state", "=", "ready"),
                    ("partner_id", "=", False),
                ]
                if document.type_id:
                    criteria.append(
                        ("type_ids", "in", document.type_id.id),
                    )
                if document.appointee_id:
                    criteria.append(
                        ("appointee_id", "=", document.appointee_id.id),
                    )
                result = Schedule.search(criteria).ids
            document.allowed_appointment_ids = result

    @api.model
    def _get_policy_field(self):
        res = super(AppointmentRequest, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "open_ok",
            "done_ok",
            "cancel_ok",
            "restart_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.onchange(
        "type_id",
    )
    def onchange_date_offset(self):
        self.date_offset = 0
        if self.type_id:
            self.date_offset = self.type_id.request_date_offset

    @api.onchange(
        "type_id",
    )
    def onchange_appointee_id(self):
        self.appointee_id = False

    @ssi_decorator.post_done_action()
    def _update_open_appointment_schedule(self):
        self.ensure_one()
        self.appointment_id.write(self._prepare_update_open_appointment_schedule())
        partner_ids = self.message_follower_ids.mapped("partner_id.id")
        self.appointment_id.message_subscribe(partner_ids=partner_ids)

    def _prepare_update_open_appointment_schedule(self):
        self.ensure_one()
        return {
            "type_id": self.type_id.id,
            "partner_id": self.partner_id.id,
            "title": self.title,
            "request_id": self.id,
        }

    @ssi_decorator.post_cancel_action()
    def _update_ready_appointment_schedule(self):
        self.ensure_one()
        self.appointment_id.write(self._prepare_update_ready_appointment_schedule())
        self.appointment_id.action_ready()
        appointment = self.appointment_id
        partners = (
            appointment.message_follower_ids.mapped("partner_id")
            - appointment.user_id.partner_id
            - appointment.appointee_id.partner_id
        )
        partner_ids = partners.ids
        appointment.message_unsubscribe(partner_ids=partner_ids)
        self.write(
            {
                "appointment_id": False,
            }
        )
        partner_ids = (
            appointment.user_id.partner_id + appointment.appointee_id.partner_id
        ).ids
        appointment.message_subscribe(partner_ids=partner_ids)

    def _prepare_update_ready_appointment_schedule(self):
        self.ensure_one()
        return {
            "type_id": False,
            "partner_id": False,
            "title": "-",
            "appointment_invitation_link": False,
            "request_id": False,
        }
