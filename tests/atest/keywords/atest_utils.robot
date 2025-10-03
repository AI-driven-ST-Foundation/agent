*** Settings ***
Library    Libraries.AiHelper
Resource    resource/common.robot
Library    Collections
*** Keywords ***
Create System Prompt
    [Arguments]    ${system_prompt}
    ${system_message}=    Create Dictionary    role=system    content=${system_prompt}
    RETURN    ${system_message}

Create User Prompt
    [Arguments]    ${text}    ${image_url}=${None}
    ${text_item}=         Create Dictionary    type=text    text=${text}
    IF    '${image_url}'!='${None}'
        ${image_url}=         Create Dictionary    url=${image_url}
        ${image_item}=        Create Dictionary    type=image_url    image_url=${image_url}
        ${user_content}=      Create List          ${text_item}    ${image_item}
    ELSE
        ${user_content}=      Create List          ${text_item}
    END

    ${user_message}=      Create Dictionary    role=user    content=${user_content}
    RETURN    ${user_message}

*** Test Cases ***
Upload Screenshot File
    ${screenshot_url}=    Upload Screenshot File    ${EXECDIR}/Libraries/OpenAI/tests/infor_traffic.png
    Log    ${screenshot_url}

Upload Screenshot Base64
    ${screenshot_base64}=    Encode Image To Base64    ${EXECDIR}/Libraries/OpenAI/tests/communauto.png
    ${screenshot_url}=    Upload Screenshot Base64    ${screenshot_base64}
    Log    ${screenshot_url}

Construire JSON Rich
    # system prompt
    ${system_message}=    Create Dictionary    role=system    content=Vous êtes un expert en tests logiciels d'applications mobiles

    # element 1 text
    ${text_item}=         Create Dictionary    type=text    text=est ce la destination goncourt a été affiché sur cet écran ?
    # element 2 url image
    ${image_url}=         Create Dictionary    url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    ${image_item}=        Create Dictionary    type=image_url    image_url=${image_url}
    ${user_content}=      Create List          ${text_item}    ${image_item}
    #former le prompt user 
    ${user_message}=      Create Dictionary    role=user    content=${user_content}

    # assemblage du prompt final
    ${messages}=          Create List          ${system_message}    ${user_message}

    # envoyer la requête au IA 
    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}




COMPARE IMAGES BY ASKING AI 
    ${system_prompt}=   Create System Prompt    Vous êtes un expert en tests logiciels d'applications mobiles
    ${user_prompt1}=    Create User Prompt    text=compare les deux images  
    ${user_prompt2}=    Create User Prompt    text=ceci est l'image actuelle    image_url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    ${user_prompt3}=    Create User Prompt    text=ceci est l'image de réference    image_url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    ${user_prompt4}=    Create User Prompt    text=Veuillez comparer les deux images et fournir une réponse structurée au format JSON avec les champs suivants: confidence_level, confidence_explanation, test_result, bugs (avec bug_description, bug_severity, bug_screenshot_region) et suggestions
    
    ${messages}=    Create List    ${system_prompt}    ${user_prompt1}    ${user_prompt2}    ${user_prompt3}    ${user_prompt4}
    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}