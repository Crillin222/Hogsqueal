@PBC14TEST
Feature: Dummy sanity test
  As a maintainer
  I want to run a quick dummy creation
  So that I can validate the Xray/Jira integration

  Scenario: Create a dummy test
    Given the application is running
    When I click on "Create dummy"
    Then a new Test should be created in Jira
