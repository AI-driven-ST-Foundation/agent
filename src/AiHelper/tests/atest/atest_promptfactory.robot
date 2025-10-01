*** Settings ***
Library    src.AiHelper.AiHelper

Library    Collections
*** Variables ***
# ${system_prompt_icon_detection}=    "Tu es un expert en reconnaissance visuelle et extraction de données à partir des images"
${prompt_icon_detection}=    "Je voudrais tracer un bouding box autour de chaque ligne de transport 
...   
...  je voudrais que tu me retourner un JSON avec les coordonnées de la ligne RER A et RER B 
...  Le json doit etre sous ce format :
...  {
...      "RER_A": {"x": valeur, "y": valeur, "width": valeur, "height": valeur},
...      "RER_B": {"x": valeur, "y": valeur, "width": valeur, "height": valeur},
...  }
...  "
${prompt_icon_detection2}=    "Je suis un robot , Je voudrais cliquer sur l'icone de la ligne RER A, 
...    tu peux me retourner les coordonnées de la ligne RER A sur cette screenshot de 
...    l'application mobile ? que je teste actuellement"

${prompt_icon_detection3}=    "Je voudrais que tu charge l'image avec ses dimensions actuelles 
...    tu peux me dire ce bounding box correspond a quelle ligne de transport ?
...    "BoundingBox_335_1486": {
...        "x": 335,
...        "y": 1486,
...        "width": 27,
...        "height": 27
...    }"

*** Test Cases ***
Use Prompt Factory Keywords 
    ${system_prompt}=   Create System Prompt    Vous êtes un expert en tests logiciels d'applications mobiles
    ${user_prompt1}=    Create User Prompt    text=compare les deux images  
    ${user_prompt2}=    Create User Prompt    text=ceci est l'image actuelle           
    #image_url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    ${user_prompt3}=    Create User Prompt    text=ceci est l'image de réference    
    #image_url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    ${user_prompt4}=    Create User Prompt    text=Veuillez comparer les deux images et fournir une réponse structurée au format JSON avec les champs suivants: confidence_level, confidence_explanation, test_result, bugs (avec bug_description, bug_severity, bug_screenshot_region) et suggestions
    
    ${messages}=    Create List    ${system_prompt}    ${user_prompt1}    ${user_prompt2}    ${user_prompt3}    ${user_prompt4}
    ${AI_RESPONSE}=    Send AI Request    ${messages}
    Log    ${AI_RESPONSE}


Use Prompt Factory Keywords 2
    # ${system_prompt}=   Create System Prompt    ${system_prompt_icon_detection} 
    ${user_prompt1}=    Create User Prompt    text=${prompt_icon_detection3}    image_url=https://i.ibb.co/zV8KpdB6/infor-traffic.png
    # ${user_prompt2}=    Create User Prompt    text=prompt
    # ${user_prompt3}=    Create User Prompt    text=ceci est l'image de réference    image_url=https://i.ibb.co/0RvxGMZr/screenshot-png.jpg
    # ${user_prompt4}=    Create User Prompt    text=Veuillez comparer les deux images et fournir une réponse structurée au format JSON avec les champs suivants: confidence_level, confidence_explanation, test_result, bugs (avec bug_description, bug_severity, bug_screenshot_region) et suggestions
    
    ${messages}=    Create List        ${user_prompt1}    
    ${AI_RESPONSE}=    Send AI Request    ${messages}    #gpt-4o    1    8000    
    Log    ${AI_RESPONSE}