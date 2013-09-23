# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@qoqa_ch @core_setup

Feature: Configure QoQa.ch

  @company_ch
  Scenario: Configure main partner and company
  Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
         | key        | value                      |
         | name       | QoQa Services SA           |
         | street     | Rue de l'Arc-en-Ciel 14    |
         | street2    |                            |
         | zip        | 1030                       |
         | city       | Bussigny-Lausanne          |
         | country_id | by code: CH                |
         | phone      | +41 21 633 20 80           |
         | fax        | +41 21 633 20 81           |
         | email      | contact@qoqa.ch            |
         | website    | http://www.qoqa.ch         |
         | parent_id  | by oid: base.main_company  |
         | vat              | FR 09 439922741                  |
         | company_registry | 439 922 741                      |
         | siret            | 439 922 741 00020                |
         | ape              | 4669 A                           |
         # temporary way of filling rml_header to change to position of header separator
         | rml_header       | <header> <pageTemplate> <frame id="first" x1="1.3cm" y1="2.5cm" height="23.0cm" width="19.0cm"/> <pageGraphics> <!-- You Logo - Change X,Y,Width and Height --> <image x="1.3cm" y="27.6cm" height="40.0" >[[ company.logo or removeParentNode('image') ]]</image> <setFont name="DejaVu Sans" size="8"/> <fill color="black"/> <stroke color="black"/> <lines>1.3cm 27.5cm 20cm 27.5cm</lines> <drawRightString x="20cm" y="27.8cm">[[ company.rml_header1 ]]</drawRightString> <drawString x="1.3cm" y="27.2cm">[[ company.partner_id.name ]]</drawString> <drawString x="1.3cm" y="26.8cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]]</drawString> <drawString x="1.3cm" y="26.4cm">[[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]] - [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString> <drawString x="1.3cm" y="26.0cm">Phone:</drawString> <drawRightString x="7cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].phone or '' ]]</drawRightString> <drawString x="1.3cm" y="25.6cm">Mail:</drawString> <drawRightString x="7cm" y="25.6cm">[[ company.partner_id.address and company.partner_id.address[0].email or '' ]]</drawRightString> <lines>1.3cm 25.5cm 7cm 25.5cm</lines> <!--page bottom--> <lines>1.2cm 2.15cm 19.9cm 2.15cm</lines> <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString> <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString> <drawCentredString x="10.5cm" y="0.8cm">Contact : [[ user.name ]] - Page: <pageNumber/></drawCentredString> </pageGraphics> </pageTemplate> </header>   |

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @qoqa_ch_logistics
  Scenario: configure logistics
    Given I find a "stock.location" with oid: stock.stock_location_company
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
    Given I find a "stock.location" with oid: stock.stock_location_output
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |
    Given I find a "stock.location" with oid: stock.stock_location_stock
    And having:
    | name       | value                    |
    | company_id | by oid: scenario.qoqa_ch |
    Given I need a "stock.location" with oid: scenario.location_ch_sav
    And having:
    | name        | value                                |
    | name        | SAV                                  |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.location" with oid: scenario.location_ch_non_reclame
    And having:
    | name        | value                                |
    | name        | Non réclamé                          |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.location" with oid: scenario.location_ch_defectueux
    And having:
    | name        | value                                |
    | name        | Défectueux                           |
    | location_id | by oid: stock.stock_location_company |
    | company_id  | by oid: scenario.qoqa_ch             |
    Given I need a "stock.warehouse" with oid: stock.warehouse0
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
    Given I need a "sale.shop" with oid: sale.sale_shop_ch
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_ch |
