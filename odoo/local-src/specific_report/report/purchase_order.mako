## -*- coding: utf-8 -*-
<html>
<head>
     <style type="text/css">
        ${css}

.list_main_table {
border:thin solid #E3E4EA;
text-align:center;
border-collapse: collapse;
}
table.list_main_table {
    margin-top: 20px;
}
.list_main_headers {
    padding: 0;
}
.list_main_headers th {
    border: thin solid #000000;
    padding-right:3px;
    padding-left:3px;
    background-color: #EEEEEE;
    text-align:center;
    font-size:12;
    font-weight:bold;
}
.list_main_table td {
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_main_lines,
.list_main_footers {
    padding: 0;
}
.list_main_footers {
    padding-top: 15px;
}
.list_main_lines td,
.list_main_footers td,
.list_main_footers th {
    text-align:left;
    font-size:12;
}

.list_main_lines td {
    border-bottom:thin solid #EEEEEE
}

.list_main_footers td {
    border: thin solid  #ffffff;
}

.list_main_footers th {
    text-align:right;
}

td .total_empty_cell {
    width: 77%;
}
td .total_sum_cell {
    width: 13%;
}

tfoot.totals tr:first-child td{
    padding-top: 15px;
}

.nobreak {
    page-break-inside: avoid;
}
caption.formatted_note {
    text-align:left;
    border-right:thin solid #EEEEEE;
    border-left:thin solid #EEEEEE;
    border-top:thin solid #EEEEEE;
    padding-left:10px;
    font-size:11;
    caption-side: bottom;
}
caption.formatted_note p {
    margin: 0;
}
.list_bank_table {
    text-align:center;
    border-collapse: collapse;
    page-break-inside: avoid;
    display:table;
}

.act_as_row {
   display:table-row;
}
.list_bank_table .act_as_thead {
    background-color: #EEEEEE;
    text-align:left;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
    white-space:nowrap;
    background-clip:border-box;
    display:table-cell;
}
.list_bank_table .act_as_cell {
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
    white-space:nowrap;
    display:table-cell;
}


.list_tax_table {
}
.list_tax_table td {
    text-align:left;
    font-size:12;
}
.list_tax_table th {
}
.list_tax_table thead {
    display:table-header-group;
}


.list_total_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_total_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px
    padding-left:3px
}
.list_total_table thead {
    display:table-header-group;
}

.right_table {
    right: 4cm;
    width:"100%";
}

.std_text {
    font-size:12;
}


td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}
.address .recipient {
    font-size: 12px;
    margin-left: 150px;
    margin-right: 120px;
    float: right;
}

.main_col1 {
    width: 10%;
}
td.main_col1 {
    text-align:left;
    vertical-align:top;
}
.main_col2 {
    width: 15%;
    vertical-align:top;
}
.main_col3 {
    width: 15%;
    text-align:center;
    vertical-align:top;
}
.main_col6 {
    width: 10%;
    vertical-align:top;
}
.main_col4 {
	width: 10%;
	text-align:right;
    vertical-align:top;
}
.main_col5 {
    width: 7%;
    text-align:left;
    vertical-align:top;
}
.main_col7 {
    width: 13%;
    vertical-align:top;
}
.main_col8 {
    width: 10%;
    vertical-align:top;
}
.main_col9 {
    width: 10%;
    vertical-align:top;
}

    </style>

