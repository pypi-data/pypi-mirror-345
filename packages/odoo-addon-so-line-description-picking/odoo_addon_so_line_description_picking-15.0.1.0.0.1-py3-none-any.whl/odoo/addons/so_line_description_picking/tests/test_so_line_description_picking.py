# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSOLineDescriptionPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "detailed_type": "product"}
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "name": "My program works!",
                        },
                    ),
                ],
            }
        )

    def test_so_line_description_picking(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids[:1]
        moves = picking.move_ids_without_package
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves.description_picking, self.sale.order_line.name)

    def test_so_line_description_picking_2_steps(self):
        self.sale.warehouse_id.delivery_steps = "pick_ship"
        self.sale.action_confirm()
        pick = self.sale.picking_ids[0]
        pick_moves = pick.move_ids_without_package
        self.assertEqual(len(pick_moves), 1)
        self.assertEqual(pick_moves.description_picking, self.sale.order_line.name)
        out = self.sale.picking_ids[1]
        out_moves = out.move_ids_without_package
        self.assertEqual(len(out_moves), 1)
        self.assertEqual(out_moves.description_picking, self.sale.order_line.name)
