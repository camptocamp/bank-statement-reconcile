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
@accounting_ch @core_setup

Feature: Configure the CH's accounting

  # TODO: do we need to create accounts for the payment modes?

  # @accounts
  # Scenario Outline: Create the bank account for ...
  #   Given I need a "account.account" with oid: <oid>
  #   And having:
  #     | key        | value                                         |
  #     | name       | <name>                                        |
  #     | code       | <code>                                        |
  #     | parent_id  | by code: 102.02                               |
  #     | type       | liquidity                                     |
  #     | user_type  | by oid: account.data_account_type_receivable  |
  #     | reconcile  | True                                          |
  #     | company_id | by oid: scenario.qoqa_ch                      |
  #     | active     | True                                          |
  #   Then I save it

  #   Examples: Bank Accounts
  #     | oid                          | name        | code      |
  #     | scenario.account_postfinance | Postfinance | 102.02.01 |
  #     | scenario.account_visa        | Visa        | 102.02.02 |
  #     | scenario.account_mastercard  | Mastercard  | 102.02.03 |

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
    Then I save it

    Examples: Bank Journals
      | oid                           | name         | code  |
      | scenario.journal_postfinance  | Postfinance  | POSTF |
      | scenario.journal_visa         | Visa         | VISA  |
      | scenario.journal_mastercard   | Mastercard   | MASTR |
      | scenario.journal_paypal       | Paypal       | PAYPA |
      | scenario.journal_swissbilling | Swissbilling | SWISS |

    Examples: Bank Journals (unused - for historic)
      | oid                              | name                      | code  |
      | scenario.journal_swikey_old      | Swikey - plus utilisé      | OLDSW |
      | scenario.journal_postfinance_old | Postfinance - plus utilisé | OLDPF |
      | scenario.journal_mastercard_old  | Mastercard - plus utilisé  | OLDMS |
      | scenario.journal_visa_old        | Visa - plus utilisé        | OLDVI |
