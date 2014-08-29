# -*- coding: utf-8 -*-
@upgrade_from_1.0.24 @qoqa

Feature: upgrade to 1.0.25

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | qoqa_offer                                             |
    Then my modules should have been installed and models reloaded

  Scenario: update application version
    Given I set the version of the instance to "1.0.25"