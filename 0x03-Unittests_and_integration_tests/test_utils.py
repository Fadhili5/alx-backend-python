#!/usr/bin/env python3

import unittest
from parameterized import parameterized, parameterized_class
from typing import Mapping, Sequence, Any
from utils import access_nested_map , get_json, memoize
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestAccessNestedMap(unittest.TestCase):
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self,nested_map, path, expected):
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)
        
    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b"))
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
            
        self.assertIn(path[-1], str(context.exception))
        
class TestGetJson(unittest.TestCase):
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        mock_get.return_value.json.return_value = test_payload
        result = get_json(test_url)
        
        #checks requests.get was called with correct URL
        mock_get.assert_called_once_with(test_url)
        #checks we get expected result
        self.assertEqual(result, test_payload)
        
        
class TestMemoize(unittest.TestCase):
    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42
            
            @memoize
            def a_property(self):
                return self.a_method()
            
        test_instance = TestClass()
        
        with patch.object(test_instance, 'a_method', return_value=42) as mock_method:
            result1  = test_instance.a_property
            result2 = test_instance.a_property
            
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            mock_method.assert_called_once()
            
class TestGithubOrgClient(unittest.TestCase): 
    @parameterized.expand([
            ("google",),
            ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org calls get_json with correct URL"""
        test_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = test_payload
        
        client = GithubOrgClient(org_name)
        result = client.org
        
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        self.assertEqual(result, test_payload)
        
        
    def test_public_repos_url(self):
        """Test that GithubOrgClient._public_repos_url returns correct URL"""
        test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock, return_value=test_payload) as mock_org:
            client = GithubOrgClient("google")
            result = client._public_repos_url
            
            expected_url = "https://api.github.com/orgs/google/repos"
            self.assertEqual(result, expected_url)
            
            mock_org.assert_called_once()
            
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected list of repo names"""
        test_payload = [
            {"name": "twilio", "id": 1},
            {"name": "cluely", "id": 2}, 
            {"name": "mario", "id": 3}
        ]
        mock_get_json.return_value = test_payload
        
        mock_url ="https://api.github.com/orgs/google/repos"
        
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock, return_value=mock_url) as mock_repos_url:
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            expected_repos = ["twilio", "cluely", "mario"]
            self.assertEqual(result, expected_repos)
            
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_url)
            
            
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])       
    def test_has_license(self, repo, license_key, expected):
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)
        
@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1], 
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def get_json_side_effect(url):
            """Return mock response based on URL"""
            mock_response = Mock()
            
            if "orgs/" in url and "/repos" not in url:
                return cls.org_payload
                
            elif "/repos" in url:
                return cls.repos_payload
            else:
                return {}
                
            return mock_response    
                
        cls.get_patcher = patch('client.get_json', side_effect=get_json_side_effect)
        cls.get_patcher.start()
    
    
    @classmethod
    def tearDownClass(cls):
        """Stops the patcher"""
        cls.get_patcher.stop()
        
    def test_public_repos(self):
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)
        
    def test_public_repos_with_license(self):
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)

        
if __name__ == "__main__":
    unittest.main(verbosity=3)