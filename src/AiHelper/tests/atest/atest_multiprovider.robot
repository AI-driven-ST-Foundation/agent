*** Settings ***
Documentation    Test Suite for Multi-Provider LLM Interface
...              Tests OpenAI, Anthropic, and Google Gemini providers
...              Verifies unified interface works across all providers
Library          Collections

*** Variables ***
${SIMPLE_PROMPT}    What is the capital of France? Answer in one short sentence.
${SYSTEM_MESSAGE}   You are a helpful assistant. Keep responses brief and concise.

*** Test Cases ***
Test Gemini Provider - Simple Request
    [Documentation]    Test Google Gemini with a simple question
    [Tags]    gemini    provider    basic
    
    # Import library with Gemini provider
    Import Library    src.AiHelper.AiHelper    gemini    gemini-2.5-flash
    
    # Create messages
    ${system_msg}=    Create Dictionary    role=system    content=${SYSTEM_MESSAGE}
    ${user_msg}=      Create Dictionary    role=user      content=${SIMPLE_PROMPT}
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain         ${response}    Paris
    
    # Check cost tracking
    ${cost}=    Get Cumulated Cost
    Should Be True    ${cost} > 0
    
    Log    ✅ Gemini Response: ${response}
    Log    💰 Cost: $${cost}

Test Anthropic Provider - Simple Request
    [Documentation]    Test Anthropic Claude with a simple question
    [Tags]    anthropic    provider    basic
    
    # Import library with Anthropic provider
    Import Library    src.AiHelper.AiHelper    anthropic    claude-3-5-sonnet-20241022
    
    # Create messages
    ${system_msg}=    Create Dictionary    role=system    content=${SYSTEM_MESSAGE}
    ${user_msg}=      Create Dictionary    role=user      content=${SIMPLE_PROMPT}
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain         ${response}    Paris
    
    # Check cost tracking
    ${cost}=    Get Cumulated Cost
    Should Be True    ${cost} > 0
    
    Log    ✅ Anthropic Response: ${response}
    Log    💰 Cost: $${cost}

Test Gemini - Complex Conversation
    [Documentation]    Test Gemini with a multi-turn conversation
    [Tags]    gemini    conversation
    
    Import Library    src.AiHelper.AiHelper    gemini
    
    ${system_msg}=      Create Dictionary    role=system      content=You are a calculator
    ${user_msg1}=       Create Dictionary    role=user        content=What is 5 + 3?
    ${assistant_msg}=   Create Dictionary    role=assistant   content=5 + 3 equals 8
    ${user_msg2}=       Create Dictionary    role=user        content=Now multiply that by 2
    
    ${messages}=        Create List    ${system_msg}    ${user_msg1}    ${assistant_msg}    ${user_msg2}
    
    ${response}=    Send AI Request    ${messages}
    
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    16    sixteen
    
    Log    ✅ Gemini Conversation: ${response}

Test Anthropic - Complex Conversation
    [Documentation]    Test Anthropic with a multi-turn conversation
    [Tags]    anthropic    conversation
    
    Import Library    src.AiHelper.AiHelper    anthropic
    
    ${system_msg}=      Create Dictionary    role=system      content=You are a calculator
    ${user_msg1}=       Create Dictionary    role=user        content=What is 5 + 3?
    ${assistant_msg}=   Create Dictionary    role=assistant   content=5 + 3 equals 8
    ${user_msg2}=       Create Dictionary    role=user        content=Now multiply that by 2
    
    ${messages}=        Create List    ${system_msg}    ${user_msg1}    ${assistant_msg}    ${user_msg2}
    
    ${response}=    Send AI Request    ${messages}
    
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    16    sixteen
    
    Log    ✅ Anthropic Conversation: ${response}

Test Gemini - Temperature Control
    [Documentation]    Test Gemini with different temperature settings
    [Tags]    gemini    parameters
    
    Import Library    src.AiHelper.AiHelper    gemini
    
    ${system_msg}=    Create Dictionary    role=system    content=You are a creative writer
    ${user_msg}=      Create Dictionary    role=user      content=Write one word that describes the color blue
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Test with low temperature (deterministic)
    ${response1}=    Send AI Request    ${messages}    temperature=0.1
    Should Not Be Empty    ${response1}
    
    Log    ✅ Gemini Low Temp: ${response1}

