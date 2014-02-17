# -*- coding: utf-8 -*-
@upgrade_from_1.0.6 @qoqa

Feature: upgrade to 1.0.7

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
    Then my modules should have been installed and models reloaded

  Scenario: update application version
    Given I set the version of the instance to "1.0.7"
