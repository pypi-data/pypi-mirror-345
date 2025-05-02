from typing import List, Dict, Optional, Any, Union
import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from .search import UnifiedSearcher, SearchResult
from ..config import config
from ..scraper import WebScraper, ScrapedContent
from ..agents.utils.citation_manager import CitationManager, SourceInfo

@dataclass
class AISearchResult:
    """Container for AI-enhanced search results with enriched output and citation tracking."""
    query: str
    summary: str
    sources: List[Dict[str, Any]]
    citation_stats: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
    
    def to_markdown(self) -> str:
        """Convert to markdown format with improved readability."""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        md = [
            f"# {self.query}",
            "## Summary",
            self.summary,
            "## Sources"
        ]
        for i, source in enumerate(self.sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '')
            snippet = source.get('snippet', '')
            source_type = source.get('source', 'Unknown')
            md.append(f"### {i}. {title}")
            if url:
                md.append(f"- **URL:** [{url}]({url})")
            if source_type:
                md.append(f"- **Source:** {source_type}")
            if snippet:
                md.append(f"- **Snippet:** {snippet}")
            md.append("")

        if self.citation_stats:
            md.append("## Research Process")
            md.append(f"- **Sources Analyzed**: {self.citation_stats.get('total_sources', len(self.sources))}")
            md.append(f"- **Key Information Points**: {self.citation_stats.get('total_learnings', 0)}")
            if self.citation_stats.get('source_reliability'):
                md.append(f"- **Source Quality**: {len(self.citation_stats.get('source_reliability', {}))} domains assessed")
            md.append("")
            
        return "\n".join(md)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "query": self.query,
            "summary": self.summary,
            "sources": self.sources,
            "timestamp": self.timestamp.isoformat()
        }
        if self.citation_stats:
            result["citation_stats"] = self.citation_stats
        return result

