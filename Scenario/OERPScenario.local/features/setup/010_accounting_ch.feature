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
@accounting_ch @setup

Feature: Configure the CH's accounting

  @banks
  Scenario Outline: Create the bank account for QoQa CH
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.journal" with oid: <journal_oid>
    And having:
      | key                       | value                       |
      | name                      | <journal_name>              |
      | code                      | <journal_code>              |
      | type                      | bank                        |
      | company_id                | by oid: scenario.qoqa_ch    |
      | currency                  | <currency>                  |
      | default_debit_account_id  | by code: <acc_code>         |
      | default_credit_account_id | by code: <acc_code>         |
      | allow_date                | false                       |
    Given I need a "res.partner.bank" with oid: <bank_oid>
    And having:
      | key        | value                     |
      | journal_id | by oid: <journal_oid>     |
      | partner_id | by name: QoQa Services SA |
      | bank_name  | <bank_name>               |
      | company_id | by oid: scenario.qoqa_ch  |
      | street     | <street>                  |
      | zip        | <zip>                     |
      | city       | <city>                    |
      | country_id | by code: CH               |
      | state      | bank                      |
      | acc_number | <iban>                    |
      | bank_bic   | <bic>                     |
      | active     | True                      |

    Examples: Bank Accounts
      | journal_oid                              | journal_code | journal_name                       | currency                           | acc_code | bank_oid                               | bank_name              | street               | zip  | city  | iban                       | bic         |
      | scenario.journal_ch_service_client       | BNK11        | Compte Service-client Qgroup       | false                              | 1011     | scenario.bank_ch_service_client        | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH68 0900 0000 1078 0685 6 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_chf      | BNK16        | Compte Fournisseurs Qgroup         | false                              | 1016     | scenario.bank_ch_fournisseur_chf       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH55 0900 0000 1225 8688 3 | POFICHBEXXX |
      | scenario.journal_ch_client_manuel        | BNK15        | Compte Client manuel Qgroup        | false                              | 1015     | scenario.bank_ch_client_manuel         | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH83 0900 0000 1283 1083 4 | POFICHBEXXX |
      | scenario.journal_ch_enc_debiteur         | BNK10        | Compte Encaissement débiteur Qgroup| false                              | 1010     | scenario.bank_ch_enc_debiteur          | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH71 0900 0000 1771 3231 4 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_eur      | BNK12        | Compte Fournisseur Qgroup en EUR   | by name: EUR and company_id: False | 1012     | scenario.bank_ch_fournisseur_eur       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH19 0900 0000 9115 5371 5 | POFICHBEXXX |
      | scenario.journal_ch_fournisseur_usd      | BNK14        | Compte Fournisseur Qgroup en USD   | by name: USD and company_id: False | 1014     | scenario.bank_ch_fournisseur_usd       | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH56 0900 0000 9114 7215 1 | POFICHBEXXX |
      #| scenario.journal_ch_projet_geelee_ch     | BNK          | Compte Projet Geelee.ch            | false                              |          | scenario.bank_ch_projet_geelee_ch      | Swiss Post-Postfinance | Nordring 8, Postfach | 3030 | Berne | CH29 0900 0000 1223 3631 5 | POFICHBEXXX |
      | scenario.journal_ch_salaires             | BNK20        | Compte Paiement Salaires           | false                              | 1020     | scenario.bank_ch_salaires              | UBS SA                 |                      | 1800 | Vevey | CH51 0025 5255 7757 4801 V | UBSWCHZH80A |
      | scenario.journal_ch_epargne              | BNK21        | Compte épargne                     | false                              | 1021     | scenario.bank_ch_epargne               | UBS SA                 |                      | 1800 | Vevey | CH10 0025 5255 7757 48C3 Z | UBSWCHZH80A |
      | scenario.journal_ch_garantie_loyer       | GAR11        | Compte garantie loyer              | false                              | 1411     | scenario.bank_ch_garantie_loyer        | UBS SA                 |                      | 1800 | Vevey | CH06 0025 5255 7757 48MK U | UBSWCHZH80A |


  @journals
  Scenario Outline: Create an accounting journal for a Bank Journal
    Given I need a "account.journal" with oid: <oid>
    And having:
      | key                       | value                    |
      | name                      | <name>                   |
      | code                      | <code>                   |
      | type                      | bank                     |
      | company_id                | by oid: scenario.qoqa_ch |
      | default_debit_account_id  | by code: 102.02          |
      | default_credit_account_id | by code: 102.02          |
      | allow_date                | false                    |

    Examples: Bank Journals
      | oid                            | name         | code  |
      | scenario.journal_postfinance   | Postfinance  | POSTF |
      | scenario.journal_visa_ch       | Visa         | VISA  |
      | scenario.journal_mastercard_ch | Mastercard   | MASTR |
      | scenario.journal_paypal_ch     | Paypal       | PAYPA |
      | scenario.journal_swissbilling  | Swissbilling | SWISS |

    Examples: Bank Journals (unused - for historic)
      | oid                                | name                       | code  |
      | scenario.journal_swikey_old        | Swikey - plus utilisé      | OLDSW |
      | scenario.journal_postfinance_old   | Postfinance - plus utilisé | OLDPF |
      | scenario.journal_mastercard_ch_old | Mastercard - plus utilisé  | OLDMS |
      | scenario.journal_visa_ch_old       | Visa - plus utilisé        | OLDVI |

