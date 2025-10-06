*** Settings ***
Documentation    Integration Tests for AgentPromptComposer
...              Real tests using the actual PromptComposerTestLibrary
...              Testing end-to-end prompt composition flows
Library          Collections
Library          tests.utest.library_promptcomposer


*** Variables ***
${TEST_INSTRUCTION_DO}         Cliquer sur le bouton "Se connecter"
${TEST_INSTRUCTION_CHECK}      Vérifier que le message "Bienvenue" est affiché


*** Test Cases ***
Integration Test - DO Messages With Real Composer
    [Documentation]    Test DO message composition with actual library
    [Tags]    integration    do    real
    
    # Compose messages using real library
    ${messages}=    Compose DO Messages    ${TEST_INSTRUCTION_DO}
    
    # Verify structure
    ${msg_count}=    Get Length    ${messages}
    Should Be Equal As Integers    ${msg_count}    2
    
    # Verify first message is system
    ${system_msg}=    Set Variable    ${messages[0]}
    Should Be Equal    ${system_msg}[role]    system
    
    # Verify system content contains action-related terms
    ${system_content}=    Extract Message Content Text    ${system_msg}
    Should Contain Any    ${system_content}    action    mobile test    AppiumLibrary
    
    # Verify second message is user
    ${user_msg}=    Set Variable    ${messages[1]}
    Should Be Equal    ${user_msg}[role]    user
    
    # Verify user content contains instruction
    ${user_content}=    Extract Message Content Text    ${user_msg}
    Should Contain    ${user_content}    ${TEST_INSTRUCTION_DO}
    
    Log    ✅ DO Messages integration test passed

Integration Test - CHECK Messages With Real Composer
    [Documentation]    Test CHECK message composition with actual library
    [Tags]    integration    check    real
    
    # Compose messages using real library
    ${messages}=    Compose CHECK Messages    ${TEST_INSTRUCTION_CHECK}
    
    # Verify structure
    ${msg_count}=    Get Length    ${messages}
    Should Be Equal As Integers    ${msg_count}    2
    
    # Verify first message is system
    ${system_msg}=    Set Variable    ${messages[0]}
    Should Be Equal    ${system_msg}[role]    system
    
    # Verify system content contains assertion-related terms
    ${system_content}=    Extract Message Content Text    ${system_msg}
    Should Contain Any    ${system_content}    assertion    verification    AppiumLibrary
    
    # Verify second message is user
    ${user_msg}=    Set Variable    ${messages[1]}
    Should Be Equal    ${user_msg}[role]    user
    
    # Verify user content contains instruction
    ${user_content}=    Extract Message Content Text    ${user_msg}
    Should Contain    ${user_content}    ${TEST_INSTRUCTION_CHECK}
    
    Log    ✅ CHECK Messages integration test passed

Integration Test - DO Messages With UI Elements
    [Documentation]    Test DO message composition with UI elements
    [Tags]    integration    do    ui-elements
    
    # Create sample UI elements
    ${element1}=    Create Dictionary
    ...    text=Login
    ...    resource_id=com.example:id/btn_login
    ...    content_desc=Login button
    ...    class_name=android.widget.Button
    
    ${element2}=    Create Dictionary
    ...    text=Password
    ...    resource_id=com.example:id/input_password
    ...    content_desc=${EMPTY}
    ...    class_name=android.widget.EditText
    
    ${ui_elements}=    Create List    ${element1}    ${element2}
    
    # Compose messages with UI elements
    ${messages}=    Compose DO Messages
    ...    instruction=Taper le mot de passe
    ...    ui_elements=${ui_elements}
    
    # Verify messages created
    ${msg_count}=    Get Length    ${messages}
    Should Be Equal As Integers    ${msg_count}    2
    
    # Extract and verify user content mentions UI elements
    ${user_msg}=    Set Variable    ${messages[1]}
    ${user_content}=    Extract Message Content Text    ${user_msg}
    
    # Should contain UI element information
    Should Contain Any    ${user_content}    Login    Password    btn_login    input_password
    
    Log    ✅ DO Messages with UI elements test passed

