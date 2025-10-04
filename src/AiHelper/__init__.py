import time
from src.AiHelper.common._logger import RobotCustomLogger
import base64
from robot.libraries.BuiltIn import BuiltIn
from typing import Any, List, Dict, Optional
from src.AiHelper.common._parserutils import BBoxToClickCoordinates
from src.AiHelper.providers.llm._factory import LLMClientFactory
from src.AiHelper.config.config import Config
from robot.api.deco import keyword
from src.AiHelper.providers.imguploader.imghandler import ImageUploader
from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.common._utils import Utilities
from src.AiHelper.common._tiktoken import TokenHelper
from src.AiHelper.providers.promptfactory import ChatPromptFactory
from appium.webdriver.common.appiumby import AppiumBy
from src.AiHelper.providers.llm._huggingface import OmniParser

__all__ = ['AiHelper']


class AiHelper:

    ROBOT_LIBRARY_SCOPE = "TEST"
    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self, client_name=None, model=None):
        self.config = Config()
        self.logger = RobotCustomLogger()
        client_name = client_name or self.config.DEFAULT_LLM_CLIENT
        
        # Select appropriate default model based on provider
        if model is None:
            if client_name == "gemini" or (client_name is None and self.config.DEFAULT_LLM_CLIENT == "gemini"):
                model = self.config.DEFAULT_GEMINI_MODEL
            elif client_name == "anthropic" or (client_name is None and self.config.DEFAULT_LLM_CLIENT == "anthropic"):
                model = self.config.DEFAULT_ANTHROPIC_MODEL
            else:
                model = self.config.DEFAULT_OPENAI_MODEL
        
        # Get API key - pass None and let the factory handle it
        self._client = LLMClientFactory.create_client(client_name, model=model)
        self._last_response = None
        self.img = ImageUploader()
        
        # Use singleton TokenHelper to ensure cost persistence across all instances
        self._token = TokenHelper()
        self.logger.info(f"AiHelper initialized with TokenHelper instance ID: {id(self._token)}", False)
        
        self.prompt = ChatPromptFactory()
        self._cumulated_cost = 0.0
        
        # initialisation conditionnelle de OmniParser ( api non stabkle )
        api_key_huggingface = self.config.HUGGINGFACE_API_KEY
        try:
            self.omniparser = OmniParser(api_key_huggingface) if api_key_huggingface else None
        except Exception as e:
            self.logger.warning(f"Failed to initialize OmniParser: {str(e)}")
            self.omniparser = None

    @keyword("Get Cumulated Cost")
    def get_cumulated_cost(self):
        # Source of truth: TokenHelper accumulator (updated on each calculate_cost call)
        total = round(self._token.get_cumulated_cost(), 5)
        cumulated_tokens = self._token.get_cumulated_tokens()
        self.logger.info(f"Cumulated cost: {total} (from {cumulated_tokens} tokens)", True)
        self.logger.info(f"TokenHelper instance ID: {id(self._token)}", False)
        return total
    
    @keyword("Reset Cumulated Cost")
    def reset_cumulated_cost(self):
        """Reset the cumulated cost and tokens to zero"""
        self._token.reset_accumulation()
        self.logger.info("Cumulated cost and tokens have been reset to zero", True)
        return 0
    
    @keyword("Get Cost Stats Summary")
    def get_cost_stats_summary(self):
        """Get comprehensive cost tracking statistics"""
        stats = self._token.get_stats_summary()
        self.logger.info(f"Cost Stats Summary: {stats}", True)
        # Show file storage info for debugging
        import os
        file_path = "/tmp/ai_cost_tracker.json"
        file_exists = os.path.exists(file_path)
        self.logger.info(f"Cost Storage File: {file_path} (exists: {file_exists})", True)
        if file_exists:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.logger.info(f"File content: {content}", True)
            except Exception as e:
                self.logger.info(f"Error reading file: {e}", True)
        return stats
    
    @keyword("Switch Provider")
    def switch_provider(self, client_name: str, model: Optional[str] = None):
        """
        Switch to a different LLM provider dynamically.
        
        Args:
            client_name: Name of the provider ('openai', 'anthropic', 'gemini')
            model: Optional model name (uses provider default if not specified)
        """
        self.logger.info(f"Switching provider to: {client_name} with model: {model}", True)
        
        # Select appropriate default model if not provided
        if model is None:
            if client_name == "gemini":
                model = self.config.DEFAULT_GEMINI_MODEL
            elif client_name == "anthropic":
                model = self.config.DEFAULT_ANTHROPIC_MODEL
            else:
                model = self.config.DEFAULT_OPENAI_MODEL
        
        # Create new client
        self._client = LLMClientFactory.create_client(client_name, model=model)
        self.logger.info(f"Provider switched successfully. Using {type(self._client).__name__}", True)

    @keyword("Get Current UI XML")
    def get_current_ui_xml(self):
        return Utilities._get_ui_xml()

    @keyword("Upload Screenshot File")
    def upload_screenshot_file(self, file_path: str):
        return self.img.upload_from_file(file_path)

    @keyword("Upload Screenshot Base64")
    def upload_screenshot_base64(self, base64_data: str):
        return self.img.upload_from_base64(base64_data)
    
    @keyword("Take Screenshot As Base64")
    def take_screenshot_as_base64(self, log: bool = True, width: int = 200):
        """ returns the screenshot as base64. does not log the screenshot if log is False (true by default)"""
        screenshot_base64 = Utilities._take_screenshot_as_base64()
        if log:
            Utilities._embed_image_to_log(screenshot_base64, width=width)
        return screenshot_base64

    @keyword("Encode Image To Base64")
    def encode_image_to_base64(self, file_path: str, log_image: bool = False, width: int = 200):
        """ returns the image as base64. does not log the image if log is False (false by default)"""
        base64_data = Utilities.encode_image_to_base64(file_path)
        if log_image:
            Utilities._embed_image_to_log(base64_data, width=width)
        return base64_data
    
    @keyword("Create System Prompt")
    def create_system_prompt(self,system_prompt: str) -> dict:
        """
        Create a system prompt.
        args:
            system_prompt: the prompt to send to the LLM
        """
        return self.prompt.create_system_prompt(system_prompt)
    
    @keyword("Create User Prompt")
    def create_user_prompt(self,text: str, image_url: str = None) -> dict:
        """ 
        Create a user prompt with a text and an image url.
        args:
            text: the text of the prompt
            image_url: the url of the image to send to the LLM
        """
        return self.prompt.create_user_prompt(text, image_url)
    
    @keyword("Create User Prompt With Current Screenshot")
    def create_user_prompt_sending_current_screenshot(self,text: str, log_image: bool = False, width: int = 200) -> dict:
        return self.prompt.create_user_prompt_sending_current_screenshot(text, log_image, width)
    
    @keyword("Create User Prompt With Current UI XML")
    def create_user_prompt_sending_current_UI_XML(self,text: str) -> dict:
        return self.prompt.create_user_prompt_sending_current_UI_XML(text)
    
    @keyword("Create User Prompt With Reference Screenshot")
    def create_user_prompt_sending_reference_screenshot(self,text: str, image_path: str, log_image: bool = False, width: int = 200) -> dict:
        return self.prompt.create_user_prompt_sending_reference_screenshot(text, image_path, log_image, width)    

    @keyword("Click On UI Element")
    def click_on_ui_element(self, element_description: str):
        built_in = BuiltIn()
        driver = built_in.get_library_instance("AppiumLibrary")._current_application()
        from src.AiHelper.common._utils import Utilities
        screenshot = Utilities._capture_screenshot_and_reduce_size(filename="omniparser_screenshot.png")
        # screenshot_bytes = base64.b64decode(screenshot)
    
        elements = self.omniparser.parse_screenshot(screenshot)
        self.logger.info("elements parsed by omniparser are: " + str(elements), True)
        user_prompt = self.prompt.create_system_prompt("""
            You are a software test automation expert in locating element coordinates.
            You are given a screenshot of the current screen of the app.
            and a list of elements with their coordinates detected by the OmniParser.
            You need to return the element coordinates that matches the element description.
            You need to return the element bbox list corresponding to that element in json format and you need to explain why you choosed this element bbox
            like this : {"bbox": [0.10640496015548706, 0.872053861618042, 0.14359503984451294, 0.8884680271148682], "explanation": "your explanation why you choosed this element"}
        """)
        user_prompt3= self.prompt.create_user_prompt_sending_current_screenshot(f"elements parsed by omniparser are: {elements}", True)
        user_prompt2= self.prompt.create_user_prompt(f"element description : ${element_description}")
        messages = [user_prompt, user_prompt2, user_prompt3]
        response = self.send_ai_request(messages)
        bbox = Utilities.extract_json_safely(response)
        self.logger.info("bbox is : " + str(bbox['bbox']), True)
        self.logger.info("explanation is : " + bbox['explanation'], True)
        bbox: list[float] = bbox['bbox']
        coordinates = BBoxToClickCoordinates().get_real_coordinates(driver, bbox)
        driver.tap([(coordinates['x'], coordinates['y'])])
        return coordinates


    @keyword("Send AI Request")
    def send_ai_request(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 1.0, 
        **kwargs,
    ) -> Dict[str, Any]:
        """ 
        les kwargs sont les arguments de la fonction create_chat_completion
        max_tokens est remplacé par max_completion_tokens pour les modèles gpt-5.0
        max_tokens est optionnel
        la documentation de openai explique tous sur les params 
        """

        self.logger.info(self.logger._icons['separator'])
        test_name = BuiltIn().get_variable_value("${TEST_NAME}")
        self.logger.info(self.logger._icons['brain'] + " Sarting New AI Verification"+
                             "\n"+ self.logger._icons['start'] + "Test Case name: " + test_name )
        self.logger.info(f"Used arguments:\n"
                            f"Used Model: {model}\n"
                            f"Temperature: {temperature}\n"
                            f"Le reste des arguments {kwargs.keys()}: {kwargs}\n"
                            f"prompt: {messages}")

        if not self._client:
            self._init_client()
            
        response = self._client.create_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs
        )
        
        formatted = self._client.format_response(response, include_tokens=True, include_reason=True)


        prompt_tokens = formatted['prompt_tokens']
        completion_tokens = formatted['completion_tokens']
        total_tokens = formatted['total_tokens']


        cost = self._token.calculate_cost(prompt_tokens, completion_tokens, model)

        self.logger.info(f"prompt tokens: {prompt_tokens} ; completion tokens: {completion_tokens} ; total tokens: {total_tokens}", True)
        self.logger.info(f"Finish reason: {formatted['finish_reason']}",False)
        self.logger.info(f"prompt cost: {cost['input_cost']} ; completion cost: {cost['output_cost']} ; total cost: {cost['total_cost']}", True)
        
        
        self._last_response = formatted
        return formatted["content"]
















    #########################################################
    # usage directe + prompt inclues + fail/pass mechanism
    #########################################################
    @keyword("Ask AI For Verification")
    def ask_llm_to_verify_screenshot(self,verification_prompt:str, send_ui_xml:bool = False, reference_screenshot:str = None, confidence_threshold:float = 0.8, loading_time:float = 3):
        """
        This keyword sends a verification request to the LLM.
        args:
            verification_prompt: the prompt to send to the LLM.
            send_ui_xml: whether to send the current UI XML to the LLM. False by default.
            reference_screenshot: the path to the reference screenshot to send to the LLM. None by default.
            confidence_threshold: the confidence threshold to use for the verification. 0.8 by default.
            loading_time: time to wait before taking the screenshot and verifying the prompt. 1 second by default.
        Example:
        | Ask AI For Verification | I want to verify the login screen | | ${CURDIR}/reference_screenshots/login_screen.png |
        
        Reply expected:
        | {"confidence": 0.95, "reason": "The login screen is correct", "bug_summary": "", "bug_description": ""} |
        | {"confidence": 0.5, "reason": "The login screen is incorrect", "bug_summary": "Login Screen Incorrect", "bug_description": "The login screen is incorrect because the logo is not visible."} |
        
        """
        if loading_time > 0:
            time.sleep(loading_time)

        system_prompt = self.create_system_prompt("""
                You are a software tester experienced in UI verification of mobile apps.
                You have extensive expertise in passenger information and 
                route planning features of transportation applications
                You will are given a screenshot of the current screen of the app (as well as potential element like UI XML and reference screenshot) and the desired verification prompt.
                You will need to verify if the current screen matches the desired verification prompt.
                You will need to return a JSON object with the following keys:
                If the current screen doesn't match the desired verification prompt, you will need to report the bug 
                """)

        user_prompt_screenshot = self.create_user_prompt_sending_current_screenshot(verification_prompt, True)
        self.logger.info(f"from keywords class: user prompt current screen : {user_prompt_screenshot}", robot_log=False)

        user_prompt_response_requirements = self.create_user_prompt("""
           You should respond in JSON format with the following keys:
           - "confidence": must be a number between 0 and 1 indicating the confidence in your reply for the verification prompt
           - "reason": a short explanation for this confidence level
           - "bug_summary": return a short summary of the bug, empty string if no bug is found
           - "bug_description": return a detailed description of the bug, empty string if no bug is found
        """)
        
        messages = [system_prompt, user_prompt_screenshot, user_prompt_response_requirements]

        if send_ui_xml:
            user_prompt_ui_xml = self.create_user_prompt_sending_current_UI_XML("This is the current UI XML of the current screen got by appium")
            self.logger.info(f"from keywords class: user prompt current UI XML : {user_prompt_ui_xml}", robot_log=False)
            messages.append(user_prompt_ui_xml)

        if reference_screenshot:

            user_prompt_reference_screenshot = self.create_user_prompt_sending_reference_screenshot("""
                    This is a reference screenshot showing the expected UI and how the app without bugs should look like.
                    """, reference_screenshot, True)
            self.logger.info(f"from keywords class: user prompt reference screenshot: {user_prompt_reference_screenshot}", robot_log=False)
            messages.append(user_prompt_reference_screenshot)



        self.logger.info(f"Messages: {messages}")
        response = self.send_ai_request(messages)
        self.logger.info(f"Response: {response}")
        response_json = Utilities.extract_json_safely(response)
        self.logger.info(f"""\n Verification prompt was : {verification_prompt} ;
                             \nConfidence: {response_json['confidence']} ;
                             \nReason: {response_json['reason']} ;
                             \nBug Summary: {response_json['bug_summary']} ;
                             \nBug Description: {response_json['bug_description']}""")
        
        built_in = BuiltIn()
        if response_json["confidence"] < confidence_threshold:
            self.logger.info(f"Response JSON: {response_json}", robot_log=False)

            built_in.fail(f"""Verification prompt was : {verification_prompt}
                            \nVerification failed with confidence: {response_json['confidence']}
                            \nBug Summary: {response_json['bug_summary']}
                            \nBug Description: {response_json['bug_description']}""")
        else:
            built_in.set_test_message(f"""Verification prompt was : {verification_prompt}
                                        \nVerification passed with confidence: {response_json['confidence']}
                                        \nActual behavior is matching the expected behavior: {response_json['reason']}""")

            self.logger.info(f"Response JSON: {response_json}", robot_log=True)
            pass

    @keyword("Click On Element Using LLM")
    def click_on_element_using_llm(self,element_description:str, sleep_time: int=3):


        #system prompt
        system_prompt = self.create_system_prompt("""
                You are a software test automation experienced in construction robust locators 
                You are giving UI XML and screenshot of the current screen of the app
                If you don't find the element and you are confident of it , tha means it is a bug

                You should respond in JSON format with the following keys:

        - "locator": the locator to click on (should be always an xpath //*[@attribute="attribute_value"]). should return empty string if no locator is found
        - "reason": a short explanation on how and why this locator was chosen
        - "bug_summary": return a short summary of the bug, empty string if no bug is found
        - "bug_description": return a detailed description of the bug, empty string if no bug is found
        """)

        #user prompt : current screenshot
        user_prompt_screenshot = self.create_user_prompt_sending_current_screenshot(element_description, True)
        self.logger.info(f"from keywords class: user prompt current screen : {user_prompt_screenshot}", robot_log=False)

        

        #user prompt : ui xml 
        user_prompt_ui_xml = self.create_user_prompt_sending_current_UI_XML("This is the current UI XML of the current screen got by appium")
        self.logger.info(f"from keywords class: user prompt current UI XML : {user_prompt_ui_xml}", robot_log=False)


        

        #messages
        messages = [system_prompt, user_prompt_screenshot, user_prompt_ui_xml]

        response = self.send_ai_request(messages)
        self.logger.info(f"Response: {response}")

        response_json = Utilities.extract_json_safely(response)
        self.logger.info(f"""\n element description was : {element_description} ;
                             \nLocator: {response_json['locator']} ;
                             \nReason: {response_json['reason']} ;
                             \nBug Summary: {response_json['bug_summary']} ;
                             \nBug Description: {response_json['bug_description']}""")
        

        built_in = BuiltIn()
        if response_json["locator"] == "":
            self.logger.info(f"Response JSON: {response_json}", robot_log=False)

            built_in.fail(f"""element description was : {element_description}
                            \nBug Summary: {response_json['bug_summary']}
                            \nBug Description: {response_json['bug_description']}""")
        else:
            built_in.set_test_message(f"""element description was : {element_description}
                                        \nLocator: {response_json['locator']} ;
                                        \nReason: {response_json['reason']} ;""")

            self.logger.info(f"Response JSON: {response_json}", robot_log=True)
            locator = response_json['locator']
            driver = built_in.get_library_instance('AppiumLibrary')._current_application()
            driver.find_element(AppiumBy.XPATH, locator).click()
            if sleep_time > 0:
                time.sleep(sleep_time)
            return locator


    @keyword("Input Text Using AI")
    def input_text_using_llm(self,element_description:str, text:str):

        #system prompt
        system_prompt = self.create_system_prompt("""
                You are a software test automation experienced in construction robust locators 
                You are giving UI XML and screenshot of the current screen of the app
                If you don't find the element and you are confident of it , tha means it is a bug
            
            You should respond in JSON format with the following keys:

        - "locator": the locator to click on (should be always an xpath). should return empty string if no locator is found
        - "reason": a short explanation on how and why this locator was chosen
        - "bug_summary": return a short summary of the bug, empty string if no bug is found
        - "bug_description": return a detailed description of the bug, empty string if no bug is found""")

        #user prompt : current screenshot
        user_prompt_screenshot = self.create_user_prompt_sending_current_screenshot(element_description)
        self.logger.info(f"from keywords class: user prompt current screen : {user_prompt_screenshot}", robot_log=False)

        #user prompt : current UI XML
        user_prompt_ui_xml = self.create_user_prompt_sending_current_UI_XML("This is the current UI XML of the current screen got by appium")
        self.logger.info(f"from keywords class: user prompt current UI XML : {user_prompt_ui_xml}", robot_log=False)

        #user prompt : text to input
        user_prompt_text = self.create_user_prompt(f"The element that I look for is : ${element_description}")
        self.logger.info(f"from keywords class: user prompt text to input : {user_prompt_text}", robot_log=False)

        messages = [system_prompt, user_prompt_screenshot, user_prompt_ui_xml, user_prompt_text]

        response = self.send_ai_request(messages)
        self.logger.info(f"Response: {response}")

        response_json = Utilities.extract_json_safely(response)
        self.logger.info(f"""\n element description was : {element_description} ;
                             \nLocator: {response_json['locator']} ;
                             \nReason: {response_json['reason']} ;
                             \nBug Summary: {response_json['bug_summary']} ;
                             \nBug Description: {response_json['bug_description']}""")
        

        built_in = BuiltIn()
        if response_json["locator"] == "":
            self.logger.info(f"Response JSON: {response_json}", robot_log=False)

            built_in.fail(f"""element description was : {element_description}
                            \nBug Summary: {response_json['bug_summary']}
                            \nBug Description: {response_json['bug_description']}""")
        else:
            built_in.set_test_message(f"""element description was : {element_description}
                                        \nLocator: {response_json['locator']} ;
                                        \nReason: {response_json['reason']} ;""")

            self.logger.info(f"Response JSON: {response_json}", robot_log=True)
            locator = response_json['locator']
            driver = built_in.get_library_instance('AppiumLibrary')._current_application()
            driver.find_element(AppiumBy.XPATH, locator).send_keys(text)
            return locator


    #draft code for current step
    # def generate_code_for_current_step(self, step_description: str, send_ui_xml: bool = False, confidence_threshold: float = 0.8):
    #     """
    #     This keyword generates code for the current step using the LLM.
    #     """
    #     system_prompt = self.create_system_prompt("""
    #         You are a software test automation expert in coding using robot framework and AppiumLibrary.
    #         You are given a step description and the current UI XML of the current screen got by appium.
    #         You need to generate the suitable code written in .robot files ( e.g.  click element , input text , etc.)
    #         You need to return the code in a valid robot framework format without any additional text or comments
    #         Your code will be added directly as current step in runtime and will be executed without modification 
    #         Example of code:
    #         _launch application
    #         click text     J'accepte 
    #         click element     //*[@name="loginButton"]
    #         input text     //*[@name="username"]    ${username}
    #         input text     //*[@name="password"]    ${password}
    #         click button    //*[@name="loginButton"]
                                                  
    #         *** you step code will be added here ***
    #         *** your second step code will be added here ***
                                                  
    #     """)

    #     user_prompt_screenshot = self.create_user_prompt_sending_current_screenshot(step_description, True)
    #     self.logger.info(f"from keywords class: user prompt current screen : {user_prompt_screenshot}", robot_log=False)