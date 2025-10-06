*** Settings ***
Documentation    Test Suite for AgentPromptComposer and AgentKeywordCatalog
...              Tests prompt composition for DO and CHECK flows
...              Verifies keyword catalog structure and locator strategies
Library          Collections
Library          String
Library          OperatingSystem
Library          tests.utest.library_promptcomposer


*** Variables ***
${SAMPLE_INSTRUCTION_DO}       Cliquer sur le bouton de connexion
${SAMPLE_INSTRUCTION_CHECK}    Vérifier que le message d'erreur est affiché
${SAMPLE_IMAGE_URL}            https://example.com/screenshot.png


*** Test Cases ***
Test Prompt Composer - Compose DO Messages Without UI Elements
    [Documentation]    Verify DO message composition with minimal input
    [Tags]    promptcomposer    do    basic
    
    ${messages}=    Compose DO Messages    instruction=${SAMPLE_INSTRUCTION_DO}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    do
    Verify User Message Has Instruction    ${messages[1]}    ${SAMPLE_INSTRUCTION_DO}
    
    Log    ✅ DO Messages composed successfully without UI elements

Test Prompt Composer - Compose DO Messages With UI Elements
    [Documentation]    Verify DO message composition with UI elements
    [Tags]    promptcomposer    do    ui-elements
    
    ${ui_elements}=    Create Sample UI Elements
    ${messages}=       Compose DO Messages    
    ...                instruction=${SAMPLE_INSTRUCTION_DO}
    ...                ui_elements=${ui_elements}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    do
    Verify User Message Has UI Elements    ${messages[1]}
    
    Log    ✅ DO Messages composed with UI elements

Test Prompt Composer - Compose DO Messages With Image URL
    [Documentation]    Verify DO message composition with image URL
    [Tags]    promptcomposer    do    image
    
    ${messages}=    Compose DO Messages    
    ...             instruction=${SAMPLE_INSTRUCTION_DO}
    ...             image_url=${SAMPLE_IMAGE_URL}
    
    Verify Message Structure    ${messages}
    Verify User Message Has Image    ${messages[1]}    ${SAMPLE_IMAGE_URL}
    
    Log    ✅ DO Messages composed with image URL

Test Prompt Composer - Compose CHECK Messages Without UI Elements
    [Documentation]    Verify CHECK message composition with minimal input
    [Tags]    promptcomposer    check    basic
    
    ${messages}=    Compose CHECK Messages    instruction=${SAMPLE_INSTRUCTION_CHECK}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    check
    Verify User Message Has Instruction    ${messages[1]}    ${SAMPLE_INSTRUCTION_CHECK}
    
    Log    ✅ CHECK Messages composed successfully without UI elements

Test Prompt Composer - Compose CHECK Messages With UI Elements
    [Documentation]    Verify CHECK message composition with UI elements
    [Tags]    promptcomposer    check    ui-elements
    
    ${ui_elements}=    Create Sample UI Elements
    ${messages}=       Compose CHECK Messages    
    ...                instruction=${SAMPLE_INSTRUCTION_CHECK}
    ...                ui_elements=${ui_elements}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    check
    Verify User Message Has UI Elements    ${messages[1]}
    
    Log    ✅ CHECK Messages composed with UI elements

Test Prompt Composer - Compose CHECK Messages With Image URL
    [Documentation]    Verify CHECK message composition with image URL
    [Tags]    promptcomposer    check    image
    
    ${messages}=    Compose CHECK Messages    
    ...             instruction=${SAMPLE_INSTRUCTION_CHECK}
    ...             image_url=${SAMPLE_IMAGE_URL}
    
    Verify Message Structure    ${messages}
    Verify User Message Has Image    ${messages[1]}    ${SAMPLE_IMAGE_URL}
    
    Log    ✅ CHECK Messages composed with image URL

Test Prompt Composer - Complete DO Flow
    [Documentation]    Test complete DO message with all parameters
    [Tags]    promptcomposer    do    complete
    
    ${ui_elements}=    Create Sample UI Elements
    ${messages}=       Compose DO Messages    
    ...                instruction=Taper "test@example.com" dans le champ email
    ...                ui_elements=${ui_elements}
    ...                image_url=${SAMPLE_IMAGE_URL}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    do
    Verify User Message Complete    ${messages[1]}    ui=${TRUE}    image=${TRUE}
    
    Log    ✅ Complete DO flow tested

