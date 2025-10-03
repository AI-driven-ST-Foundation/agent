*** Settings ***
Library    AppiumLibrary
Library    src.AiHelper.AgentKeywords

Suite Setup    Open Application    remote_url=https://hub-cloud.browserstack.com/wd/hub
Suite Teardown    Close Application

*** Test Cases ***
Premier Flux Minimal
    Agent.Do    accepte les cookies
    Agent.Do    ignore l'écran
    Agent.Check    l'écran affiche bien le map avec les icones des bus



