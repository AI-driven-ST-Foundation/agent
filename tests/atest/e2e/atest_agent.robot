*** Settings ***
Documentation   To run the test on browserstack, need to have browserstack.yml file 
...    and browserstack-sdk installed 
...    then run the test with the command :
...    browserstack-sdk robot tests/atest/e2e/atest_agent.robot
...    
...    this test run on the sample app at tests/atest/sample_app.apk
Library    AppiumLibrary
Library    src.AiHelper.AgentKeywords
*** Test Cases ***
Test Agent
    Open Application        remote_url=https://hub-cloud.browserstack.com/wd/hub
    ${prompt}=    Set Variable    click on the button enter some value
    ${prompt2}=    Set Variable    input this text in the texte field: hello
    ${prompt3}=    Set Variable    click on the submit button 
    ${prompt4}=    Set Variable    check that the text hello is displayed under the button of submit 
    src.AiHelper.AgentKeywords.Agent Do    instruction=${prompt} 
    src.AiHelper.AgentKeywords.Agent Do    instruction=${prompt2} 
    src.AiHelper.AgentKeywords.Agent Do    instruction=${prompt3}
    src.AiHelper.AgentKeywords.Agent check    instruction=${prompt4}