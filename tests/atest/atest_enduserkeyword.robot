# *** Settings ***
# Library    ${EXECDIR}/Libraries/AiHelper/__init__.py
# Resource    ${EXECDIR}/PageObjects/common.resource
# Library    Collections
# *** Variables ***
# ${screenshot_path}    ${EXECDIR}/Libraries/AiHelper/tests/screenshot_infotraffic.png
# *** Test Cases ***
# TC1- Current Screenshot Sent Only
#     __Launch IDFM App
#     Sleep    5
#     ASK AI For Verification    what does this screenshot contain ?

# TC2- Current Screenshot And UI XML Sent
#     __Launch IDFM App
#     Sleep    5
#     ASK AI For Verification    what does this screenshot contain ?    True

# TC3- Current Screenshot And Reference Screenshot
#     __Launch IDFM App
#     Sleep    5
#     ASK AI For Verification    what does this screenshot contain ?    False    ${screenshot_path}

# TC4- Current Screenshot And Reference Screenshot
#     __Launch IDFM App
#     Sleep    5
#     ASK AI For Verification    what does this screenshot contain ?    True    ${screenshot_path}

# TC5- Get Cumulated Cost
#     ${cumulated_cost} =    Get Cumulated Cost
#     Log To Console    ${cumulated_cost}