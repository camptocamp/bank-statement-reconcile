# -*- coding: utf-8 -*-
@upgrade_from_1.0.31 @qoqa

Feature: upgrade to 1.0.32

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Then I set the version of the instance to "1.0.32"