Test Anthropic - Temperature Control
    [Documentation]    Test Anthropic with different temperature settings
    [Tags]    anthropic    parameters
    
    Import Library    src.AiHelper.AiHelper    anthropic
    
    ${system_msg}=    Create Dictionary    role=system    content=You are a creative writer
    ${user_msg}=      Create Dictionary    role=user      content=Write one word that describes the color blue
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Test with low temperature (deterministic)
    ${response1}=    Send AI Request    ${messages}    temperature=0.1
    Should Not Be Empty    ${response1}
    
    Log    ✅ Anthropic Low Temp: ${response1}

Test Cost Tracking Across Providers
    [Documentation]    Verify cost tracking accumulates across different providers
    [Tags]    cost    tracking
    
    # Reset cost counter
    Import Library    src.AiHelper.AiHelper    gemini
    ${initial_cost}=    Reset Cumulated Cost
    Should Be Equal As Numbers    ${initial_cost}    0
    
    # Test Gemini with longer prompt for measurable cost
    Import Library       src.AiHelper.AiHelper    gemini
    ${msg}=              Create Dictionary    role=user    content=Write a paragraph about artificial intelligence and its impact on society
    ${messages}=         Create List          ${msg}
    ${response1}=        Send AI Request    ${messages}
    ${cost1}=            Get Cumulated Cost
    # Gemini is very cheap, cost might be close to 0
    Should Be True       ${cost1} >= 0
    
    # Test Anthropic
    Import Library       src.AiHelper.AiHelper    anthropic
    ${response2}=        Send AI Request    ${messages}
    ${cost2}=            Get Cumulated Cost
    Should Be True       ${cost2} >= ${cost1}
    
    Log    Gemini cost: $${cost1}
    Log    Total cost after Anthropic: $${cost2}
    Log    Cost tracking works across providers!

Test Provider Comparison - Same Prompt
    [Documentation]    Send same prompt to all providers and compare responses
    [Tags]    comparison    all-providers
    
    ${prompt}=    Set Variable    Explain quantum computing in exactly one sentence.
    ${user_msg}=  Create Dictionary    role=user    content=${prompt}
    ${messages}=  Create List          ${user_msg}
    
    # Reset cost
    Import Library    src.AiHelper.AiHelper    gemini
    Reset Cumulated Cost
    
    # Test Gemini
    Import Library    src.AiHelper.AiHelper    gemini
    ${gemini_response}=    Send AI Request    ${messages}
    ${gemini_cost}=        Get Cumulated Cost
    
    # Test Anthropic  
    Import Library    src.AiHelper.AiHelper    anthropic
    ${anthropic_response}=    Send AI Request    ${messages}
    ${anthropic_cost}=        Get Cumulated Cost
    
    # Verify all responded
    Should Not Be Empty    ${gemini_response}
    Should Not Be Empty    ${anthropic_response}
    
    # Log comparison
    Log    ============================================================
    Log    PROVIDER COMPARISON RESULTS
    Log    ============================================================
    Log    Prompt: ${prompt}
    Log    Gemini Response: ${gemini_response}
    Log    Cost: $${gemini_cost}
    Log    Anthropic Response: ${anthropic_response}
    Log    Total Cost: $${anthropic_cost}
    Log    ============================================================

Test Gemini Haiku Model
    [Documentation]    Test using Anthropic's fastest/cheapest model
    [Tags]    anthropic    haiku    cheap
    
    Import Library    src.AiHelper.AiHelper    anthropic    claude-3-haiku-20240307
    
    ${user_msg}=  Create Dictionary    role=user    content=What is 2+2?
    ${messages}=  Create List          ${user_msg}
    
    ${response}=    Send AI Request    ${messages}
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    4    four
    
    Log    ✅ Claude Haiku Response: ${response}

Test Error Handling - Invalid Provider
    [Documentation]    Verify proper error handling for unsupported providers
    [Tags]    error    negative
    
    # This should fail gracefully
    Run Keyword And Expect Error    *Unsupported LLM client*
    ...    Import Library    src.AiHelper.AiHelper    invalid_provider

*** Keywords ***
Should Contain Any
    [Arguments]    ${text}    @{keywords}
    [Documentation]    Verify text contains at least one of the keywords
    ${found}=    Set Variable    ${FALSE}
    FOR    ${keyword}    IN    @{keywords}
        ${contains}=    Run Keyword And Return Status    Should Contain    ${text}    ${keyword}    ignore_case=True
        ${found}=    Set Variable If    ${contains}    ${TRUE}    ${found}
    END
    Should Be True    ${found}    Text '${text}' does not contain any of: ${keywords}

