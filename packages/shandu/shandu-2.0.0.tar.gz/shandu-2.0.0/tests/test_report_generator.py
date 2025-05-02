import unittest
from unittest.mock import AsyncMock, patch
import asyncio
from shandu.agents.processors.report_generator import format_citations
from shandu.agents.utils.citation_registry import CitationRegistry

class TestReportGenerator(unittest.TestCase):
    """Basic tests for report generation functions."""
    
    def setUp(self):
        """Set up test cases."""
        self.mock_llm = AsyncMock()
        self.mock_llm.ainvoke = AsyncMock()
        
        # Sample citation data
        self.sample_sources = [
            {"url": "https://example.com/article1", "title": "Test Article 1", "date": "2023-01-01"},
            {"url": "https://github.com/user/repo", "title": "Sample Repository", "date": "2024-02-15"}
        ]
        
        # Create a citation registry
        self.registry = CitationRegistry()
        self.registry.register_citation("https://example.com/article1")
        self.registry.register_citation("https://github.com/user/repo")
        
        # Add metadata to the citations
        self.registry.update_citation_metadata(1, {
            "title": "Test Article 1",
            "date": "2023-01-01"
        })
        self.registry.update_citation_metadata(2, {
            "title": "Sample Repository",
            "date": "2024-02-15"
        })
    
    def test_format_citations_sync(self):
        """Test format_citations function synchronously by running the async function."""
        # Set up the mock to return properly formatted citations
        self.mock_llm.ainvoke.return_value.content = """
        [1] *example.com*, "Test Article 1", https://example.com/article1
        [2] *github.com*, "Sample Repository", https://github.com/user/repo
        """
        
        # Run the async function in a synchronous context
        formatted_citations = asyncio.run(format_citations(
            self.mock_llm,
            ["https://example.com/article1", "https://github.com/user/repo"],
            self.sample_sources,
            self.registry
        ))
        
        # Check the results
        self.assertIn("*example.com*", formatted_citations)
        self.assertIn("\"Test Article 1\"", formatted_citations)
        self.assertIn("https://example.com/article1", formatted_citations)
        
        # Verify the correct format (no date in citations)
        self.assertNotIn("2023-01-01", formatted_citations)
        self.assertNotIn("2024-02-15", formatted_citations)
        
        # Ensure citation numbers are properly formatted
        self.assertIn("[1]", formatted_citations)
        self.assertIn("[2]", formatted_citations)

if __name__ == '__main__':
    unittest.main()
