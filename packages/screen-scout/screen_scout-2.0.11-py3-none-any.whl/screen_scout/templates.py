"""
This module contains all the templates used for test creation and execution.
"""

create_test_template_comprehensive = '''
You are an expert QA engineer specializing in UI testing. Your task is to create a detailed test suite for the following website:

TARGET WEBSITE: {{.webURL}}
NUMBER OF TESTS: {{.ntype}}

TEST STRUCTURE REQUIREMENTS:
Each test case must be a well-formed JSON object with the following fields:
1. "testName": A concise, descriptive name for the test
2. "testType": The category of test (e.g., "Functional", "Accessibility", "UI/UX", "Cross-browser")
3. "description": A clear explanation of what the test verifies
4. "steps": An ordered array of specific, actionable steps
5. "expectedResult": The expected outcome after test execution
6. "url": The target webpage URL

OUTPUT FORMAT:
Return a single JSON object with a "testCase" array containing the test cases:
{
  "testCase": [
    {
      "testName": "Example Test Name",
      "testType": "Functional",
      "description": "Clear description of test purpose",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Expected outcome description",
      "url": "{{.webURL}}"
    }
  ]
}

IMPORTANT GUIDELINES:
1. Each test should focus on a single functionality or component
2. Steps should be specific and actionable
3. Avoid tests requiring authentication
4. Tests should be self-contained and independent
5. Include both positive and negative test cases
6. Consider edge cases and error scenarios
7. Ensure steps are in logical order
8. Make descriptions clear and unambiguous
9. Include a mix of different test types

PROCESS:
1. First, navigate to {{.webURL}}
2. Analyze the page structure and available elements
3. Create up to {{.ntype}} unique test cases
4. Ensure each test case follows the exact format specified
5. Verify all required fields are present
6. Return only the JSON object, no additional text

DO NOT:
- Include markdown formatting
- Use Google or external resources
- Create tests requiring login credentials
- Mix multiple functionalities in a single test
- Skip any required fields in the output
- Add explanatory text outside the JSON structure

Begin by navigating to {{.webURL}} and creating the test cases according to these specifications.'''

create_custom_test_template = '''
You are an expert QA engineer specializing in UI testing. Your task is to create UI tests based on the following parameters:

TARGET WEBSITE: {{.webURL}}
NUMBER OF TESTS: {{.ntype}}
USER REQUIREMENT: {{user_requirement}}

TEST STRUCTURE REQUIREMENTS:
Each test case must be a well-formed JSON object with the following fields:
1. "testName": A concise, descriptive name for the test
2. "testType": The category of test (e.g., "Functional", "Accessibility", "UI/UX", "Cross-browser")
3. "description": A clear explanation of what the test verifies
4. "steps": An ordered array of specific, actionable steps
5. "expectedResult": The expected outcome after test execution
6. "url": The target webpage URL

OUTPUT FORMAT:
Return a single JSON object with a "testCase" array containing the test cases:
{
  "testCase": [
    {
      "testName": "Example Test Name",
      "testType": "Functional",
      "description": "Clear description of test purpose",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Expected outcome description",
      "url": "{{.webURL}}"
    }
  ]
}

IMPORTANT GUIDELINES:
1. Each test should focus on a single functionality or component
2. Steps should be specific and actionable
3. Avoid tests requiring authentication
4. Tests should be self-contained and independent
5. Include both positive and negative test cases
6. Consider edge cases and error scenarios
7. Ensure steps are in logical order
8. Make descriptions clear and unambiguous

PROCESS:
1. First, navigate to {{.webURL}}
2. Analyze the page structure and available elements
3. Create up to {{.ntype}} unique test cases
4. Ensure each test case follows the exact format specified
5. Verify all required fields are present
6. Return only the JSON object, no additional text

DO NOT:
- Include markdown formatting
- Use Google or external resources
- Create tests requiring login credentials
- Mix multiple functionalities in a single test
- Skip any required fields in the output
- Add explanatory text outside the JSON structure

Begin by navigating to {{.webURL}} and creating the test cases according to these specifications.''' 

execute_test_template = '''You are an expert UI testing engineer.
Your task is to navigate to {url} and execute the following UI test:

TEST DETAILS:
Test Name: {testName}
Test Type: {testType}
Description: {description}
Expected Result: {expectedResult}

TEST STEPS:
{steps}

After performing the test, please provide a *well-formed JSON array* containing at least:
- "testName": The name of the test
- "description": A short explanation of what the test covers
- "steps": An ordered list of the steps you took
- "result": The outcome (e.g., "Passed", "Failed", "Blocked")
- "notes": Any additional context or observations

**For the final answer, return only the JSON object by converting the json string (no extra text) in the format**:
{
  "testName": "...",
  "description": "...",
  "steps": ["...", "..."],
  "result": "...",
  "notes": "..."
}

IMPORTANT GUIDELINES:
1. Follow the test steps exactly as specified
2. Record all actions taken
3. Note any issues or unexpected behavior
4. Be specific in your observations
5. Include any relevant error messages

PROCESS:
1. Navigate to {url}
2. Execute each step in the test
3. Record your observations
4. Determine the test result
5. Return the JSON response

DO NOT:
- Skip any steps
- Add an unnecessary number of steps not in the original test
- Include markdown formatting
- Add explanatory text outside the JSON structure
- Use external resources

Begin by navigating to {url} and executing the test according to these specifications.'''
