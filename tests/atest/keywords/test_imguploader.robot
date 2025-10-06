*** Settings ***
Documentation    Tests pour ImageUploader - teste tous les cas de fallback
Library          Collections
Library          String
Library          OperatingSystem
Library          ImageUploaderTestLibrary.py
Documentation    Tests for ImageUploader - tests all fallback cases
...              only test file for image uploading
...              recieve image base64 return link or base64 if failed to upload 
*** Variables ***
${SAMPLE_BASE64}    iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==

*** Test Cases ***
Test Upload With ImgBB Provider
    [Documentation]    Teste l'upload avec le provider ImgBB configuré
    [Tags]    imgbb    success
    ${result}=    Test Upload With ImgBB    ${SAMPLE_BASE64}
    Should Start With    ${result}    https://
    Log    ✅ Upload ImgBB réussi: ${result}

Test Upload With FreeImageHost Provider
    [Documentation]    Teste l'upload avec le provider FreeImageHost configuré
    [Tags]    freeimagehost    success
    ${result}=    Test Upload With FreeImageHost    ${SAMPLE_BASE64}
    Should Start With    ${result}    https://
    Log    ✅ Upload FreeImageHost réussi: ${result}

Test Fallback When No Provider Configured
    [Documentation]    Teste le fallback vers base64 quand aucun provider n'est configuré
    [Tags]    fallback    no-provider
    ${result}=    Test Upload Without Provider    ${SAMPLE_BASE64}
    Should Start With    ${result}    data:image/png;base64,
    Should Contain    ${result}    ${SAMPLE_BASE64}
    Log    ✅ Fallback sans provider: retour base64 confirmé

Test Fallback When Upload Returns None
    [Documentation]    Teste le fallback quand l'upload échoue et retourne None
    [Tags]    fallback    upload-failed
    ${result}=    Test Upload Returning None    ${SAMPLE_BASE64}
    Should Start With    ${result}    data:image/png;base64,
    Should Contain    ${result}    ${SAMPLE_BASE64}
    Log    ✅ Fallback upload échoué: retour base64 confirmé

Test Fallback When Upload Raises Exception
    [Documentation]    Teste le fallback quand une exception est levée pendant l'upload
    [Tags]    fallback    exception
    ${result}=    Test Upload With Exception    ${SAMPLE_BASE64}
    Should Start With    ${result}    data:image/png;base64,
    Should Contain    ${result}    ${SAMPLE_BASE64}
    Log    ✅ Fallback exception: retour base64 confirmé

Test Auto Selection With ImgBB Key
    [Documentation]    Teste la sélection automatique avec clé ImgBB présente
    [Tags]    auto-select    imgbb
    ${result}=    Test Auto Select ImgBB    ${SAMPLE_BASE64}
    Should Start With    ${result}    https://
    Log    ✅ Auto-select ImgBB réussi

Test Auto Selection With FreeImageHost Key
    [Documentation]    Teste la sélection automatique avec clé FreeImageHost présente
    [Tags]    auto-select    freeimagehost
    ${result}=    Test Auto Select FreeImageHost    ${SAMPLE_BASE64}
    Should Start With    ${result}    https://
    Log    ✅ Auto-select FreeImageHost réussi

Test Warning Messages Are Logged
    [Documentation]    Vérifie que les messages de warning sont bien loggés
    [Tags]    logging    warning
    ${warnings}=    Test Get Warning Messages    ${SAMPLE_BASE64}
    ${warning_count}=    Get Length    ${warnings}
    Should Be True    ${warning_count} > 0
    Log Many    @{warnings}
    Log    ✅ ${warning_count} warning(s) loggé(s) correctement

Test Multiple Fallbacks In Sequence
    [Documentation]    Teste plusieurs appels avec fallback en séquence
    [Tags]    fallback    sequence
    ${result1}=    Test Upload Without Provider    ${SAMPLE_BASE64}
    ${result2}=    Test Upload Returning None    ${SAMPLE_BASE64}
    ${result3}=    Test Upload With Exception    ${SAMPLE_BASE64}
    
    Should Start With    ${result1}    data:image/png;base64,
    Should Start With    ${result2}    data:image/png;base64,
    Should Start With    ${result3}    data:image/png;base64,
    Log    ✅ Séquence de fallbacks testée avec succès

*** Keywords ***
Should Start With
    [Arguments]    ${string}    ${prefix}
    ${starts}=    Evaluate    "${string}".startswith("${prefix}")
    Should Be True    ${starts}    String '${string}' should start with '${prefix}'

