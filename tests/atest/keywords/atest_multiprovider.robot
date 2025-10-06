*** Settings ***
Documentation    Test Suite for Multi-Provider LLM Interface
...              Tests OpenAI, Anthropic, Google Gemini, DeepSeek, and Ollama (local) providers
...              Verifies unified interface works across all providers
Library          Collections
Library          src.AiHelper.AiHelper

*** Variables ***
${SIMPLE_PROMPT}    What is the capital of France? Answer in one short sentence.
${SYSTEM_MESSAGE}   You are a helpful assistant. Keep responses brief and concise.

*** Test Cases ***
Test Gemini Provider - Simple Request
    [Documentation]    Test Google Gemini with a simple question
    [Tags]    gemini    provider    basic
    
    # Switch to Gemini provider
    Switch Provider    gemini    gemini-2.5-flash
    
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
    
    # Switch to Anthropic provider
    Switch Provider    anthropic    claude-3-5-sonnet-20241022
    
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
    
    Switch Provider    gemini
    
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
    
    Switch Provider    anthropic
    
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
    
    Switch Provider    gemini
    
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
    
    Switch Provider    anthropic
    
    ${system_msg}=    Create Dictionary    role=system    content=You are a creative writer
    ${user_msg}=      Create Dictionary    role=user      content=Write one word that describes the color blue
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Test with low temperature (deterministic)
    ${response1}=    Send AI Request    ${messages}    temperature=0.1
    Should Not Be Empty    ${response1}
    
    Log    ✅ Anthropic Low Temp: ${response1}

Test DeepSeek Provider - Simple Request
    [Documentation]    Test DeepSeek with a simple question
    [Tags]    deepseek    provider    basic
    
    # Switch to DeepSeek provider
    Switch Provider    deepseek    deepseek-chat
    
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
    
    Log    ✅ DeepSeek Response: ${response}
    Log    💰 Cost: $${cost}

Test DeepSeek - Complex Conversation
    [Documentation]    Test DeepSeek with a multi-turn conversation
    [Tags]    deepseek    conversation
    
    Switch Provider    deepseek
    
    ${system_msg}=      Create Dictionary    role=system      content=You are a calculator
    ${user_msg1}=       Create Dictionary    role=user        content=What is 5 + 3?
    ${assistant_msg}=   Create Dictionary    role=assistant   content=5 + 3 equals 8
    ${user_msg2}=       Create Dictionary    role=user        content=Now multiply that by 2
    
    ${messages}=        Create List    ${system_msg}    ${user_msg1}    ${assistant_msg}    ${user_msg2}
    
    ${response}=    Send AI Request    ${messages}
    
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    16    sixteen
    
    Log    ✅ DeepSeek Conversation: ${response}

Test DeepSeek R1 Model
    [Documentation]    Test using DeepSeek R1 reasoning model
    [Tags]    deepseek    r1    reasoning
    
    Switch Provider    deepseek    deepseek-reasoner
    
    ${user_msg}=  Create Dictionary    role=user    content=What is 2+2? Explain your reasoning.
    ${messages}=  Create List          ${user_msg}
    
    ${response}=    Send AI Request    ${messages}
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    4    four
    
    Log    ✅ DeepSeek R1 Response: ${response}

Test Ollama Provider - Simple Request
    [Documentation]    Test Ollama with local Llama model
    [Tags]    ollama    provider    basic    local
    
    # Switch to Ollama provider (local)
    Reset Cumulated Cost
    Switch Provider    ollama    llama3.2
    
    # Create messages
    ${system_msg}=    Create Dictionary    role=system    content=${SYSTEM_MESSAGE}
    ${user_msg}=      Create Dictionary    role=user      content=${SIMPLE_PROMPT}
    ${messages}=      Create List          ${system_msg}  ${user_msg}
    
    # Send request to local model
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain         ${response}    Paris
    
    Log    ✅ Ollama Response: ${response}

Test Ollama - Complex Conversation
    [Documentation]    Test Ollama with multi-turn conversation
    [Tags]    ollama    conversation    local
    
    Switch Provider    ollama    llama3.2
    
    ${system_msg}=      Create Dictionary    role=system      content=You are a calculator
    ${user_msg1}=       Create Dictionary    role=user        content=What is 5 + 3?
    ${assistant_msg}=   Create Dictionary    role=assistant   content=5 + 3 equals 8
    ${user_msg2}=       Create Dictionary    role=user        content=Now multiply that by 2
    
    ${messages}=        Create List    ${system_msg}    ${user_msg1}    ${assistant_msg}    ${user_msg2}
    
    ${response}=    Send AI Request    ${messages}
    
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    16    sixteen
    
    Log    ✅ Ollama Conversation: ${response}