</head>
<body>
    <%page expression_filter="entity"/>

    <%def name="address(partner, commercial_partner=None)">
        <%doc>
            XXX add a helper for address in report_webkit module as this won't be suported in v8.0
        </%doc>
        <% company_partner = False %>
        %if commercial_partner:
            %if commercial_partner.id != partner.id:
                <% company_partner = commercial_partner %>
            %endif
        %elif partner.parent_id:
            <% company_partner = partner.parent_id %>
        %endif

        %if company_partner:
            <tr><td class="name">${company_partner.name or ''}</td></tr>
            <tr><td>${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
            <% address_lines = partner.contact_address.split("\n")[1:] %>
        %else:
            <tr><td class="name">${partner.title and partner.title.name or ''} ${partner.name}</td></tr>
            <% address_lines = partner.contact_address.split("\n") %>
        %endif
        %for part in address_lines:
            % if part:
                <tr><td>${part}</td></tr>
            % endif
        %endfor
        <tr><td>
    </%def>

    %for purch in objects :
        <%
              quotation = purch.state == 'draft'
        %>

        <% setLang(purch.partner_id.lang) %>
        <div class="address">
            <table class="recipient">
		        ${address(partner=purch.partner_id)}
            </table>
            %if purch.company_id.partner_id:
                <table class="invoice">
                <tr><td class="address_title">${_("Invoice address:")}</td></tr>
                ${address(partner=purch.company_id.partner_id)}
                </table>
            %endif
            <br/>
            %if purch.dest_address_id:
                <table class="shipping">
                <tr><td class="address_title">${_("Shipping address:")}</td></tr>
		        ${address(partner=purch.dest_address_id)}
                </table>
            %endif
        </div>

        <h3 style="clear: both; padding-top: 20px;">
        	${quotation and _(u'Quotation N°') or _(u'Purchase Order N°') } ${purch.name}
        </h3>
        <table class="basic_table" width="100%">
            <tr>
                <th>${_("Source Document")}</th>
                <th style="text-align:center">${_("Your Order Reference")}</th>
                <th class="date">${_("Date Ordered")}</th>
                <th style="text-align:center">${_("Validated by")}</th>
            </tr>
            <tr>
                <td>${purch.name or ''}</td>
                <td style="text-align:center">${purch.partner_ref or ''}</td>
                <td class="date">${formatLang(purch.date_order, date=True)}</td>
                <td style="text-align:center">${purch.validator and purch.validator.name or ''  }</td>
            </tr>
        </table>
        <table class="list_main_table" width="100%" >
            <thead>
              <tr class="list_main_headers">
                <th class="main_col1">${_("Brand")}</th>
                <th class="main_col2">${_("Name")}</th>
                <th class="main_col3">${_("Description")}</th>
                <th class="main_col4">${_("Date Req.")}</th>
                <th style="text-align:center" class="amount main_col5">${_("Qty")}</th>
                <th class="main_col6">${_("UoM")}</th>
                <th class="amount main_col7">${_("Unit Price")}</th>
                <th class="main_col8">${_("Taxes")}</th>
                <th class="amount main_col9">${_("Net Price")}</th>
              </tr>
            </thead>
            <tbody>
            <%
              total_qty = 0
            %>
            %for line in purch.order_line :
              <%
                total_qty += line.product_qty
              %>
              <tr class="list_main_lines">
                <td class="main_col1">${line.product_id.brand or '' | n}</td>
                <td class="main_col2">${"%s - %s" % (line.product_id.name or '', line.product_id.variants or '')}</td>
                <td class="main_col3">${line.product_id.default_code or '' | n}</td>
                <td style="text-align:center" class="main_col5">${formatLang(line.date_planned, date=True)}</td>
                <td class="amount main_col5">${line.product_qty}</td>
                <td class="main_col6">${line.product_uom.name}</td>
                <td class="amount main_col7">${formatLang(line.price_unit, digits=get_digits(dp='Purchase Price'))}</td>
                <td style="text-align:center" class="main_col8">${ ', '.join([ tax.name or '' for tax in line.taxes_id ])}</td>
                <td class="amount main_col9">${formatLang(line.price_subtotal, digits=get_digits(dp='Purchase Price'))} ${purch.pricelist_id.currency_id.symbol}</td>
              </tr>
           %endfor
            </tbody>
	      <tfoot class="totals">
            <tr class="list_main_footers">
                <td colspan="3" class="total_empty_cell"/>
              <td style="font-weight:bold; text-align: right">
                ${_("Quantity :")}
              </td>
              <td class="amount total_sum_cell">
                ${total_qty}
              </td>
                <td colspan="2" class="total_empty_cell"/>
              <td style="font-weight:bold; text-align: right">
                ${_("Net :")}
              </td>
              <td class="amount total_sum_cell">
                ${formatLang(purch.amount_untaxed, digits=get_digits(dp='Purchase Price'))} ${purch.pricelist_id.currency_id.symbol}
              </td>
            </tr>
            <tr class="list_main_footers">
              <td colspan="7" class="total_empty_cell"/>
              <td style="font-weight:bold; text-align: right">
                ${_("Taxes:")}
              </td>
              <td class="amount total_sum_cell">
                ${formatLang(purch.amount_tax, digits=get_digits(dp='Purchase Price'))} ${purch.pricelist_id.currency_id.symbol}
              </td>
            </tr>
            <tr class="list_main_footers">
              <td colspan="7" class="total_empty_cell"/>
              <td style="font-weight:bold; text-align: right">
                ${_("Total:")}
              </td>
              <td class="amount total_sum_cell">
                ${formatLang(purch.amount_total, digits=get_digits(dp='Purchase Price'))} ${purch.pricelist_id.currency_id.symbol}
              </td>
            </tr>
      </tfoot>
    </table>
    %if purch.warehouse_id:
        <p style="page-break-after:always"/>
        <br/>
        <div>
            <br/>
            <p><b>Information pour la livraison</b></p>
        
        %if purch.warehouse_id.name == 'QoQa Services SA':
            <p>Contacts logistique QoQa : Serkan Kilinc</p>
            <p>Téléphone : 021/633.20.83</p>
            <p>e-mail : logistique@qoqa.ch</p>
            <p>Heures d’ouverture : 8h-12h et 13h30-17h30</p>
            <p>Hauteur minimum du véhicule pour livraison : 70cm</p>
            <p>Hauteur max palettes : 220cm</p>

            <p>Plan d'accès :</p>
            <br/>
            ${helper.embed_logo_by_name('plan_acces', width=550)|n}
        %elif purch.warehouse_id.name == 'Poste Daillens':
            <p>Merci de contacter Sylvain Ecoffey, Responsable d’exploitation pour les livraisons et informations supplémentaires.</p>
            <br/>
            <p>Poste CH SA</p>
            <p>PostLogistics</p>
            <p>Centre logistique</p>
            <p>Z.I. Les Graveys</p>
            <p>CH-1306 Daillens</p>
            <br/>
            <p>Portable : +41 (0)79 606 22 28</p>
            <p>E-Mail : sylvain.ecoffey@poste.ch</p>
            <p>Info logistique team: cld.sav.stockage@post.ch</p>
        %elif purch.warehouse_id.name == 'Poste Dintikon':
            <p>Merci de contacter Sylvain Ecoffey, Responsable d’exploitation pour les livraisons et informations supplémentaires.</p>
            <p>Pour la livraison des gros articles de plus de 30 kg (sèche-linge, imprimantes, TV, appareils de fitness,...).</p>
            <br/>
            <p>PostLogistics SA</p>
            <p>Service de montage</p>
            <p>Lagerstrasse 12</p>
            <p>5606 Dintikon</p>
            <br/>
            <p>Portable : +41 (0)79 606 22 28</p>
            <p>E-Mail : sylvain.ecoffey@poste.ch</p>
            <p>Info logistique team: cld.sav.stockage@post.ch</p>
        %endif
        </div>
    %endif
        
%endfor
</body>
</html>