import ast
import re
import sys
from cneura_ai.llm import LLMInterface
from stdlib_list import stdlib_list # type: ignore
from cneura_ai.logger import logger


class CodeGenerator:
    def __init__(self, llm: LLMInterface, max_iterations=10):
        self.llm = llm
        self.max_iterations = max_iterations
        self.RULES_SCHEMA = {
        "logic_rules": {"description":"List of core logic and processing steps that the program must follow."},
        "usecase_rules": {"description":"List of different usage scenarios in which the program will be used."},
        "input_rules": {"description":"List of valid and invalid input formats, including expected data types and constraints."},
        "output_rules": {"description":"List of expected output formats, structure, and required details."},
        "error_handling_rules": {"description":"List of rules on how the program should handle errors and exceptions gracefully."},
        "data_validation_rules": {"description":"List of validation rules to ensure input data integrity and correctness."}
    }
        self.INSTRUCT_SCHEMA = {
        "errors": [
            {
                "reasons": {"description":"list of explanations of why the errors occurred"},
                "solution": {"description":"The list of solutions to fix the errors"},
                "instructions": {"description":"A list of Step-by-step guides to apply the solutions"}
            }
        ]
    }
        self.EXEC_RESULT_SCHEMA = {
            "error": {"description":"The result is a error: True. The result is success: False"},
            "total_testcases": {"description":"the total testcase that executed"},
            "pass_testcases": {"description":"the passed testcases count"},
            "fail_testcases": {"description":"the failed testcase count"}
        }
        self.SECRET_SCHEMA = {
            "has": {"description":"the code need external variables like api keys, secrets. output - True / False"},
            "variables": {"description":"a list of required variables like api keys, secrets, credntials with description."}
        }


    def parse_code(self, code: str, language: str = "python") -> str:
        pattern = fr"```{language}\n?(.*?)(?:\n```|$)"
        matches = re.findall(pattern, code, re.DOTALL)
        return matches[0].strip() if matches else code
    
    def plan(self, query: str) -> dict:
        system_prompt = (
            "system", 
            "You are an expert software architect.\nYour task is to analyze the user query and define a structured rule set that the program must follow when implementing the requested functionality."
        )

        prompt = (
            f"User Query: {query}\n",
            "Define a structured set of rules for implementing this request in a Python program.\nEnsure the rules cover logic, use cases, input/output expectations, error handling, and data validation.\nDo not include implementation details or code, only provide well-defined rules."
        )

        response = self.llm.query([system_prompt, prompt], self.RULES_SCHEMA)
        return response

    def synthesize(self, rules: dict) -> str:
        system_prompt = (
            "system", 
            """You are an experienced software developer.
            You write concise and efficient Python code following the given set of rules.
            Ensure the implementation strictly adheres to the provided logic, input/output formats, error handling, and validation constraints.
            If you need to get config variables like api keys, credentials. 
            get them like this: 
            ```python
            from config import Config

            Config.VARIABLE_NAME
            ```"""
        )

        prompt = (
            "Based on the following structured rules, generate a Python function that implements the required logic:\n\n"
            f"- Logic Rules: {rules.get('logic_rules', 'No rules specified.')}\n"
            f"- Use Case Rules: {rules.get('usecase_rules', 'No rules specified.')}\n"
            f"- Input Rules: {rules.get('input_rules', 'No rules specified.')}\n"
            f"- Output Rules: {rules.get('output_rules', 'No rules specified.')}\n"
            f"- Error Handling Rules: {rules.get('error_handling_rules', 'No rules specified.')}\n"
            f"- Data Validation Rules: {rules.get('data_validation_rules', 'No rules specified.')}\n\n"
            "Write the complete Python function based strictly on these rules.\n"
            "Do not include example usages or multiple scenarios.\n"
            "Only provide the function definition without explanations or extra formatting."
            "Don't include dummy functions and classes. You must implement every logic for the program."
            "Implement the program as a python class. In that class must have a method that can call the program like function."
        )

        response = self.llm.query([system_prompt, prompt])
        
        return self.parse_code(response)
    
    def identify_secrets(self, code: str, testcases: str)-> str:
        prompt = f"""Your job is indentify the external variables like api keys, secrets, credentials, configurations. 
                    Analyze this code and testcases, after identify what are they. Remember in the code they are in like this, Config.variable. in the output, don't include variable name as Config.variable, give varibale.
                    ## code
                    {code}
                    
                    ## testcases
                    {testcases}
                    """
        response = self.llm.query(prompt, self.SECRET_SCHEMA)
        print(response)
        return response 

    def instruct(self,code_with_test:str, errors: str) -> str:
        prompt = f"""
        I am solving a coding contest problem and need help debugging my solution.

        ### Current Code with testcases:  
        {code_with_test}

        ### Issue:  
        {errors}  

        Provide clear and concise **debugging instructions** to fix the code. 
        - Only focus on the program code, not the testcases. 
        - Identify the root cause of the issue.  
        - Suggest specific changes to correct logic errors, handle edge cases, and meet problem constraints.  
        - **Do not** rewrite or provide any code—only describe the necessary fixes.  
        - If error is came from the code. don't answer that. pass it. Only focus on code errors. 
        """
        response = self.llm.query(prompt, self.INSTRUCT_SCHEMA)
        return response if response else "Fix the errors in the program."

    def debug(self, code: str, instructions: str) -> str:
        prompt = f"""You are a software developer who fixes bugs in the given python code. Solve the following code contest problem.
        Currently, the code is
        ```
        {code}
        ```
        instructionsModify the code as {instructions}.
        You must only return correct code.
        Remove any triple quotes, language name or explanations.
        Don't include any testcases. You need to implement every logics in the source code. 
        Don't loss the code in the source code. 
        Don't include dummy function and classes."""
        response = self.llm.query(prompt)
        return self.parse_code(response)

    def generate_test_script(self, code: str) -> str:
        prompt = f"""Code: {code}
        Generate test cases to verify correctness. Return only the test code. Add doc string for each method for describing what is it testing for.
        And also, import the code as a module to testcases code and don't include the given code into this. 
        If you need to get config variables like api keys, credentials. import Config class from config and access them as attributes.
       
        Give the testcases in following format:
        ```python
        import unittest
        from config import Config # get Config class that contains api key, credentials etc.
        # import other required libraries
        from script import code # **the class of the give codebase.**

        ### **Don't include the given code **

        class TestCaseClassName(unittest.TestCase):
            def setUp(self):
                # initialize the instance of main program class of the given code.

            # ... testcases
            # ... testcases

        if __name__ == '__main__':
            unittest.main()
        ```
        Give the testcases in the above format. Don't give any explaintion or other text."""
        response = self.llm.query(prompt)
        return self.parse_code(response) if response else "No valid test code returned from LLM."

    def extract_imports(self, code):
        tree = ast.parse(code)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        return list(imports)

    def identify_third_party(self, imports):
        third_party = []
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        std_libs = set(stdlib_list(python_version))
        
        for lib in imports:
            if lib in std_libs or lib in sys.builtin_module_names or lib == "config":
                continue  # Skip built-in and standard library modules
            third_party.append(lib)

        return third_party

    def extract_dependencies(self, code):
        imports = self.extract_imports(code)
        third_party_libs = self.identify_third_party(imports)
        return third_party_libs if isinstance(third_party_libs, list) else [third_party_libs]

    def execution_result_processor(self, result: str):
        system_prompt = (
            "system", 
            """Your job is the extract information from the code execution result. 
                * error - The result is a error: True. The result is success: False
                * total_testcases - the total testcase that executed
                * fail_testcases - the failed testcase count
            """
        )

        prompt = (
            f"user",
            f"Code execution result: {result}"
        )

        response = self.llm.query([system_prompt, prompt], self.EXEC_RESULT_SCHEMA)
        return response

    

