"""
Robot Framework Test Library for AgentPromptComposer and AgentKeywordCatalog

This library provides keywords to test the prompt composition functionality
for DO and CHECK flows in the agent system.
"""

from typing import List, Dict, Optional, Any
from robot.api.deco import keyword, library
from src.AiHelper.agent._promptcomposer import AgentPromptComposer, AgentKeywordCatalog


@library(scope='SUITE', auto_keywords=True)
class PromptComposerTestLibrary:
    """Test library for AgentPromptComposer and AgentKeywordCatalog.
    
    This library provides reusable keywords for testing prompt composition
    and keyword catalog functionality.
    
    == Usage ==
    
    | Library | tests.utest.PromptComposerTestLibrary |
    
    == Examples ==
    
    | ${messages}= | Compose DO Messages | instruction=Click login button |
    | ${keywords}= | Get DO Keywords |
    | ${strategies}= | Get Locator Strategies |
    """
    
    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self, locale: str = "fr"):
        """Initialize the test library.
        
        Args:
            locale: Language locale for prompts (default: fr)
        """
        self.locale = locale
        self.composer = None
        self.catalog = None
        self._reset()
    
    def _reset(self):
        """Reset the composer and catalog instances."""
        self.composer = AgentPromptComposer(locale=self.locale)
        self.catalog = AgentKeywordCatalog()
    
    # ==================== Prompt Composer Keywords ====================
    
    @keyword("Compose DO Messages")
    def compose_do_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Compose DO (action) messages for the agent.
        
        Creates a list of messages containing system prompt and user prompt
        for the DO flow, which is used to determine which action to execute.
        
        Args:
            instruction: The action instruction (e.g., "Click login button")
            ui_elements: Optional list of UI element dictionaries
            image_url: Optional screenshot image URL
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
            
        Examples:
            | ${messages}= | Compose DO Messages | Click login button |
            | ${messages}= | Compose DO Messages | instruction=Type email | ui_elements=${elements} |
            | ${messages}= | Compose DO Messages | Tap icon | image_url=https://example.com/screen.png |
        """
        return self.composer.compose_do_messages(
            instruction=instruction,
            ui_elements=ui_elements,
            image_url=image_url
        )
    
    @keyword("Compose CHECK Messages")
    def compose_check_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Compose CHECK (visual verification) messages for the agent.
        
        Creates a list of messages containing system prompt and user prompt
        for the VISUAL CHECK flow, which uses AI vision to analyze screenshots.
        
        Args:
            instruction: The verification instruction (e.g., "Check error message is displayed")
            ui_elements: Optional list of UI element dictionaries (ignored for visual check)
            image_url: Optional screenshot image URL
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
            
        Examples:
            | ${messages}= | Compose CHECK Messages | Verify login button is visible |
            | ${messages}= | Compose CHECK Messages | instruction=Check text contains welcome | image_url=${screenshot_url} |
        """
        return self.composer.compose_visual_check_messages(
            instruction=instruction,
            image_url=image_url
        )
    
    @keyword("Compose DO Messages With Locale")
    def compose_do_messages_with_locale(
        self,
        instruction: str,
        locale: str = "fr"
    ) -> List[Dict[str, Any]]:
        """Compose DO messages with a specific locale.
        
        Temporarily sets the locale for message composition.
        
        Args:
            instruction: The action instruction
            locale: Language locale (e.g., 'fr', 'en')
            
        Returns:
            List of message dictionaries
            
        Examples:
            | ${messages}= | Compose DO Messages With Locale | Click button | en |
        """
        original_locale = self.composer.locale
        self.composer.locale = locale
        messages = self.composer.compose_do_messages(instruction=instruction)
        self.composer.locale = original_locale
        return messages
    
    @keyword("Render UI Elements")
    def render_ui_elements(
        self,
        ui_elements: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Render UI elements as text for prompt inclusion.
        
        Args:
            ui_elements: List of UI element dictionaries
            
        Returns:
            Rendered text representation of UI elements
            
        Examples:
            | ${text}= | Render UI Elements | ${elements} |
        """
        return self.composer._render_ui_candidates(ui_elements)
    
    @keyword("Get DO Output Schema")
    def get_do_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for DO output.
        
        Returns the expected JSON schema that the LLM should follow
        when generating DO action responses.
        
        Returns:
            Dictionary containing JSON schema definition
            
        Examples:
            | ${schema}= | Get DO Output Schema |
            | Should Be Equal | ${schema}[type] | object |
        """
        return self.composer._get_do_output_schema()
    
    @keyword("Get CHECK Output Schema")
    def get_check_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for CHECK output.
        
        Returns the expected JSON schema that the LLM should follow
        when generating CHECK assertion responses.
        
        Returns:
            Dictionary containing JSON schema definition
            
        Examples:
            | ${schema}= | Get CHECK Output Schema |
            | Should Be Equal | ${schema}[type] | object |
        """
        return self.composer._get_visual_check_output_schema()
    
    # ==================== Keyword Catalog Keywords ====================
    
    @keyword("Get DO Keywords")
    def get_do_keywords(self) -> List[Dict[str, Any]]:
        """Get the list of available DO (action) keywords.
        
        Returns the complete catalog of action keywords that can be
        used in DO flows, including their Robot Framework mappings.
        
        Returns:
            List of keyword dictionaries with action, rf_keyword, and other metadata
            
        Examples:
            | ${keywords}= | Get DO Keywords |
            | ${count}= | Get Length | ${keywords} |
            | Should Be True | ${count} > 0 |
        """
        return self.catalog._get_do_keywords()
    
    
    @keyword("Get Locator Strategies")
    def get_locator_strategies(self) -> List[str]:
        """Get the list of available locator strategies.
        
        Returns the locator strategies supported by the platform
        (e.g., xpath, id, accessibility_id, class_name).
        
        Returns:
            List of locator strategy strings
            
        Examples:
            | ${strategies}= | Get Locator Strategies |
            | List Should Contain Value | ${strategies} | xpath |
        """
        return self.catalog._get_locator_strategies()
    
    @keyword("Render Catalog Text For Action")
    def render_catalog_text_for_action(self, action_type: str = "do") -> str:
        """Render the keyword catalog as text.
        
        Generates a human-readable text representation of the keyword
        catalog for inclusion in prompts.
        
        Args:
            action_type: Either 'do' or 'check'
            
        Returns:
            Formatted text representation of the catalog
            
        Examples:
            | ${text}= | Render Catalog Text For Action | do |
            | Should Contain | ${text} | tap |
            | ${text}= | Render Catalog Text For Action | check |
            | Should Contain | ${text} | visible |
        """
        return self.catalog._render_catalog_text(for_action=action_type)
    
    # ==================== Helper Keywords ====================
    
    @keyword("Get Keyword By Action")
    def get_keyword_by_action(
        self,
        action_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific DO keyword by its action name.
        
        Args:
            action_name: The action name (e.g., 'tap', 'type', 'clear')
            
        Returns:
            Keyword dictionary if found, None otherwise
            
        Examples:
            | ${keyword}= | Get Keyword By Action | tap |
            | Should Be Equal | ${keyword}[rf_keyword] | Click Element |
        """
        keywords = self.catalog._get_do_keywords()
        for keyword in keywords:
            if keyword.get("action") == action_name:
                return keyword
        return None
    
    
    @keyword("Verify Message Has Role")
    def verify_message_has_role(
        self,
        message: Dict[str, Any],
        expected_role: str
    ) -> bool:
        """Verify a message has the expected role.
        
        Args:
            message: Message dictionary
            expected_role: Expected role ('system' or 'user')
            
        Returns:
            True if role matches, False otherwise
            
        Examples:
            | ${is_system}= | Verify Message Has Role | ${message} | system |
        """
        return message.get("role") == expected_role
    
    @keyword("Extract Message Content Text")
    def extract_message_content_text(
        self,
        message: Dict[str, Any]
    ) -> str:
        """Extract text content from a message.
        
        Handles both simple string content and complex content arrays.
        
        Args:
            message: Message dictionary with 'content' key
            
        Returns:
            Extracted text content
            
        Examples:
            | ${text}= | Extract Message Content Text | ${message} |
            | Should Contain | ${text} | instruction |
        """
        content = message.get("content", "")
        
        # If content is a string, return it directly
        if isinstance(content, str):
            return content
        
        # If content is a list (complex content with text and images)
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "\n".join(text_parts)
        
        return str(content)
    
    @keyword("Message Has Image URL")
    def message_has_image_url(
        self,
        message: Dict[str, Any]
    ) -> bool:
        """Check if a message contains an image URL.
        
        Args:
            message: Message dictionary
            
        Returns:
            True if message contains image, False otherwise
            
        Examples:
            | ${has_image}= | Message Has Image URL | ${message} |
            | Should Be True | ${has_image} |
        """
        content = message.get("content", "")
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image_url":
                    return True
        
        return False
    
    @keyword("Count DO Actions")
    def count_do_actions(self) -> int:
        """Count the number of DO actions available.
        
        Returns:
            Number of DO actions in the catalog
            
        Examples:
            | ${count}= | Count DO Actions |
            | Should Be True | ${count} > 3 |
        """
        return len(self.catalog._get_do_keywords())
    
    
    @keyword("Verify DO Action Exists")
    def verify_do_action_exists(self, action_name: str) -> bool:
        """Verify that a DO action exists in the catalog.
        
        Args:
            action_name: Name of the action to check
            
        Returns:
            True if action exists, False otherwise
            
        Examples:
            | ${exists}= | Verify DO Action Exists | tap |
            | Should Be True | ${exists} |
        """
        return self.get_keyword_by_action(action_name) is not None
    
    # ==================== AI Response Validation Keywords ====================
    
    @keyword("Validate DO Response Structure")
    def validate_do_response_structure(self, response: str) -> bool:
        """Validate that a DO response has the correct structure.
        
        Args:
            response: AI response JSON string
            
        Returns:
            True if structure is valid, False otherwise
            
        Examples:
            | ${valid}= | Validate DO Response Structure | ${ai_response} |
            | Should Be True | ${valid} |
        """
        try:
            import json
            response_data = json.loads(response)
            
            # Check required fields
            required_fields = ['action', 'locator']
            for field in required_fields:
                if field not in response_data:
                    return False
            
            # Validate action is from allowed list
            allowed_actions = ['tap', 'type', 'clear', 'swipe', 'scroll', 'wait']
            if response_data['action'] not in allowed_actions:
                return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    @keyword("Validate CHECK Response Structure")
    def validate_check_response_structure(self, response: str) -> bool:
        """Validate that a CHECK response has the correct structure for visual analysis.
        
        Args:
            response: AI response JSON string
            
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            import json
            response_data = json.loads(response)
            
            # Check required fields for visual check
            required_fields = ['verification_result', 'confidence_score', 'analysis']
            for field in required_fields:
                if field not in response_data:
                    return False
            
            # Validate verification_result is boolean
            if not isinstance(response_data['verification_result'], bool):
                return False
            
            # Validate confidence_score is between 0 and 1
            confidence = response_data['confidence_score']
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                return False
            
            # Validate analysis is not empty
            analysis = response_data['analysis']
            if not analysis or len(str(analysis).strip()) == 0:
                return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    @keyword("Validate Response Completeness")
    def validate_response_completeness(self, response: str, response_type: str = "do") -> bool:
        """Validate that a response is complete and contains all necessary information.
        
        Args:
            response: AI response JSON string
            response_type: Type of response ("do" or "check")
            
        Returns:
            True if response is complete, False otherwise
        """
        try:
            import json
            response_data = json.loads(response)
            
            if response_type.lower() == "do":
                return self._validate_do_completeness(response_data)
            elif response_type.lower() == "check":
                return self._validate_check_completeness(response_data)
            else:
                return False
                
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    def _validate_do_completeness(self, response_data: Dict) -> bool:
        """Validate DO response completeness."""
        required_fields = ['action', 'locator']
        
        # Check required fields
        for field in required_fields:
            if field not in response_data or not response_data[field]:
                return False
        
        return True
    
    def _validate_check_completeness(self, response_data: Dict) -> bool:
        """Validate CHECK response completeness."""
        required_fields = ['verification_result', 'confidence_score', 'analysis']
        
        # Check required fields
        for field in required_fields:
            if field not in response_data:
                return False
        
        # Check analysis is not empty
        analysis = response_data.get('analysis', '')
        if not analysis or len(analysis.strip()) < 5:
            return False
        
        return True

