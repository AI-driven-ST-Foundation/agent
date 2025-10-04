*** Settings ***
Library    src.AiHelper.AiHelper
Library    AppiumLibrary
Library    Collections
*** Test Cases ***
*** Settings ***
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



Send AI Request
    ${system_prompt}=    Create Dictionary    role=system    content=Hello

    ${user_prompt}=    Create Dictionary    role=user    content=What is the capital of France?

    ${content_list}=    Create List    ${user_prompt}

    ${user_prompt}=    Create Dictionary    role=user    content=${content_list}


    @{messages}=    Create List    ${system_prompt}    ${user_prompt}


    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}

Send AI Request With Image
    ${system_prompt}=    Create Dictionary    role=system    content=Hello

    ${user_prompt}=    Create Dictionary    role=user    content=Descibe This Image

    ${content}=      Create Dictionary    type=text    text=Descibe This Image
    ${image_url}=    Create Dictionary    url=https://i.ibb.co/XxNvsP0N/screenshot-png.jpg
    ${image_content}=    Create Dictionary    type=image_url    image_url=${image_url}

    ${content_list}=    Create List    ${content}    ${image_content}

    ${message2}=    Create Dictionary    role=user    content=${content_list}
    @{messages}=    Create List    ${message2}    ${message2}
    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}

Upload Screenshot File
    ${screenshot_url}=    Upload Screenshot File    ${EXECDIR}/Libraries/OpenAI/tests/communauto.png
    Log    ${screenshot_url}

Upload Screenshot Base64
    ${screenshot_base64}=    Encode Image To Base64    ${EXECDIR}/Libraries/OpenAI/tests/communauto.png
    ${screenshot_url}=    Upload Screenshot Base64    ${screenshot_base64}
    Log    ${screenshot_url}

Test AI Verification
    ${screenshot_base64}=    Encode Image To Base64    ${EXECDIR}/Libraries/OpenAI/tests/communauto.png
    ${screenshot_url}=    Upload Screenshot Base64    ${screenshot_base64}
    Log    ${screenshot_url}
    ${message1}=    Create Dictionary    role=developer    content=You are an expert of software testing of mobile application
    ...    and you are testing the mobility as a service application
    ${message2}=    Create Dictionary    role=user    content=The screenshot is a screenshot of a logo
    ${message3}=    Create Dictionary    role=assistant    content=What is the name of the application?
    ${messages}=    Create List    ${message1}    ${message2}    ${message3}
    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}

Test AI Verification 2
    ${screenshot_base64}=    Encode Image To Base64    ${EXECDIR}/Libraries/AiHelper/tests/screenshot_infotraffic.png
    ${screenshot_url}=    Upload Screenshot Base64    ${screenshot_base64}
    
    ${image_url}=    Create Dictionary   
    ...    url=${screenshot_url}

    ${image_content}=    Create Dictionary
    ...    type=image_url
    ...    image_url=${image_url}
    
    ${text_content}=    Create Dictionary
    ...    type=text
    ...    text=est ce la destination goncourt a été affiché sur cet écran ?
    
    ${content_list}=    Create List    ${text_content}    ${image_content}
    
    ${message}=    Create Dictionary
    ...    role=user
    ...    content=${content_list}
    
    ${system_prompt}=    Create Dictionary    
    ...    role=system    
    ...    content=Vous êtes un expert en tests logiciels d'applications mobiles
    
    ${messages}=    Create List    ${system_prompt}    ${message}
    Log    ${messages}
    ${AI_RESPONSE}=    Send AI Request    ${messages}    model=gpt-4o-mini
    Log    ${AI_RESPONSE}

Test AI Verification 3
    ${screenshot_base64}=    Encode Image To Base64    ${EXECDIR}/Libraries/OpenAI/tests/s5.jpeg
    ${screenshot_url}=       Upload Screenshot Base64    ${screenshot_base64}
    
    # Construction correcte de l'URL d'image
    ${image_url}=    Create Dictionary    
    ...    url=${screenshot_url}    
    ...    detail=high  # Ajout important pour l'analyse visuelle

    ${image_content}=    Create Dictionary    
    ...    type=image_url    
    ...    image_url=${image_url}  # Structure imbriquée correcte

    ${text_content}=    Create Dictionary    
    ...    type=text    
    ...    text=Est-ce que la destination Goncourt a été affichée sur cet écran ?

    ${content_list}=    Create List    ${text_content}    ${image_content}
    
    ${message}=    Create Dictionary    
    ...    role=user    
    ...    content=${content_list}
    
    ${system_prompt}=    Create Dictionary    
    ...    role=system    
    ...    content=Vous êtes un expert en tests logiciels d'applications mobiles
    
    ${messages}=    Create List    ${system_prompt}    ${message}
    
    # Appel avec les bons paramètres
    ${AI_RESPONSE}=    Send AI Request   
    ...    ${messages}    
    ...    model=gpt-4o-mini  # Modèle officiel pour les images
    ...    max_tokens=300
    
    Log    ${AI_RESPONSE}

Test AI Verification- ASK LLM TO VERIFY SCREENSHOT
    # __Launch IDFM App
    ${system_prompt}=   set variable    Vous êtes un expert en tests logiciels d'applications mobiles de transport et information voyageur    
    ${user_prompt}=     set variable    sur cet écran il est affiché les bouton j'accepte en bleu dans le bon endroit ?

    ${AI_RESPONSE}=    Ask AI For Verification    ${system_prompt}    ${user_prompt}
    Log    ${AI_RESPONSE}