class AISearcher:
    """
    AI-powered search functionality.
    Combines search results with AI analysis for any type of query.
    Enhanced with scraping capability, detailed outputs, source citations, and learning extraction.
    """
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        searcher: Optional[UnifiedSearcher] = None,
        scraper: Optional[WebScraper] = None,
        citation_manager: Optional[CitationManager] = None,
        max_results: int = 10,
        max_pages_to_scrape: int = 3
    ):
        api_base = config.get("api", "base_url")
        api_key = config.get("api", "api_key")
        model = config.get("api", "model")
        self.llm = llm or ChatOpenAI(
            base_url=api_base,
            api_key=api_key,
            model=model,
            temperature=0.4,
            max_tokens=8192
        )
        self.searcher = searcher or UnifiedSearcher(max_results=max_results)
        self.scraper = scraper or WebScraper()
        self.citation_manager = citation_manager or CitationManager()
        self.max_results = max_results
        self.max_pages_to_scrape = max_pages_to_scrape

        self.ddg_search = DuckDuckGoSearchRun()
        self.ddg_results = DuckDuckGoSearchResults(output_format="list")
    
    async def search(
        self, 
        query: str,
        engines: Optional[List[str]] = None,
        detailed: bool = False,
        enable_scraping: bool = True,
        use_ddg_tools: bool = True
    ) -> AISearchResult:
        """
        Perform AI-enhanced search with detailed outputs and source citations.
        
        Args:
            query: Search query (can be about any topic)
            engines: List of search engines to use
            detailed: Whether to generate a detailed analysis
            enable_scraping: Whether to scrape content from top results
            use_ddg_tools: Whether to use DuckDuckGo tools from langchain_community
        
        Returns:
            AISearchResult object with a comprehensive summary and cited sources
        """
        timestamp = datetime.now()
        sources = []
        
        # Use DuckDuckGo tools if enabled
        if use_ddg_tools and (not engines or 'duckduckgo' in engines):
            try:

                ddg_structured_results = self.ddg_results.invoke(query)
                for result in ddg_structured_results[:self.max_results]:
                    source_info = {
                        "title": result.get("title", "Untitled"),
                        "url": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "DuckDuckGo"
                    }
                    sources.append(source_info)
                    
                    # Register source with citation manager
                    self._register_source_with_citation_manager(source_info)
            except Exception as e:
                print(f"Error using DuckDuckGoSearchResults: {e}")
        
        # Use UnifiedSearcher as a fallback or if DuckDuckGo tools are disabled
        if not sources or not use_ddg_tools:
            search_results = await self.searcher.search(query, engines)
        
        # Collect all sources
            for result in search_results:
                if isinstance(result, SearchResult):
                    result_dict = result.to_dict()
                    sources.append(result_dict)
                    
                    # Register source with citation manager
                    self._register_source_with_citation_manager(result_dict)
                elif isinstance(result, dict):
                    sources.append(result)
                    
                    # Register source with citation manager
                    self._register_source_with_citation_manager(result)
        
        # Scrape additional content if enabled
        if enable_scraping:
            urls_to_scrape = []
            for source in sources:
                if source.get('url') and len(urls_to_scrape) < self.max_pages_to_scrape:
                    urls_to_scrape.append(source['url'])
            if urls_to_scrape:
                print(f"Scraping {len(urls_to_scrape)} pages for deeper insights...")
                scraped_results = await self.scraper.scrape_urls(urls_to_scrape, dynamic=True)
                for scraped in scraped_results:
                    if hasattr(scraped, 'is_successful') and scraped.is_successful():
                        try:
                            main_content = scraped.text
                            if hasattr(self.scraper, 'extract_main_content'):
                                main_content = await self.scraper.extract_main_content(scraped)
                            if "unexpected error" in main_content.lower():
                                continue
                            preview = main_content[:500] + ("...(truncated)" if len(main_content) > 1500 else "")
                            source_info = {
                                "title": scraped.title,
                                "url": scraped.url,
                                "snippet": preview,
                                "source": "Scraped Content"
                            }
                            sources.append(source_info)
                            
                            # Register source with citation manager and extract learnings
                            source_id = self._register_source_with_citation_manager(source_info)
                            if source_id and main_content:
                                self.citation_manager.extract_learning_from_text(
                                    main_content, 
                                    scraped.url,
                                    context=f"Search query: {query}"
                                )
                        except Exception as e:
                            print(f"Error processing scraped content from {scraped.url}: {e}")
        
        # Prepare sources with improved citation format
        aggregated_text = ""
        for i, source in enumerate(sources, 1):

            url = source.get('url', '')
            domain = url.split("//")[1].split("/")[0] if "//" in url else "Unknown Source"
            # Capitalize first letter of domain for a more professional look
            domain_name = domain.split('.')[0].capitalize() if '.' in domain else domain
            
            aggregated_text += (
                f"[{i}] {domain_name}\n"
                f"Title: {source.get('title', 'Untitled')}\n"
                f"URL: {url}\n"
                f"Snippet: {source.get('snippet', '')}\n\n"
            )
        
        current_date = timestamp.strftime('%Y-%m-%d')
        if detailed:
            detail_instruction = (
                "Provide a detailed analysis with in-depth explanations, "
                "specific examples, relevant background, and additional insights "
                "to enhance understanding of the topic."
            )
        else:
            detail_instruction = "Provide a concise yet informative summary, focusing on the key points and essential information."
        
        final_prompt = f"""You are Shandu, an expert analyst. Based on the following sources retrieved on {current_date} for the query "{query}", {detail_instruction}

- If the query is a question, answer it directly with a thorough explanation.
- If it's a topic, provide a well-rounded overview with supporting details.
- Use bullet points or numbered lists to organize information clearly.
- If there are conflicting views or uncertainties, discuss them explicitly.
- When providing information, cite the source by using the number in square brackets, like [1], to indicate where the information was sourced.
- ONLY use the citation numbers provided in the sources below.
- DO NOT include years or dates in your citations, just use the bracketed number like [1].
- Ensure the response is engaging, detailed, and written in plain text suitable for all readers.

Sources:

{aggregated_text}
"""
        
        final_output = await self.llm.ainvoke(final_prompt)

        citation_stats = None
        if sources:
            citation_stats = {
                "total_sources": len(self.citation_manager.sources),
                "total_learnings": len(self.citation_manager.learnings),
                "source_reliability": self.citation_manager._calculate_source_reliability()
            }
        
        return AISearchResult(
            query=query,
            summary=final_output.content.strip(),
            sources=sources,
            citation_stats=citation_stats,
            timestamp=timestamp
        )
    
    def _register_source_with_citation_manager(self, source: Dict[str, Any]) -> Optional[str]:
        """Register a source with the citation manager and return its ID."""
        try:
            url = source.get('url', '')
            if not url:
                return None
                
            title = source.get('title', 'Untitled')
            snippet = source.get('snippet', '')
            source_type = source.get('source', 'web')

            domain = url.split("//")[1].split("/")[0] if "//" in url else "unknown"

            source_info = SourceInfo(
                url=url,
                title=title,
                snippet=snippet,
                source_type=source_type,
                content_type="article",
                access_time=time.time(),
                domain=domain,
                reliability_score=0.8,  # Default score
                metadata=source
            )

            return self.citation_manager.add_source(source_info)
            
        except Exception as e:
            print(f"Error registering source with citation manager: {e}")
            return None
    
    def search_sync(
        self, 
        query: str,
        engines: Optional[List[str]] = None,
        detailed: bool = False,
        enable_scraping: bool = True,
        use_ddg_tools: bool = True
    ) -> AISearchResult:
        """Synchronous version of the search method."""
        return asyncio.run(self.search(query, engines, detailed, enable_scraping, use_ddg_tools))
