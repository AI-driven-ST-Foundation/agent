*** Settings ***
Documentation  This will be the most high level acceptance test for the library 
...   the library will contains methods like do / check / analyse  ... 
...   each method will collect some mobile app evidence like XML hierarchy and screenshot
...   send them to the LLM to get a response
...   in a more low level of acceptance test we can test that request to the ai
...    and see how it works with different models and different requests 
...    


...  typical actions in the automation are ; click element , input text , 
...  page should contains text ,
Library    AppiumLibrary

*** Test Cases ***
Test Agent
    [Documentation]   this doesn't work of cours e bcause we didn't code the 
    ...   high level keywords yet , but just as an example 
    Open Application        remote_url=https://hub-cloud.browserstack.com/wd/hub
    AiHelper.