Integration Test - DO Messages With Image URL
    [Documentation]    Test DO message composition with image URL
    [Tags]    integration    do    image
    
    ${image_url}=    Set Variable    https://example.com/screenshot.png
    
    # Compose messages with image
    ${messages}=    Compose DO Messages
    ...    instruction=Identifier l'élément dans l'image
    ...    image_url=${image_url}
    
    # Verify messages created
    ${msg_count}=    Get Length    ${messages}
    Should Be Equal As Integers    ${msg_count}    2
    
    # Verify user message has image
    ${user_msg}=    Set Variable    ${messages[1]}
    ${has_image}=    Message Has Image URL    ${user_msg}
    Should Be True    ${has_image}
    
    Log    ✅ DO Messages with image URL test passed

Integration Test - Complete DO Flow With All Parameters
    [Documentation]    Test complete DO flow with all parameters
    [Tags]    integration    do    complete
    
    # Create UI elements
    ${element}=    Create Dictionary
    ...    text=Submit
    ...    resource_id=com.example:id/btn_submit
    ...    class_name=android.widget.Button
    ${ui_elements}=    Create List    ${element}
    
    # Compose with all parameters
    ${messages}=    Compose DO Messages
    ...    instruction=Cliquer sur le bouton de soumission
    ...    ui_elements=${ui_elements}
    ...    image_url=https://example.com/screen.png
    
    # Verify complete structure
    Should Be Equal As Integers    ${{len($messages)}}    2
    
    ${user_msg}=    Set Variable    ${messages[1]}
    ${has_image}=    Message Has Image URL    ${user_msg}
    Should Be True    ${has_image}
    
    ${content}=    Extract Message Content Text    ${user_msg}
    Should Contain    ${content}    Submit
    
    Log    ✅ Complete DO flow test passed

Integration Test - Real DO Keyword Catalog
    [Documentation]    Test real DO keyword catalog
    [Tags]    integration    catalog    do
    
    # Get real DO keywords
    ${keywords}=    Get DO Keywords
    
    # Verify we have keywords
    ${count}=    Get Length    ${keywords}
    Should Be True    ${count} >= 4    Should have at least 4 DO actions
    
    # Verify specific actions exist
    ${tap_exists}=    Verify DO Action Exists    tap
    Should Be True    ${tap_exists}
    
    ${type_exists}=    Verify DO Action Exists    type
    Should Be True    ${type_exists}
    
    ${clear_exists}=    Verify DO Action Exists    clear
    Should Be True    ${clear_exists}
    
    # Verify tap keyword details
    ${tap_kw}=    Get Keyword By Action    tap
    Should Be Equal    ${tap_kw}[rf_keyword]    Click Element
    Should Be True     ${tap_kw}[requires_locator]
    
    # Verify type keyword details
    ${type_kw}=    Get Keyword By Action    type
    Should Be Equal    ${type_kw}[rf_keyword]    Input Text
    Should Be True     ${type_kw}[requires_locator]
    
    Log    ✅ Real DO keyword catalog test passed
    Log    Found ${count} DO actions in catalog


Integration Test - Real Locator Strategies
    [Documentation]    Test real locator strategies from platform
    [Tags]    integration    catalog    locator
    
    # Get real locator strategies
    ${strategies}=    Get Locator Strategies
    
    # Verify we have strategies
    ${count}=    Get Length    ${strategies}
    Should Be True    ${count} >= 3    Should have at least 3 locator strategies
    
    # Verify essential strategies exist
    List Should Contain Value    ${strategies}    xpath
    List Should Contain Value    ${strategies}    id
    
    Log    ✅ Real locator strategies test passed
    Log    Available strategies: ${strategies}

