from typing import Optional

from ...application.services.test_service import TestService
from ...domain.models.test_case import TestCaseBase, TestCase
from ...utils.string import build_query_params, is_valid_id
from ...infrastructure.clients.http_client import Client

class TestCaseService:
    def __init__(self, client: Client, test_service: TestService):
        self._client = client
        self.test_service = test_service
        
    def create(self, test_id: str, input: str, expected_output: Optional[str] = None, context: Optional[str] = None, tag: Optional[str] = None):
        """
        Create a new test case.
        
        Args:
            test_id (str): ID of the test.
            input (str): Input for the test case.
            expected_output (str , optional): Expected output for the test case.
            name (str, optional): Name of the test case.
            context (str, optional): Context for the test case.
            tag (str, optional): Tag for the test case.
            
        Returns:
            TestCase: The created test case object.
        """
        test_case= TestCaseBase(
            test_id=test_id,
            input=input,
            expected_output=expected_output,
            context=context,
            tag=tag
        )
        test_case.model_validate(test_case.model_dump())
        response = self._client.post("testCases", json=test_case.model_dump(by_alias=True))
        test_case_response = TestCase(**response.json())
        return test_case_response
    
    def list(self, test_id: str, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        Retrieve test cases for a given test ID.
        
        Args:
            test_id (str): ID of the test.
            
        Returns:
            list[TestCase]: List of test case objects.
        """
        if not is_valid_id(test_id):
            raise ValueError("Test ID provided is not valid.")

        query_params = build_query_params(testIds=[test_id], offset=offset, limit=limit)
        response = self._client.get(f"testCases?{query_params}")
        test_cases = [TestCase(**test_case) for test_case in response.json()]
        
        if not test_cases:
            try:
                self.test_service.get(test_id)
            except:
                raise ValueError(f"Test with ID {test_id} does not exist.")

        return test_cases
    
    def get(self, test_case_id: str):
        """
        Retrieve a test case by its ID.
        
        Args:
            test_case_id (str): ID of the test case.
            
        Returns:
            TestCase: The retrieved test case object.
        """
        if not is_valid_id(test_case_id):
            raise ValueError("Test case ID provided is not valid.")
        
        response = self._client.get(f"testCases/{test_case_id}")
        test_case_response = TestCase(**response.json())
        return test_case_response
    
    def delete(self, test_case_id: str):
        """
        Delete a test case by its ID.
        
        Args:
            test_case_id (str): ID of the test case to be deleted.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not is_valid_id(test_case_id):
            raise ValueError("Test case ID provided is not valid.")
        
        response = self._client.delete(f"testCases/{test_case_id}")
        return response.status_code == 204