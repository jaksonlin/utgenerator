from typing import List
from .prompt_manager import PromptManager
from .testcase_type import TestCaseType

class Java8Prompt(PromptManager):
    """
    This prompt will use JUnit 4 with Mockito 4.8 to generate test cases against Java 8 code.
    """
    
    def __init__(self, language: str):
        super().__init__(language)
        self.init_prompt_settings()
    
    def init_prompt_settings(self):
        self.prompt_settings = {
            TestCaseType.basic: """Generate basic functionality unit tests for the following Java code:

    {code}

    Focus on testing the main logic and expected outcomes. Use Mockito 4.8 to mock any calls to methods from other classes. Include the necessary import statements. Follow these guidelines:
    1. Use Java 8 syntax and features.
    2. Use JUnit 4 annotations (@Test, @Before, etc.).
    3. For any method calls to other classes outside the current class, use Mockito 4.8 to mock the behavior.
    4. Include @Mock and @InjectMocks annotations where appropriate.
    5. Use Mockito's when().thenReturn() syntax for defining mock behavior.
    6. Verify mock interactions using Mockito's verify() method where relevant.
    """,

            TestCaseType.edge_cases: """Generate edge case unit tests for the following Java code:

    {code}

    Consider boundary conditions, unusual inputs, and potential corner cases. Use Mockito 4.8 to mock any calls to methods from other classes. Include the necessary import statements. Follow these guidelines:
    1. Use Java 8 syntax and features.
    2. Use JUnit 4 annotations (@Test, @Before, etc.).
    3. For any method calls to other classes outside the current class, use Mockito 4.8 to mock the behavior.
    4. Include @Mock and @InjectMocks annotations where appropriate.
    5. Use Mockito's when().thenReturn() syntax for defining mock behavior.
    6. Verify mock interactions using Mockito's verify() method where relevant.
    7. Consider edge cases such as null inputs, empty collections, maximum/minimum values, and unusual combinations of parameters.
    """,

            TestCaseType.null_empty: """Generate unit tests for null and empty inputs for the following Java code:

    {code}

    Ensure all methods handle null and empty inputs correctly. Use Mockito 4.8 to mock any calls to methods from other classes. Include the necessary import statements. Follow these guidelines:
    1. Use Java 8 syntax and features.
    2. Use JUnit 4 annotations (@Test, @Before, etc.).
    3. For any method calls to other classes outside the current class, use Mockito 4.8 to mock the behavior.
    4. Include @Mock and @InjectMocks annotations where appropriate.
    5. Use Mockito's when().thenReturn() syntax for defining mock behavior.
    6. Verify mock interactions using Mockito's verify() method where relevant.
    7. Test scenarios with null inputs for all parameters that accept objects.
    8. Test scenarios with empty strings, collections, and maps where applicable.
    9. Use assertThrows to test for expected exceptions when null or empty inputs are not allowed.
    """
        }