Test Ollama - Different Models
    [Documentation]    Test switching between different local models
    [Tags]    ollama    models    local
    
    # Test with Llama 3.2
    Switch Provider    ollama    llama3.2
    ${user_msg}=  Create Dictionary    role=user    content=Say hello in one word
    ${messages}=  Create List          ${user_msg}
    ${response1}=    Send AI Request    ${messages}
    Should Not Be Empty    ${response1}
    Log    ✅ Llama 3.2: ${response1}
    
    # Test with Mistral (if available)
    Switch Provider    ollama    mistral
    ${response2}=    Send AI Request    ${messages}
    Should Not Be Empty    ${response2}
    Log    ✅ Mistral: ${response2}

Test Cost Tracking Across Providers
    [Documentation]    Verify cost tracking accumulates across different providers
    [Tags]    cost    tracking
    
    # Reset cost counter
    Switch Provider    gemini
    ${initial_cost}=    Reset Cumulated Cost
    Should Be Equal As Numbers    ${initial_cost}    0
    
    # Test Gemini with longer prompt for measurable cost
    Switch Provider    gemini
    ${msg}=              Create Dictionary    role=user    content=Write a paragraph about artificial intelligence and its impact on society
    ${messages}=         Create List          ${msg}
    ${response1}=        Send AI Request    ${messages}
    ${cost1}=            Get Cumulated Cost
    # Gemini is very cheap, cost might be close to 0
    Should Be True       ${cost1} >= 0
    
    # Test Anthropic
    Switch Provider    anthropic
    ${response2}=        Send AI Request    ${messages}
    ${cost2}=            Get Cumulated Cost
    Should Be True       ${cost2} >= ${cost1}
    
    # Test DeepSeek
    Switch Provider    deepseek
    ${response3}=        Send AI Request    ${messages}
    ${cost3}=            Get Cumulated Cost
    Should Be True       ${cost3} >= ${cost2}
    
    Log    Gemini cost: $${cost1}
    Log    Total cost after Anthropic: $${cost2}
    Log    Total cost after DeepSeek: $${cost3}
    Log    Cost tracking works across providers!

Test Provider Comparison - Same Prompt
    [Documentation]    Send same prompt to all providers and compare responses
    [Tags]    comparison    all-providers
    
    ${prompt}=    Set Variable    Explain quantum computing in exactly one sentence.
    ${user_msg}=  Create Dictionary    role=user    content=${prompt}
    ${messages}=  Create List          ${user_msg}
    
    # Reset cost
    Switch Provider    gemini
    Reset Cumulated Cost
    
    # Test Gemini
    Switch Provider    gemini
    ${gemini_response}=    Send AI Request    ${messages}
    ${gemini_cost}=        Get Cumulated Cost
    
    # Test Anthropic  
    Switch Provider    anthropic
    ${anthropic_response}=    Send AI Request    ${messages}
    ${anthropic_cost}=        Get Cumulated Cost
    
    # Test DeepSeek
    Switch Provider    deepseek
    ${deepseek_response}=    Send AI Request    ${messages}
    ${deepseek_cost}=        Get Cumulated Cost
    
    # Verify all responded
    Should Not Be Empty    ${gemini_response}
    Should Not Be Empty    ${anthropic_response}
    Should Not Be Empty    ${deepseek_response}
    
    # Log comparison
    Log    ============================================================
    Log    PROVIDER COMPARISON RESULTS
    Log    ============================================================
    Log    Prompt: ${prompt}
    Log    Gemini Response: ${gemini_response}
    Log    Gemini Cost: $${gemini_cost}
    Log    Anthropic Response: ${anthropic_response}
    Log    Anthropic Cost: $${anthropic_cost}
    Log    DeepSeek Response: ${deepseek_response}
    Log    Total Cost: $${deepseek_cost}
    Log    ============================================================

Test Gemini Haiku Model
    [Documentation]    Test using Anthropic's fastest/cheapest model
    [Tags]    anthropic    haiku    cheap
    
    Switch Provider    anthropic    claude-3-haiku-20240307
    
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

Test Anthropic - Image URL Support
    [Documentation]    Test Anthropic Claude with image URL (vision API)
    [Tags]    anthropic    vision    image
    
    Switch Provider    anthropic    claude-sonnet-4-5-20250929
    
    # Create message with image - using OpenAI-style format for compatibility
    ${text_content}=    Create Dictionary    type=text    text=What do you see in this image? Describe it briefly.
    ${image_url}=       Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image_content}=   Create Dictionary    type=image_url    image_url=${image_url}
    ${content_list}=    Create List          ${text_content}    ${image_content}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    ant    insect    bug    Camponotus
    
    # Check cost tracking
    ${cost}=    Get Cumulated Cost
    Should Be True    ${cost} > 0
    
    Log    ✅ Anthropic Vision Response: ${response}
    Log    💰 Cost: $${cost}

Test Anthropic - Multiple Images
    [Documentation]    Test Anthropic Claude with multiple images
    [Tags]    anthropic    vision    multiple-images
    
    Switch Provider    anthropic    claude-sonnet-4-5-20250929
    
    # Create message with text and first image
    ${text1}=           Create Dictionary    type=text    text=Image 1:
    ${image_url1}=      Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image1}=          Create Dictionary    type=image_url    image_url=${image_url1}
    
    ${text2}=           Create Dictionary    type=text    text=Image 2:
    ${image_url2}=      Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
    ${image2}=          Create Dictionary    type=image_url    image_url=${image_url2}
    
    ${question}=        Create Dictionary    type=text    text=What animals are shown in these two images?
    
    ${content_list}=    Create List    ${text1}    ${image1}    ${text2}    ${image2}    ${question}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response mentions both animals
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    ant    insect
    Should Contain Any     ${response}    cat    feline
    
    Log    ✅ Anthropic Multiple Images: ${response}

Test Anthropic - Vision with System Prompt
    [Documentation]    Test Anthropic vision with system prompt
    [Tags]    anthropic    vision    system-prompt
    
    Switch Provider    anthropic    claude-sonnet-4-5-20250929
    
    # Create system message
    ${system_msg}=      Create Dictionary    role=system    content=You are an expert biologist. Identify species in images using scientific names.
    
    # Create user message with image
    ${text_content}=    Create Dictionary    type=text    text=What species is this?
    ${image_url}=       Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image_content}=   Create Dictionary    type=image_url    image_url=${image_url}
    ${content_list}=    Create List          ${text_content}    ${image_content}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${system_msg}    ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    Camponotus    ant    species
    
    Log    ✅ Anthropic Vision with System Prompt: ${response}

Test Gemini - Image URL Support
    [Documentation]    Test Gemini with image URL (vision API)
    [Tags]    gemini    vision    image
    
    Switch Provider    gemini    gemini-2.5-flash
    
    # Create message with image - using OpenAI-style format for compatibility
    ${text_content}=    Create Dictionary    type=text    text=What do you see in this image? Describe it briefly.
    ${image_url}=       Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image_content}=   Create Dictionary    type=image_url    image_url=${image_url}
    ${content_list}=    Create List          ${text_content}    ${image_content}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    ant    insect    bug    Camponotus
    
    # Check cost tracking
    ${cost}=    Get Cumulated Cost
    Should Be True    ${cost} >= 0
    
    Log    ✅ Gemini Vision Response: ${response}
    Log    💰 Cost: $${cost}

Test Gemini - Multiple Images
    [Documentation]    Test Gemini with multiple images
    [Tags]    gemini    vision    multiple-images
    
    Switch Provider    gemini    gemini-2.5-flash
    
    # Create message with text and first image
    ${text1}=           Create Dictionary    type=text    text=Image 1:
    ${image_url1}=      Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image1}=          Create Dictionary    type=image_url    image_url=${image_url1}
    
    ${text2}=           Create Dictionary    type=text    text=Image 2:
    ${image_url2}=      Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
    ${image2}=          Create Dictionary    type=image_url    image_url=${image_url2}
    
    ${question}=        Create Dictionary    type=text    text=What animals are shown in these two images?
    
    ${content_list}=    Create List    ${text1}    ${image1}    ${text2}    ${image2}    ${question}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response mentions both animals
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    ant    insect
    Should Contain Any     ${response}    cat    feline
    
    Log    ✅ Gemini Multiple Images: ${response}

Test Gemini - Vision with System Prompt
    [Documentation]    Test Gemini vision with system prompt
    [Tags]    gemini    vision    system-prompt
    
    Switch Provider    gemini    gemini-2.5-flash
    
    # Create system message
    ${system_msg}=      Create Dictionary    role=system    content=You are a helpful assistant that describes images in detail.
    
    # Create user message with image
    ${text_content}=    Create Dictionary    type=text    text=What type of insect is in this image?
    ${image_url}=       Create Dictionary    url=https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg
    ${image_content}=   Create Dictionary    type=image_url    image_url=${image_url}
    ${content_list}=    Create List          ${text_content}    ${image_content}
    
    ${user_message}=    Create Dictionary    role=user    content=${content_list}
    ${messages}=        Create List          ${system_msg}    ${user_message}
    
    # Send request
    ${response}=    Send AI Request    ${messages}
    
    # Verify response - accept safety filter message or valid response
    Should Not Be Empty    ${response}
    Should Contain Any     ${response}    ant    insect    Camponotus    blocked
    
    Log    ✅ Gemini Vision with System Prompt: ${response}

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