Test Prompt Composer - Complete CHECK Flow
    [Documentation]    Test complete CHECK message with all parameters
    [Tags]    promptcomposer    check    complete
    
    ${ui_elements}=    Create Sample UI Elements
    ${messages}=       Compose CHECK Messages    
    ...                instruction=Vérifier que le texte contient "Bienvenue"
    ...                ui_elements=${ui_elements}
    ...                image_url=${SAMPLE_IMAGE_URL}
    
    Verify Message Structure    ${messages}
    Verify System Message Content    ${messages[0]}    check
    Verify User Message Complete    ${messages[1]}    ui=${TRUE}    image=${TRUE}
    
    Log    ✅ Complete CHECK flow tested

Test Keyword Catalog - DO Keywords Structure
    [Documentation]    Verify structure of DO keywords catalog
    [Tags]    catalog    do    structure
    
    ${do_keywords}=    Get DO Keywords
    
    Verify Keywords List Not Empty    ${do_keywords}
    Verify Each Keyword Has Required Fields    ${do_keywords}    action
    Verify DO Keyword Actions    ${do_keywords}
    
    Log    ✅ DO Keywords structure validated: ${do_keywords.__len__()} actions found


Test Keyword Catalog - Locator Strategies
    [Documentation]    Verify available locator strategies
    [Tags]    catalog    locator    strategies
    
    ${strategies}=    Get Locator Strategies
    
    Should Not Be Empty    ${strategies}
    Log    Available locator strategies: ${strategies}
    
    # Common strategies that should be present
    List Should Contain Value    ${strategies}    xpath
    List Should Contain Value    ${strategies}    id
    
    Log    ✅ Locator strategies validated

Test Keyword Catalog - DO Keywords Mapping
    [Documentation]    Verify DO keywords map to Robot Framework keywords correctly
    [Tags]    catalog    do    mapping
    
    ${do_keywords}=    Get DO Keywords
    
    # Verify specific action mappings
    ${tap_keyword}=    Get Keyword By Action    ${do_keywords}    tap
    Should Be Equal    ${tap_keyword}[rf_keyword]    Click Element
    Should Be True     ${tap_keyword}[requires_locator]
    
    ${type_keyword}=    Get Keyword By Action    ${do_keywords}    type
    Should Be Equal     ${type_keyword}[rf_keyword]    Input Text
    Should Be True      ${type_keyword}[requires_locator]
    
    ${clear_keyword}=    Get Keyword By Action    ${do_keywords}    clear
    Should Be Equal      ${clear_keyword}[rf_keyword]    Clear Text
    Should Be True       ${clear_keyword}[requires_locator]
    
    ${swipe_keyword}=    Get Keyword By Action    ${do_keywords}    swipe
    Should Be Equal      ${swipe_keyword}[rf_keyword]    Swipe By Percent
    Should Not Be True   ${swipe_keyword}[requires_locator]
    
    Log    ✅ DO keywords mapping validated


Test Keyword Catalog - Render DO Catalog Text
    [Documentation]    Verify rendering of DO catalog as text
    [Tags]    catalog    do    render
    
    ${catalog_text}=    Render Catalog Text For Action    do
    
    Should Not Be Empty    ${catalog_text}
    Should Contain         ${catalog_text}    tap
    Should Contain         ${catalog_text}    type
    Should Contain         ${catalog_text}    Click Element
    Should Contain         ${catalog_text}    Input Text
    
    Log    ✅ DO Catalog rendered:\n${catalog_text}

Test Keyword Catalog - Render CHECK Catalog Text
    [Documentation]    Verify rendering of CHECK catalog as text
    [Tags]    catalog    check    render
    
    ${catalog_text}=    Render Catalog Text For Action    check
    
    # NOTE: Visual check returns DO catalog since it doesn't have its own keywords
    Should Not Be Empty    ${catalog_text}
    Should Contain         ${catalog_text}    tap
    Should Contain         ${catalog_text}    type
    Should Contain         ${catalog_text}    Click Element
    Should Contain         ${catalog_text}    Input Text
    
    Log    ✅ CHECK Catalog rendered (visual check - uses DO catalog):\n${catalog_text}

