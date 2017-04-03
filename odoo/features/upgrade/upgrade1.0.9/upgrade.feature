# -*- coding: utf-8 -*-
@upgrade_from_1.0.8 @qoqa

Feature: upgrade to 1.0.9

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | picking_dispatch                                       |
      | picking_dispatch_group                                 |
      | web_ckeditor4                                          |
      | qoqa_offer                                             |
      | account_statement_ext                                  |
      | account_payment_transaction_id                         |
      | account_statement_one_move                             |
      | account_easy_reconcile                                 |
      | account_statement_transactionid_completion             |
    Then my modules should have been installed and models reloaded

  Scenario: update application version
    Given I set the version of the instance to "1.0.9"