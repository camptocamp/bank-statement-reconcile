# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from itertools import islice, groupby
from collections import namedtuple
from openerp.osv import orm, fields
from openerp.tools.translate import _


# packs: list of packs
# group: boolean, True means that all the packs are identical
# leftover: means it is the result of grouping all the leftovers
# leftover_size: quantity of products in the packs of the leftover
# dispatch (leftovers are grouped by quantity of products
PreparedDispatch = namedtuple('PreparedDispatch',
                              'packs group leftover leftover_size')


class picking_dispatch_group(orm.TransientModel):
    _name = 'picking.dispatch.group'
    _description = 'Picking Dispatch Grouping'

    _columns = {
        'pack_limit': fields.integer(
            'Number of packs',
            help='The number of packs per dispatch will be limited to this '
                 'quantity. Leave 0 to set no limit.'),
        'pack_limit_apply_threshold': fields.boolean(
            'No limit for 1 unit',
            help='The limit is not applied when the packs contains '
                 'only 1 unit. Does only apply to '
                 'the dispatches grouped with similar content.'),
        'only_product_ids': fields.many2many(
            'product.product',
            string='Filter on products',
            help='Dispatches will be created only if the content of the '
                 'pack contains exactly the same products than selected '
                 '(without consideration for the quantity).\n'
                 'No filter is applied when no product is selected.'),
        'group_by_content': fields.boolean(
            'Group By Content',
            help='Packs with similar content will be grouped in '
                 'the same dispatch'),
        'group_leftovers': fields.boolean(
            'Group Leftovers',
            help='Leftovers are dispatches generated and containing a '
                 'number of packs below a threshold. This option will '
                 'group them all in a final dispatch'),
        'group_leftovers_threshold': fields.integer(
            'Threshold',
            help='Generated dispatches are considered as leftovers when '
                 'they have a less or equal number of packs than the '
                 'threshold.\n'
                 'With the default value of 1, the dispatches with 1 pack '
                 'will be grouped in a final dispatch.'),
        'suffix': fields.char('Suffix'),
    }

    _defaults = {
        'pack_limit_apply_threshold': True,
        'group_by_content': True,
        'group_leftovers': True,
        'group_leftovers_threshold': 1,
    }

    _sql_constraints = [
        ('pack_limit_number', 'CHECK (pack_limit >= 0)',
         'The pack limit must be equal or above 0.'),
        ('group_leftovers_threshold_number',
         'CHECK (group_leftovers_threshold >= 1)',
         'The Leftovers threshold must be above 0.'),
    ]

    def _picking_to_pack_ids(self, cr, uid, picking_ids, context=None):
        """ Get the pack ids from picking ids """
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid,
                                   [('picking_id', 'in', picking_ids)],
                                   context=context)
        moves = move_obj.read(cr, uid, move_ids, ['tracking_id'],
                              context=context)
        pack_ids = (move['tracking_id'][0] for move in moves
                    if move['tracking_id'])
        return list(set(pack_ids))

    @staticmethod
    def chunks(iterable, size):
        """ Chunk iterable to n parts of size `size` """
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, size))
            if not chunk:
                return
            yield chunk

    def _filter_packs(self, cr, uid, wizard, packs, context=None):
        """ Filter the packs. Their content should equal to the filter """
        # exclude packs that are in canceled or done pickings
        packs = (pack for pack in packs if
                 not any(move.picking_id.state in ('cancel', 'done')
                         for move in pack.move_ids))
        # exclude packs without moves
        packs = (pack for pack in packs if pack.move_ids)
        # exclude packs when an least one move is already in a dispatch
        packs = [pack for pack in packs if
                 not any(move.dispatch_id for move in pack.move_ids)]
        if not wizard.only_product_ids:
            return packs
        filter_product_ids = set(pr.id for pr in wizard.only_product_ids)
        keep = []
        for pack in packs:
            product_ids = set(move.product_id.id for move in pack.move_ids)
            if product_ids != filter_product_ids:
                continue
            keep.append(pack)
        return keep

    @staticmethod
    def _pack_sort_key(pack):
        """ Sort key used for the grouping of the packs """
        # sort the moves so they are compared equally,
        # e.g. avoid to compare [(1, 10), (2, 20)] vs [(2, 20), (1, 10)]
        sorted_moves = sorted(pack.move_ids,
                              key=lambda m: (m.product_id.id,
                                             m.product_qty,
                                             m.product_uom.id))
        return [(move.product_id.id, move.product_qty, move.product_uom.id) for
                move in sorted_moves]

    def _group_by_content(self, cr, uid, wizard, packs, context=None):
        """ Group the packs by the equality of their content """
        if wizard.group_by_content:
            packs = sorted(packs, key=self._pack_sort_key)
            for _content, gpacks in groupby(packs, self._pack_sort_key):
                yield PreparedDispatch(list(gpacks), group=True,
                                       leftover=False, leftover_size=None)
        else:
            # one dispatch with all the packs
            yield PreparedDispatch(packs, group=False,
                                   leftover=False, leftover_size=None)

    def _split_dispatches_to_limit(self, cr, uid, wizard, dispatches,
                                   context=None):
        """ Split the dispatches having a count of packs above the limit

        Threshold should not be applied when a dispatch has packs
        of disparate content.  The content is the same when the option
        group_by_content is used and the dispatch is not a leftover

        """
        pack_limit = wizard.pack_limit
        threshold = wizard.pack_limit_apply_threshold
        for packs, group, leftover, leftover_size in dispatches:
            # only make sense for groups when all the packs have the
            # same content
            if group and threshold:
                first_pack = packs[0]
                # ignore the limit when below the threshold
                if (len(first_pack.move_ids) == 1 and
                        first_pack.move_ids[0].product_qty == 1):
                    yield PreparedDispatch(packs, group=group,
                                           leftover=leftover,
                                           leftover_size=leftover_size)
                    continue
            if pack_limit:
                for chunk in self.chunks(packs, pack_limit):
                    yield PreparedDispatch(chunk, group=group,
                                           leftover=leftover,
                                           leftover_size=leftover_size)
            else:
                yield PreparedDispatch(packs, group=group,
                                       leftover=leftover,
                                       leftover_size=leftover_size)

    def _dispatch_leftovers(self, cr, uid, wizard, dispatches, context=None):
        """ Find the leftovers dispatches and group them in a final dispatch.

        Leftovers are dispatches containing less packs than a defined
        threshold (1 by default).  The leftovers may be grouped in one
        (or several when using a limit of packs per dispatch) dispatch
        to avoid having one dispatch for each unique pack.

        """
        group_leftovers = wizard.group_leftovers
        threshold = wizard.group_leftovers_threshold
        leftovers_packs = []
        for packs, group, leftover, leftover_size in dispatches:
            if group_leftovers:
                if len(packs) <= threshold:
                    leftovers_packs += packs
                else:
                    yield PreparedDispatch(packs, group=group,
                                           leftover=leftover,
                                           leftover_size=leftover_size)
            else:
                yield PreparedDispatch(packs, group=group,
                                       leftover=leftover,
                                       leftover_size=leftover_size)

        if leftovers_packs:
            yield PreparedDispatch(leftovers_packs, group=False,
                                   leftover=True, leftover_size=None)

    @staticmethod
    def _leftovers_sort_key(pack):
        """ Used to split leftover dispatches according to the quantity
        of products.
        """
        return sum(move.product_qty for move in pack.move_ids)

    def _group_leftovers(self, cr, uid, wizard, dispatches, context=None):
        """ Group leftovers by number of products.

        The leftovers are packs of mixed content and it would help if
        packs are grouped by total quantity of product in leftovers so
        dispatches have all the same quantity of products.

        """
        leftovers = []
        for prepared_dispatch in dispatches:
            if not prepared_dispatch.leftover:
                yield prepared_dispatch
                continue
            packs = sorted(prepared_dispatch.packs,
                           key=self._leftovers_sort_key)
            for qty, gpacks in groupby(packs, self._leftovers_sort_key):
                dispatch = PreparedDispatch(
                    list(gpacks), group=prepared_dispatch.group,
                    leftover=prepared_dispatch.leftover,
                    leftover_size=qty)
                # we must re-apply the limit on the leftovers
                split = self._split_dispatches_to_limit(cr, uid, wizard,
                                                        [dispatch],
                                                        context=context)
                for prepared_dispatch in split:
                    leftovers.append(prepared_dispatch)
        if leftovers:
            # one more time, but only on the leftovers, so if dispatches
            # have been generated below the threshold, we group them
            # again in a "leftover of leftovers".
            leftovers = self._dispatch_leftovers(cr, uid, wizard, leftovers,
                                                 context=context)
            leftovers = self._split_dispatches_to_limit(cr, uid, wizard,
                                                        leftovers,
                                                        context=context)
            for prepared_dispatch in leftovers:
                yield prepared_dispatch

    def _create_dispatch(self, cr, uid, wizard, vals, packs, context=None):
        """ Create a dispatch for packs """
        move_obj = self.pool['stock.move']
        dispatch_obj = self.pool['picking.dispatch']
        move_ids = [move.id for pack in packs for move in pack.move_ids]
        dispatch_id = dispatch_obj.create(cr, uid, vals, context=context)
        move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id},
                       context=context)
        return dispatch_id

    def _prepare_dispatch_vals(self, cr, uid, wizard, prepared_dispatch,
                               context=None):
        name = self.pool['ir.sequence'].get(cr, uid, 'picking.dispatch')
        nb_packs = len(prepared_dispatch.packs)
        if not (prepared_dispatch.group or prepared_dispatch.leftover):
            descr = _('%d packs of mixed content') % nb_packs
        # a grouped leftover should not happen
        elif prepared_dispatch.leftover:
            size = prepared_dispatch.leftover_size
            if size is None:
                descr = (_('%d packs of leftovers with various units') %
                         (nb_packs))
            else:
                descr = (_('%d packs of leftovers with %s units') %
                         (nb_packs, size))
        elif prepared_dispatch.group:
            prods = [_("%sx[%s]") % (move.product_qty,
                                     move.product_id.default_code)
                     for move in prepared_dispatch.packs[0].move_ids]
            descr = _('%d packs grouped by: %s') % (nb_packs,
                                                    ' + '.join(prods))

        name = ' - '.join([part for part in (name, wizard.suffix, descr)
                           if part])
        vals = {'name': name}
        return vals

    def _read_packs(self, cr, uid, wizard, pack_ids, context=None):
        pack_obj = self.pool['stock.tracking']
        return pack_obj.browse(cr, uid, pack_ids, context=context)

    def _group_packs(self, cr, uid, wizard, pack_ids, context=None):
        """ Split a set of packs in many dispatches according to rules """
        packs = self._read_packs(cr, uid, wizard, pack_ids, context=context)
        packs = self._filter_packs(cr, uid, wizard, packs, context=context)
        if not packs:
            return []
        dispatches = self._group_by_content(cr, uid, wizard, packs,
                                            context=context)
        dispatches = self._split_dispatches_to_limit(cr, uid, wizard,
                                                     dispatches,
                                                     context=context)
        # done after the split because the split can create new
        # leftovers by leaving a pack alone in a picking dispatch
        dispatches = self._dispatch_leftovers(cr, uid, wizard, dispatches,
                                              context=context)
        dispatches = self._group_leftovers(cr, uid, wizard, dispatches,
                                           context=context)

        created_ids = []
        for prepared_dispatch in dispatches:
            vals = self._prepare_dispatch_vals(cr, uid, wizard,
                                               prepared_dispatch,
                                               context=context)
            dispatch_id = self._create_dispatch(cr, uid, wizard, vals,
                                                prepared_dispatch.packs,
                                                context=context)
            created_ids.append(dispatch_id)
        return created_ids

    def group(self, cr, uid, ids, context=None):
        """ Public method to use the wizard.

        Can be used from Delivery Orders or Packs.
        When used with Delivery Orders, it consumes all the packs
        of the selected delivery orders.

        """
        if context is None:
            context = {}
        if isinstance(ids, (tuple, list)):
            assert len(ids) == 1, "expect 1 ID, got %s" % ids
            ids = ids[0]
        model = context.get('active_model')
        assert model in ('stock.picking.out', 'stock.tracking'), \
            "unexpected 'active_model', got %s" % model
        assert context.get('active_ids'), "'active_ids' required"
        pack_ids = context['active_ids']
        if model == 'stock.picking.out':
            pack_ids = self._picking_to_pack_ids(cr, uid, pack_ids,
                                                 context=context)
        wizard = self.browse(cr, uid, ids, context=context)
        dispatch_ids = self._group_packs(cr, uid, wizard, pack_ids,
                                         context=context)
        return {
            'domain': "[('id', 'in', %s)]" % dispatch_ids,
            'name': _('Generated Dispatches'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'picking.dispatch',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }