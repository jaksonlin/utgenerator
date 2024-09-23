from .testcase_type import TestCaseType

prompt_without_mock ={
        TestCaseType.basic: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Focus on testing the main logic and expected outcomes. 
    """,

        TestCaseType.edge_cases: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Consider boundary conditions, unusual inputs, and potential corner cases. Follow these guidelines:
    1. Consider edge cases such as maximum/minimum values, and unusual combinations of parameters.
    2. Consider math operation like division, large number caculation where possible.
    """,

        TestCaseType.null_empty: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Ensure all methods handle null and empty inputs correctly. 
    1. Consider edge cases such as null inputs, empty collections
    2. Test scenarios with null inputs for all parameters that accept objects.
    3. Test scenarios with empty strings, collections, and maps where applicable.
    """
    }

prompt_with_mock ={
        TestCaseType.basic: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Focus on testing the main logic and expected outcomes. Use {mock_engine} to mock any calls to methods from other dependencies. Include the necessary import statements. Follow these guidelines:
    1. For any method calls to other dependencies outside the current code, use {mock_engine} to mock the behavior.
    2. Include {mock_engine} setup where appropriate.
    3. Verify mock interactions using where relevant.
    """,

        TestCaseType.edge_cases: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Consider boundary conditions, unusual inputs, and potential corner cases. Use {mock_engine} to mock any calls to methods from other dependencies. Include the necessary import statements. Follow these guidelines:
    1. For any method calls to other dependencies outside the current code, use {mock_engine} to mock the behavior.
    2. Include {mock_engine} setup where appropriate.
    3. Verify mock interactions using where relevant.
    4. Consider edge cases such as null inputs, empty collections, maximum/minimum values, and unusual combinations of parameters.
    """,

        TestCaseType.null_empty: """Generate basic functionality unit tests for the following {language} code:

    {code}

    Ensure all methods handle null and empty inputs correctly. Use {mock_engine} to mock any calls to methods from other dependencies. Include the necessary import statements. Follow these guidelines:
    1. For any method calls to other dependencies outside the current code, use {mock_engine} to mock the behavior.
    2. Include {mock_engine} setup where appropriate.
    3. Verify mock interactions using where relevant.
    4. Consider edge cases such as null inputs, empty collections, maximum/minimum values, and unusual combinations of parameters.
    5. Test scenarios with null inputs for all parameters that accept objects.
    6. Test scenarios with empty strings, collections, and maps where applicable.
    """
    }