Integration Test - DO Output Schema Validation
    [Documentation]    Test real DO output schema structure
    [Tags]    integration    schema    do
    
    # Get real DO schema
    ${schema}=    Get DO Output Schema
    
    # Verify schema structure
    Should Be Equal    ${schema}[type]    object
    
    # Verify required fields
    List Should Contain Value    ${schema}[required]    action
    List Should Contain Value    ${schema}[required]    locator
    
    # Verify properties
    Dictionary Should Contain Key    ${schema}[properties]    action
    Dictionary Should Contain Key    ${schema}[properties]    locator
    Dictionary Should Contain Key    ${schema}[properties]    text
    Dictionary Should Contain Key    ${schema}[properties]    options
    
    # Verify action property has enum
    ${action_prop}=    Get From Dictionary    ${schema}[properties]    action
    Dictionary Should Contain Key    ${action_prop}    enum
    
    # Verify enum contains expected actions
    ${action_enum}=    Get From Dictionary    ${action_prop}    enum
    List Should Contain Value    ${action_enum}    tap
    List Should Contain Value    ${action_enum}    type
    
    Log    ✅ DO output schema validation passed

Integration Test - CHECK Output Schema Validation
    [Documentation]    Test real CHECK output schema structure
    [Tags]    integration    schema    check
    
    # Get real CHECK schema (visual check schema)
    ${schema}=    Get CHECK Output Schema
    
    # Verify schema structure
    Should Be Equal    ${schema}[type]    object
    
    # Verify required fields (visual check schema has different required fields)
    List Should Contain Value    ${schema}[required]    verification_result
    List Should Contain Value    ${schema}[required]    confidence_score
    List Should Contain Value    ${schema}[required]    analysis
    
    # Verify properties
    Dictionary Should Contain Key    ${schema}[properties]    verification_result
    Dictionary Should Contain Key    ${schema}[properties]    confidence_score
    Dictionary Should Contain Key    ${schema}[properties]    analysis
    
    # Verify verification_result is boolean
    ${verification_prop}=    Get From Dictionary    ${schema}[properties]    verification_result
    Should Be Equal    ${verification_prop}[type]    boolean
    
    # Verify confidence_score is number with min/max
    ${confidence_prop}=    Get From Dictionary    ${schema}[properties]    confidence_score
    Should Be Equal    ${confidence_prop}[type]    number
    Should Be Equal    ${confidence_prop}[minimum]    ${0.0}
    Should Be Equal    ${confidence_prop}[maximum]    ${1.0}
    
    Log    ✅ CHECK output schema validation passed

Integration Test - Catalog Text Rendering
    [Documentation]    Test real catalog text rendering
    [Tags]    integration    catalog    render
    
    # Render DO catalog
    ${do_catalog}=    Render Catalog Text For Action    do
    Should Not Be Empty    ${do_catalog}
    Should Contain    ${do_catalog}    tap
    Should Contain    ${do_catalog}    type
    Should Contain    ${do_catalog}    Click Element
    
    # Render CHECK catalog (returns DO catalog since visual check doesn't use keywords)
    ${check_catalog}=    Render Catalog Text For Action    check
    Should Not Be Empty    ${check_catalog}
    # Note: Visual check returns DO catalog since it doesn't have its own keywords
    Should Contain    ${check_catalog}    tap
    Should Contain    ${check_catalog}    type
    
    Log    ✅ Catalog text rendering test passed
    Log    DO Catalog:\n${do_catalog}
    Log    CHECK Catalog (visual check):\n${check_catalog}

Integration Test - UI Elements Rendering
    [Documentation]    Test real UI elements rendering
    [Tags]    integration    ui-rendering
    
    # Test with empty list
    ${empty_rendered}=    Render UI Elements    ${None}
    Should Contain    ${empty_rendered}    aucun élément
    
    # Test with actual elements
    ${element}=    Create Dictionary
    ...    text=Login Button
    ...    resource_id=com.example:id/btn_login
    ...    content_desc=Login
    ...    class_name=android.widget.Button
    
    ${elements}=    Create List    ${element}
    ${rendered}=    Render UI Elements    ${elements}
    
    Should Not Contain    ${rendered}    aucun élément
    Should Contain    ${rendered}    Login Button
    Should Contain    ${rendered}    btn_login
    
    Log    ✅ UI elements rendering test passed
    Log    Rendered:\n${rendered}