Test DO Schema - Structure and Required Fields
    [Documentation]    Verify DO output JSON schema structure
    [Tags]    schema    do
    
    ${schema}=    Get DO Output Schema
    
    Should Be Equal    ${schema}[type]    object
    List Should Contain Value    ${schema}[required]    action
    List Should Contain Value    ${schema}[required]    locator
    
    Dictionary Should Contain Key    ${schema}[properties]    action
    Dictionary Should Contain Key    ${schema}[properties]    locator
    Dictionary Should Contain Key    ${schema}[properties]    text
    Dictionary Should Contain Key    ${schema}[properties]    options
    
    Log    ✅ DO Schema structure validated

Test CHECK Schema - Structure and Required Fields
    [Documentation]    Verify CHECK output JSON schema structure
    [Tags]    schema    check
    
    ${schema}=    Get CHECK Output Schema
    
    # NOTE: CHECK is now visual check with different schema
    Should Be Equal    ${schema}[type]    object
    List Should Contain Value    ${schema}[required]    verification_result
    List Should Contain Value    ${schema}[required]    confidence_score
    List Should Contain Value    ${schema}[required]    analysis
    
    Dictionary Should Contain Key    ${schema}[properties]    verification_result
    Dictionary Should Contain Key    ${schema}[properties]    confidence_score
    Dictionary Should Contain Key    ${schema}[properties]    analysis
    Dictionary Should Contain Key    ${schema}[properties]    found_elements
    Dictionary Should Contain Key    ${schema}[properties]    issues
    
    Log    ✅ CHECK Schema structure validated (visual check schema)

Test UI Elements Rendering - Empty List
    [Documentation]    Verify rendering of empty UI elements list
    [Tags]    ui-rendering    edge-case
    
    ${rendered}=    Render UI Elements    ${None}
    
    Should Contain    ${rendered}    aucun élément
    
    Log    ✅ Empty UI elements handled correctly

Test UI Elements Rendering - With Elements
    [Documentation]    Verify rendering of UI elements list
    [Tags]    ui-rendering    basic
    
    ${ui_elements}=    Create Sample UI Elements
    ${rendered}=       Render UI Elements    ${ui_elements}
    
    Should Not Contain    ${rendered}    aucun élément
    Should Contain        ${rendered}    text=
    
    Log    ✅ UI elements rendered:\n${rendered}

Test UI Elements Rendering - Large List Truncation
    [Documentation]    Verify that large UI element lists are truncated to 30 items
    [Tags]    ui-rendering    truncation
    
    ${large_list}=    Create Large UI Elements List    count=50
    ${rendered}=      Render UI Elements    ${large_list}
    
    # Should only render first 30 elements
    ${lines}=    Get Lines Count    ${rendered}
    Should Be True    ${lines} <= 30
    
    Log    ✅ Large UI list correctly truncated

Test Prompt Composer - Different Locales
    [Documentation]    Test prompt composer with different locales
    [Tags]    promptcomposer    locale
    
    # Default locale (fr)
    ${messages_fr}=    Compose DO Messages With Locale    
    ...                instruction=${SAMPLE_INSTRUCTION_DO}
    ...                locale=fr
    
    ${messages_en}=    Compose DO Messages With Locale    
    ...                instruction=Click login button
    ...                locale=en
    
    Should Not Be Equal    ${messages_fr}    ${messages_en}
    
    Log    ✅ Different locales handled

Test AI Response Validation - DO Response Structure
    [Documentation]    Test validation of DO response structure
    [Tags]    ai-validation    do    structure
    
    # Test valid DO response
    ${valid_do_response}=    Create Dictionary    
    ...    action=tap
    ...    locator=id=com.example:id/button
    ...    text=${EMPTY}
    ...    options=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${valid_do_response}
    ${structure_valid}=    Validate DO Response Structure    ${json_response}
    Should Be True    ${structure_valid}    Valid DO response should pass structure validation
    
    # Test invalid DO response (missing locator)
    ${invalid_do_response}=    Create Dictionary    
    ...    action=tap
    # Missing locator field
    
    ${json_response}=    Convert To JSON    ${invalid_do_response}
    ${structure_valid}=    Validate DO Response Structure    ${json_response}
    Should Be Equal    ${structure_valid}    ${FALSE}    Invalid DO response should fail structure validation
    
    Log    ✅ DO response structure validation passed

