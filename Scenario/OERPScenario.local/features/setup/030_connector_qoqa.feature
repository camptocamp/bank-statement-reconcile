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
@connector_qoqa @setup


Feature: Configure the connector's backend

  @qoqa_backend
  Scenario: Configure the QoQa backend
  Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
         | key                 | value                                                                            |
         | url                 | http://admin.test02.qoqa.com                                                     |
         | default_lang_id     | by code: fr_FR                                                                   |
         | access_token_secret | 2N2RLFT5HtRmyxY70Ydzsj1PJmqTzJc4t2lwBJyfmlJlkiLicW3pWQO6                         |
         | client_key          | obfRm2CNDY40DBbcvqZLmF2rUFRyjBxM                                                 |
         | client_secret       | IoDEPZcUlYH1P5DNkkrtsD4ok227yQaTlFFnMeJ3bcUYkfWDVmFwI2VTnRjcht9hjC7qX52KIPaX4G4T |
         | access_token        | 6yuI7ELBNEZo92ZiyAgRJwrzWLVIcYgA                                                 |


  @automatic_workflows
  Scenario: Configure Sales Automatic Workflows
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.automatic_validation
    And having:
      | key                        | value           |
      | picking_policy             | one             |
      | invoice_quantity           | procurement     |
      | order_policy               | manual          |
      | validate_order             | True            |
      | validate_invoice           | True            |
      | create_invoice_on          | on_picking_done |
      | invoice_date_is_order_date | True            |
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.manual_validation
    And having:
      | key              | value       |
      | picking_policy   | one         |
      | invoice_quantity | procurement |
      | order_policy     | picking     |
      | validate_order   | False       |
      | validate_invoice | True        |

  @sale_payment_methods @gift
  Scenario: Create the automatic payment methods for gift cards
  Given I need a "payment.method" with oid: scenario.payment_method_gift_card_ch
    And having:
      | key                 | value                                                |
      | name                | Bon d'achat CH                                       |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | qoqa_id             | 9                                                    |
      | sequence            | 99                                                   |
      | journal_id          | scenario.journal_bon_achat_ch                        |
      | company_id          | by oid:  scenario.qoqa_ch                            |
  Given I need a "payment.method" with oid: scenario.payment_method_gift_card_fr
    And having:
      | key                 | value                                                |
      | name                | Bon d'achat FR                                       |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | qoqa_id             | 9                                                    |
      | sequence            | 99                                                   |
      | company_id          | by oid:  scenario.qoqa_fr                            |

  @sale_payment_methods @old
  Scenario Outline: Create the automatic payment methods not assigned to a company
  Given I need a "payment.method" with oid: <oid>
    And having:
      | key                 | value                                                |
      | name                | <name>                                               |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | qoqa_id             | <qoqa_id>                                            |
      | active              | 0                                                    |
      | company_id          | False                                                |

    Examples: Payment Methods
      | oid                                   | name                                | qoqa_id |
      | scenario.payment_method_manual        | Traitement manuel                   | 8       |
      | scenario.payment_method_cash          | Paiement en espèce                  | 7       |
      | scenario.payment_method_virement      | Virement                            | 6       |
      | scenario.payment_method_bvr           | BVR                                 | 5       |

  @sale_payment_methods @ch
  Scenario Outline: Create the automatic payment methods for CH
  Given I need a "payment.method" with oid: <oid>
    And having:
      | key                 | value                                                |
      | name                | <name> (CH)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | <journal_id>                                         |
      | qoqa_id             | <qoqa_id>                                            |
      | company_id          | by oid: scenario.qoqa_ch                             |
      | active              | <active> |

    Examples: Payment Methods
      | oid                                   | name                                | journal_id                                             | qoqa_id | active |
      | scenario.payment_method_postfinance   | Postfinance                         | by oid: scenario.journal_reglement_postfinance         | 3       | 1      |
      | scenario.payment_method_visa_ch       | Visa                                | by oid: scenario.journal_reglement_visa_mastercard_ch  | 1       | 1      |
      | scenario.payment_method_mastercard_ch | Mastercard                          | by oid: scenario.journal_reglement_visa_mastercard_ch  | 2       | 1      |
      | scenario.payment_method_paypal_ch     | Paypal                              | by oid: scenario.journal_paypal_ch                     | 12      | 1      |
      | scenario.payment_method_swissbilling  | Swissbilling (paiement par facture) | by oid: scenario.journal_swissbilling                  |         | 1      |

    Examples: Payment Methods (unused now but kept for the history)
      | oid                                   | name                  | journal_id                          | qoqa_id | active |
      | scenario.payment_method_swikey_ch_old | Swikey - plus utilisé | by oid: scenario.journal_swikey_old | 10      | 0      |

  @sale_payment_methods @fr
  Scenario Outline: Create the automatic payment methods for FR
  Given I need a "payment.method" with oid: <oid>
    And having:
      | key                 | value                                                |
      | name                | <name> (FR)                                          |
      | workflow_process_id | by oid: sale_automatic_workflow.automatic_validation |
      | import_rule         | paid                                                 |
      | journal_id          | <journal_id>                                         |
      | qoqa_id             | <qoqa_id>                                            |
      | company_id          | by oid: scenario.qoqa_fr                             |
      | active              | <active> |

    Examples: Payment Methods
      | oid                                    | name             | journal_id                             | qoqa_id | active |
      | scenario.payment_method_carte_bleue    | Carte Bleue Visa | by oid: scenario.journal_carte_bleue   | 4       | 1      |
      | scenario.payment_method_visa_fr        | Visa             | by oid: scenario.journal_visa_fr       | 1       | 1      |
      | scenario.payment_method_mastercard_fr  | Mastercard       | by oid: scenario.journal_mastercard_fr | 2       | 1      |
      | scenario.payment_method_paiement_3x_fr | Paiement 3x      | by oid: scenario.journal_paiement_3x   | 11      | 1      |
      | scenario.payment_method_paypal_fr      | Paypal           | by oid: scenario.journal_paypal_fr     | 12      | 1      |

    Examples: Payment Methods (unused now but kept for the history)
      | oid                                       | name                         | journal_id                              | qoqa_id | active |
      | scenario.payment_method_sogenactif_fr_old | ? Sogenactif  - plus utilisé | by oid: scenario.journal_sogenactif_old |         | 0      |

  @qoqa_id @lang
  Scenario: Set the qoqa_ids on the languages
    Given I find a "res.lang" with code: fr_FR
    And having:
         | key     | value |
         | qoqa_id | 1     |
    Given I find a "res.lang" with code: de_DE
    And having:
         | key     | value |
         | qoqa_id | 2     |

  @qoqa_id @currency
  Scenario Outline: Set the qoqa_ids on the currencies
    Given I find a "res.currency" with oid: <oid>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | oid      | qoqa_id |
         | base.CHF | 1       |
         | base.EUR | 2       |
         | base.USD | 3       |
         | base.GBP | 4       |
         | base.CNY | 5       |
         | base.JPY | 6       |

  @qoqa_id @country
  Scenario Outline: Set the qoqa_ids on the Countries
    Given I find a "res.country" with oid: <oid>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | oid     | qoqa_id |
         | base.ch | 1       |
         | base.fr | 2       |
         | base.de | 3       |
         | base.it | 4       |
         | base.us | 5       |
         | base.uk | 6       |
         | base.dk | 7       |
         | base.nl | 8       |
         | base.be | 9       |
         | base.es | 10      |
         | base.pt | 11      |
         | base.cn | 12      |
         | base.jp | 14      |
         | base.li | 15      |
         | base.lu | 16      |
         | base.cy | 17      |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with description: <tax_code>
    And having:
         | key           | value     |
         | qoqa_id       | <qoqa_id> |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.5%     | 4       |
         | 3.8%     | 5       |
         | 8.0%     | 6       |
         | 0% excl. | 10      |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find an inactive "account.tax" with description: <tax_code>
    And having:
         | key           | value     |
         | qoqa_id       | <qoqa_id> |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.4%     | 1       |
         | 3.6%     | 2       |
         | 7.6%     | 3       |

  @qoqa_id @tax
  Scenario Outline: Set the qoqa_ids on the taxes
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I find a "account.tax" with description: <tax_code>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: currencies
         | tax_code | qoqa_id |
         | 2.1      | 7       |
         | 5.5      | 8       |
         | 19.6     | 9       |

  @qoqa_id @delivery_service
  Scenario Outline: Set the qoqa_ids on the Delivery Services
    Given I find a "delivery.service" with oid: <oid>
    And having:
         | key     | value         |
         | qoqa_id | <qoqa_id>     |

    Examples: delivery services
         | oid                                               | qoqa_id |
         | qoqa_offer.delivery_service_manualundefined       | 1       |
         | qoqa_offer.delivery_service_postpac_prisi_std     | 2       |
         | qoqa_offer.delivery_service_postpac_prisi_man     | 3       |
         | qoqa_offer.delivery_service_postpac_prisi_sp      | 4       |
         | qoqa_offer.delivery_service_amail_b5_0100g_02cm   | 5       |
         | qoqa_offer.delivery_service_amail_b5_0100g_25cm   | 6       |
         | qoqa_offer.delivery_service_amail_b5_100250g_02cm | 7       |
         | qoqa_offer.delivery_service_amail_b5_100250g_25cm | 8       |
         | qoqa_offer.delivery_service_legacy_fr             | 9       |
         | qoqa_offer.delivery_service_wine_transport        | 10      |
         | qoqa_offer.delivery_service_vinolog               | 11      |
         | qoqa_offer.delivery_service_manual_wphone         | 12      |
         | qoqa_offer.delivery_service_standard              | 13      |
         | qoqa_offer.delivery_service_standard_wphone       | 14      |
         | qoqa_offer.delivery_service_legacy_qwfr           | 15      |
         | qoqa_offer.delivery_service_postpac_pri           | 16      |
         | qoqa_offer.delivery_service_so_colissimo          | 17      |
         | qoqa_offer.delivery_service_client_appointments   | 18      |
