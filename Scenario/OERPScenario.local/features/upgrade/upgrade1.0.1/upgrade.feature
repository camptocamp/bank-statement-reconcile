@upgrade_from_1.0.0 @qoqa

Feature: upgrade to 1.0.1

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                       |
      | connector_qoqa             |
      | account_compute_tax_amount |
    Then my modules should have been installed and models reloaded

  @qoqa_backend
  Scenario: Configure the QoQa backend
    Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I set global property named "property_voucher_journal_id_ch" for model "qoqa.backend" and field "property_voucher_journal_id" for company with ref "scenario.qoqa_ch"
    And the property is related to model "account.journal" using column "name" and value "Règlement par Bon Cadeau"
    Given I am configuring the company with ref "scenario.qoqa_fr"
    And I set global property named "property_voucher_journal_id_fr" for model "qoqa.backend" and field "property_voucher_journal_id" for company with ref "scenario.qoqa_fr"
    And the property is related to model "account.journal" using column "name" and value "Règlement par Bon Cadeau"

  Scenario: update application version
    Given I set the version of the instance to "1.0.1"