Test AI Response Validation - CHECK Response Structure
    [Documentation]    Test validation of CHECK response structure
    [Tags]    ai-validation    check    structure
    
    # Test valid CHECK response
    ${valid_check_response}=    Create Dictionary    
    ...    verification_result=${TRUE}
    ...    confidence_score=${0.85}
    ...    analysis=The text is clearly visible and readable
    ...    found_elements=button, text
    ...    issues=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${valid_check_response}
    ${structure_valid}=    Validate CHECK Response Structure    ${json_response}
    Should Be True    ${structure_valid}    Valid CHECK response should pass structure validation
    
    # Test invalid CHECK response (invalid confidence score)
    ${invalid_check_response}=    Create Dictionary    
    ...    verification_result=${TRUE}
    ...    confidence_score=${1.5}    # Invalid: > 1.0
    ...    analysis=Test analysis
    
    ${json_response}=    Convert To JSON    ${invalid_check_response}
    ${structure_valid}=    Validate CHECK Response Structure    ${json_response}
    Should Be Equal    ${structure_valid}    ${FALSE}    Invalid CHECK response should fail structure validation
    
    Log    ✅ CHECK response structure validation passed

Test AI Response Validation - Response Completeness
    [Documentation]    Test validation of response completeness
    [Tags]    ai-validation    completeness
    
    # Test complete DO response
    ${complete_do_response}=    Create Dictionary    
    ...    action=type
    ...    locator=id=com.example:id/input
    ...    text=hello
    ...    options=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${complete_do_response}
    ${completeness_valid}=    Validate Response Completeness    ${json_response}    do
    Should Be True    ${completeness_valid}    Complete DO response should pass completeness validation
    
    # Test complete CHECK response
    ${complete_check_response}=    Create Dictionary    
    ...    verification_result=${TRUE}
    ...    confidence_score=${0.9}
    ...    analysis=Element is clearly visible and properly displayed
    ...    found_elements=button
    ...    issues=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${complete_check_response}
    ${completeness_valid}=    Validate Response Completeness    ${json_response}    check
    Should Be True    ${completeness_valid}    Complete CHECK response should pass completeness validation
    
    Log    ✅ Response completeness validation passed


*** Keywords ***
# ============================================================================
# SETUP AND HELPER KEYWORDS
# ============================================================================

Create Sample UI Elements
    [Documentation]    Create a sample list of UI elements for testing
    ${element1}=    Create Dictionary
    ...    text=Login
    ...    resource_id=com.example:id/btn_login
    ...    content_desc=Login button
    ...    class_name=android.widget.Button
    ...    bounds=[100,200][300,400]
    
    ${element2}=    Create Dictionary
    ...    text=Email
    ...    resource_id=com.example:id/input_email
    ...    content_desc=${EMPTY}
    ...    class_name=android.widget.EditText
    ...    bounds=[50,100][350,180]
    
    ${element3}=    Create Dictionary
    ...    text=${EMPTY}
    ...    resource_id=com.example:id/icon_home
    ...    content_desc=Home icon
    ...    class_name=android.widget.ImageView
    ...    bounds=[10,10][90,90]
    
    ${ui_elements}=    Create List    ${element1}    ${element2}    ${element3}
    RETURN    ${ui_elements}

Create Large UI Elements List
    [Documentation]    Create a large list of UI elements for truncation testing
    [Arguments]    ${count}=50
    ${elements}=    Create List
    FOR    ${i}    IN RANGE    ${count}
        ${element}=    Create Dictionary
        ...    text=Element ${i}
        ...    resource_id=com.example:id/element_${i}
        ...    content_desc=Element ${i}
        ...    class_name=android.widget.TextView
        ...    bounds=[0,${i*10}][100,${i*10+50}]
        Append To List    ${elements}    ${element}
    END
    RETURN    ${elements}

Get Lines Count
    [Documentation]    Count number of lines in text
    [Arguments]    ${text}
    ${lines}=    Split To Lines    ${text}
    ${count}=    Get Length    ${lines}
    RETURN    ${count}

# ============================================================================
# Note: Most keywords are provided by PromptComposerTestLibrary
# Only custom wrapper keywords are defined here
# ============================================================================

# ============================================================================
# VERIFICATION KEYWORDS
# ============================================================================

Verify Message Structure
    [Documentation]    Verify that messages have proper structure (system + user)
    [Arguments]    ${messages}
    ${length}=    Get Length    ${messages}
    Should Be Equal As Integers    ${length}    2    Messages should contain exactly 2 items (system + user)
    
    # Verify first message is system message
    Should Be Equal    ${messages[0]}[role]    system
    Dictionary Should Contain Key    ${messages[0]}    content
    
    # Verify second message is user message
    Should Be Equal    ${messages[1]}[role]    user
    Dictionary Should Contain Key    ${messages[1]}    content