Integration Test - DO Action Counts
    [Documentation]    Verify counts of DO actions
    [Tags]    integration    catalog    count
    
    # Count DO actions
    ${do_count}=    Count DO Actions
    Should Be True    ${do_count} >= 4
    
    Log    ✅ DO action counts verified
    Log    DO Actions: ${do_count}

Integration Test - AI Response Validation
    [Documentation]    Test AI response validation with real scenarios
    [Tags]    integration    ai-validation    concrete
    
    # Test DO response validation
    ${do_response}=    Create Dictionary    
    ...    action=tap
    ...    locator=id=com.example:id/btn_login
    ...    text=${EMPTY}
    ...    options=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${do_response}
    ${structure_valid}=    Validate DO Response Structure    ${json_response}
    Should Be True    ${structure_valid}    DO response should pass structure validation
    
    ${completeness_valid}=    Validate Response Completeness    ${json_response}    do
    Should Be True    ${completeness_valid}    DO response should pass completeness validation
    
    # Test CHECK response validation
    ${check_response}=    Create Dictionary    
    ...    verification_result=${TRUE}
    ...    confidence_score=${0.9}
    ...    analysis=The login button is clearly visible and clickable
    ...    found_elements=button
    ...    issues=${EMPTY}
    
    ${json_response}=    Convert To JSON    ${check_response}
    ${structure_valid}=    Validate CHECK Response Structure    ${json_response}
    Should Be True    ${structure_valid}    CHECK response should pass structure validation
    
    ${completeness_valid}=    Validate Response Completeness    ${json_response}    check
    Should Be True    ${completeness_valid}    CHECK response should pass completeness validation
    
    Log    ✅ AI response validation passed

Integration Test - Invalid AI Response Handling
    [Documentation]    Test handling of invalid AI responses
    [Tags]    integration    ai-validation    error-handling
    
    # Test invalid DO response (missing required fields)
    ${invalid_do_response}=    Create Dictionary    
    ...    action=tap
    # Missing locator field
    
    ${json_response}=    Convert To JSON    ${invalid_do_response}
    ${structure_valid}=    Validate DO Response Structure    ${json_response}
    Should Be Equal    ${structure_valid}    ${FALSE}    Invalid DO response should fail validation
    
    # Test invalid CHECK response (invalid confidence score)
    ${invalid_check_response}=    Create Dictionary    
    ...    verification_result=${TRUE}
    ...    confidence_score=${1.5}    # Invalid: > 1.0
    ...    analysis=Test analysis
    
    ${json_response}=    Convert To JSON    ${invalid_check_response}
    ${structure_valid}=    Validate CHECK Response Structure    ${json_response}
    Should Be Equal    ${structure_valid}    ${FALSE}    Invalid CHECK response should fail validation
    
    Log    ✅ Invalid AI response handling passed


*** Keywords ***
Should Contain Any
    [Documentation]    Verify text contains at least one of the keywords
    [Arguments]    ${text}    @{keywords}
    ${found}=    Set Variable    ${FALSE}
    FOR    ${keyword}    IN    @{keywords}
        ${contains}=    Run Keyword And Return Status    
        ...    Should Contain    ${text}    ${keyword}    ignore_case=True
        ${found}=    Set Variable If    ${contains}    ${TRUE}    ${found}
    END
    Should Be True    ${found}    
    ...    Text '${text}' does not contain any of: ${keywords}

Convert To JSON
    [Documentation]    Convert dictionary to JSON string
    [Arguments]    ${data}
    ${json_string}=    Evaluate    json.dumps($data)    json
    RETURN    ${json_string}