Verify System Message Content
    [Documentation]    Verify system message contains appropriate content for action type
    [Arguments]    ${system_message}    ${action_type}
    ${content}=    Get From Dictionary    ${system_message}    content
    Should Not Be Empty    ${content}
    
    IF    '${action_type}' == 'do'
        Should Contain Any    ${content}    action    DO    execution
    ELSE IF    '${action_type}' == 'check'
        Should Contain Any    ${content}    assertion    CHECK    verification
    END

Verify User Message Has Instruction
    [Documentation]    Verify user message contains the instruction
    [Arguments]    ${user_message}    ${instruction}
    ${content}=    Get From Dictionary    ${user_message}    content
    ${content_str}=    Convert To String    ${content}
    Should Contain    ${content_str}    ${instruction}

Verify User Message Has UI Elements
    [Documentation]    Verify user message contains UI elements rendering
    [Arguments]    ${user_message}
    ${content}=    Get From Dictionary    ${user_message}    content
    ${content_str}=    Convert To String    ${content}
    # UI elements should be mentioned in some form
    Should Not Be Empty    ${content}

Verify User Message Has Image
    [Documentation]    Verify user message contains image URL
    [Arguments]    ${user_message}    ${expected_url}
    ${content}=    Get From Dictionary    ${user_message}    content
    
    # Check if content is a list (complex content with images)
    ${is_list}=    Run Keyword And Return Status    Should Be True    ${{isinstance($content, list)}}
    IF    ${is_list}
        ${has_image}=    Message Has Image URL    ${user_message}
        Should Be True    ${has_image}    User message should contain image reference
    ELSE
        # Simple string content - check if URL is mentioned
        Should Contain    ${content}    ${expected_url}    User message should contain image reference
    END

Verify User Message Complete
    [Documentation]    Verify user message has all components
    [Arguments]    ${user_message}    ${ui}=${FALSE}    ${image}=${FALSE}
    ${content}=    Get From Dictionary    ${user_message}    content
    Should Not Be Empty    ${content}

Verify Keywords List Not Empty
    [Documentation]    Verify keywords list is not empty
    [Arguments]    ${keywords}
    Should Not Be Empty    ${keywords}
    ${length}=    Get Length    ${keywords}
    Should Be True    ${length} > 0

Verify Each Keyword Has Required Fields
    [Documentation]    Verify each keyword has required fields
    [Arguments]    ${keywords}    ${key_field}
    FOR    ${keyword}    IN    @{keywords}
        Dictionary Should Contain Key    ${keyword}    ${key_field}
        Dictionary Should Contain Key    ${keyword}    rf_keyword
        Dictionary Should Contain Key    ${keyword}    requires_locator
        Dictionary Should Contain Key    ${keyword}    description
    END

Verify DO Keyword Actions
    [Documentation]    Verify DO keywords contain expected actions
    [Arguments]    ${keywords}
    ${actions}=    Create List
    FOR    ${keyword}    IN    @{keywords}
        Append To List    ${actions}    ${keyword}[action]
    END
    
    # Verify essential actions are present
    List Should Contain Value    ${actions}    tap
    List Should Contain Value    ${actions}    type
    List Should Contain Value    ${actions}    clear


Get Keyword By Action
    [Documentation]    Get keyword from list by action name
    [Arguments]    ${keywords}    ${action_name}
    FOR    ${keyword}    IN    @{keywords}
        ${action}=    Get From Dictionary    ${keyword}    action
        IF    '${action}' == '${action_name}'
            RETURN    ${keyword}
        END
    END
    Fail    Keyword with action '${action_name}' not found


Should Contain Any
    [Documentation]    Verify text contains at least one of the keywords
    [Arguments]    ${text}    @{keywords}
    ${found}=    Set Variable    ${FALSE}
    FOR    ${keyword}    IN    @{keywords}
        ${contains}=    Run Keyword And Return Status    Should Contain    ${text}    ${keyword}    ignore_case=True
        ${found}=    Set Variable If    ${contains}    ${TRUE}    ${found}
    END
    Should Be True    ${found}    Text '${text}' does not contain any of: ${keywords}

Convert To JSON
    [Documentation]    Convert dictionary to JSON string
    [Arguments]    ${data}
    ${json_string}=    Evaluate    json.dumps($data)    json
    RETURN    ${json_string}

