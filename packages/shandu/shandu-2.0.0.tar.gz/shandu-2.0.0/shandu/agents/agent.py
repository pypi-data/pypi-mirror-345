"""Agent module for Shandu research system."""
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.tools import Tool, DuckDuckGoSearchResults, DuckDuckGoSearchRun

from ..search.search import UnifiedSearcher, SearchResult
from ..research.researcher import ResearchResult
from ..scraper import WebScraper, ScrapedContent
from ..prompts import SYSTEM_PROMPTS, USER_PROMPTS
from .utils.citation_manager import CitationManager, SourceInfo, Learning

class ResearchAgent:
    """LangChain-based research agent with enhanced citation tracking."""
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        searcher: Optional[UnifiedSearcher] = None,
        scraper: Optional[WebScraper] = None,
        temperature: float = 0,
        max_depth: int = 2,
        breadth: int = 4,
        max_urls_per_query: int = 3,
        proxy: Optional[str] = None
    ):
        self.llm = llm or ChatOpenAI(
            temperature=temperature,
            model="gpt-4"
        )
        self.searcher = searcher or UnifiedSearcher()
        self.scraper = scraper or WebScraper(proxy=proxy)
        self.citation_manager = CitationManager()  # Initialize citation manager
        # Research parameters
        self.max_depth = max_depth
        self.breadth = breadth
        self.max_urls_per_query = max_urls_per_query

        self.system_prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPTS["research_agent"])
        self.reflection_prompt = ChatPromptTemplate.from_template(USER_PROMPTS["reflection"])
        self.query_gen_prompt = ChatPromptTemplate.from_template(USER_PROMPTS["query_generation"])

        self.tools = self._setup_tools()

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def _setup_tools(self) -> List[Tool]:
        """Setup agent tools."""
        return [
            Tool(
                name="search",
                func=self.searcher.search_sync,
                description="Search multiple sources for information about a topic"
            ),
            DuckDuckGoSearchResults(
                name="ddg_results",
                description="Get detailed search results from DuckDuckGo"
            ),
            DuckDuckGoSearchRun(
                name="ddg_search",
                description="Search DuckDuckGo for a quick answer"
            ),
            Tool(
                name="reflect",
                func=self._reflect_on_findings,
                description="Analyze and reflect on current research findings"
            ),
            Tool(
                name="generate_queries",
                func=self._generate_subqueries,
                description="Generate targeted subqueries for deeper research"
            )
        ]

    async def _reflect_on_findings(self, findings: str) -> str:
        """Analyze research findings."""
        reflection_chain = self.reflection_prompt | self.llm | StrOutputParser()
        return await reflection_chain.ainvoke({"findings": findings})

    async def _generate_subqueries(
        self,
        query: str,
        findings: str,
        questions: str
    ) -> List[str]:
        """Generate subqueries for deeper research."""
        query_chain = self.query_gen_prompt | self.llm | StrOutputParser()
        result = await query_chain.ainvoke({
            "query": query,
            "findings": findings,
            "questions": questions,
            "breadth": self.breadth
        })

        queries = [q.strip() for q in result.split("\n") if q.strip()]
        return queries[:self.breadth]

    async def _extract_urls_from_results(
        self,
        search_results: List[SearchResult],
        max_urls: int = 3
    ) -> List[str]:
        """Extract top URLs from search results."""
        urls = []
        seen = set()
        
        for result in search_results:
            if len(urls) >= max_urls:
                break
                
            url = result.url
            if url and url not in seen and url.startswith('http'):
                urls.append(url)
                seen.add(url)
        
        return urls

    async def _analyze_content(
        self,
        query: str,
        content: List[ScrapedContent]
    ) -> Dict[str, Any]:
        """Analyze scraped content and track learnings with citation manager."""
        # Prepare content for analysis
        content_text = ""
        for item in content:

            source_info = SourceInfo(
                url=item.url,
                title=item.title,
                content_type=item.content_type,
                access_time=time.time(),
                domain=item.url.split("//")[1].split("/")[0] if "//" in item.url else "unknown",
                reliability_score=0.8,  # Default score, could be more dynamic
                metadata=item.metadata
            )
            self.citation_manager.add_source(source_info)

            content_text += f"\nSource: {item.url}\nTitle: {item.title}\n"
            content_text += f"Content Summary:\n{item.text[:2000]}...\n"
        
        # Use the content analysis prompt from centralized prompts
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPTS["content_analysis"]),
            ("user", USER_PROMPTS["content_analysis"])
        ])
        
        analysis_chain = analysis_prompt | self.llm | StrOutputParser()
        analysis = await analysis_chain.ainvoke({"query": query, "content": content_text})

        for item in content:
            # Use citation manager to extract and register learnings
            learning_hashes = self.citation_manager.extract_learning_from_text(
                analysis,  # Use the analysis as the source of learnings
                item.url,
                context=f"Analysis for query: {query}"
            )
            
        return {
            "analysis": analysis,
            "sources": [c.url for c in content],
            "learnings": len(self.citation_manager.learnings)  # Track number of learnings
        }

    async def research(
        self,
        query: str,
        depth: Optional[int] = None,
        engines: List[str] = ["google", "duckduckgo"]
    ) -> ResearchResult:
        """Execute the research process with enhanced citation tracking."""
        depth = depth if depth is not None else self.max_depth

        context = {
            "query": query,
            "depth": depth,
            "breadth": self.breadth,
            "findings": "",
            "sources": [],
            "subqueries": [],
            "content_analysis": [],
            "learnings_by_source": {}  # Track learnings by source
        }
        
        # Initial system prompt to set up the research
        system_chain = self.system_prompt | self.llm | StrOutputParser()
        context["findings"] = await system_chain.ainvoke(context)
        
        # Iterative deepening research process
        for current_depth in range(depth):
            # Reflect on current findings
            reflection = await self._reflect_on_findings(context["findings"])
            
            new_queries = await self._generate_subqueries(
                query=query,
                findings=context["findings"],
                questions=reflection
            )
            context["subqueries"].extend(new_queries)
            
            for subquery in new_queries:
                agent_result = await self.agent.arun(
                    f"Research this specific aspect: {subquery}\n\n"
                    f"Current findings: {context['findings']}\n\n"
                    "Think step by step about what tools to use and how to verify the information."
                )
                
                # Perform the search
                search_results = await self.searcher.search(
                    subquery,
                    engines=engines
                )

                urls_to_scrape = await self._extract_urls_from_results(
                    search_results,
                    self.max_urls_per_query
                )
                
                # Scrape and analyze content
                if urls_to_scrape:
                    scraped_content = await self.scraper.scrape_urls(
                        urls_to_scrape,
                        dynamic=True,
                        force_refresh=False  # Use cache when available
                    )
                    
                    if scraped_content:
                        # Analyze the content
                        analysis = await self._analyze_content(subquery, scraped_content)
                        context["content_analysis"].append({
                            "subquery": subquery,
                            "analysis": analysis["analysis"],
                            "sources": analysis["sources"],
                            "learnings": analysis.get("learnings", 0)
                        })

                for r in search_results:
                    if isinstance(r, SearchResult):
                        context["sources"].append(r.to_dict())
                    elif isinstance(r, dict):
                        context["sources"].append(r)
                    else:
                        print(f"Warning: Skipping non-serializable search result: {type(r)}")
                
                context["findings"] += f"\n\nFindings for '{subquery}':\n{agent_result}"

                if context["content_analysis"]:
                    latest_analysis = context["content_analysis"][-1]
                    context["findings"] += f"\n\nDetailed Analysis:\n{latest_analysis['analysis']}"
        
        # Final reflection and summary
        final_reflection = await self._reflect_on_findings(context["findings"])
        
        # Prepare detailed sources with content analysis
        detailed_sources = []
        for source in context["sources"]:
            # Source is already a dictionary at this point
            source_dict = source.copy()  # Make a copy to avoid modifying the original

            for analysis in context["content_analysis"]:
                if source.get("url", "") in analysis["sources"]:
                    source_dict["detailed_analysis"] = analysis["analysis"]

            if source.get("url") in self.citation_manager.source_to_learnings:
                source_url = source.get("url")
                learning_ids = self.citation_manager.source_to_learnings.get(source_url, [])
                source_dict["tracked_learnings"] = len(learning_ids)
                context["learnings_by_source"][source_url] = len(learning_ids)
                
            detailed_sources.append(source_dict)

        citation_stats = {
            "total_sources": len(self.citation_manager.sources),
            "total_learnings": len(self.citation_manager.learnings),
            "source_reliability": self.citation_manager._calculate_source_reliability()
        }
        
        return ResearchResult(
            query=query,
            summary=final_reflection,
            sources=detailed_sources,
            subqueries=context["subqueries"],
            depth=depth,
            content_analysis=context["content_analysis"],
            citation_stats=citation_stats
        )

    def research_sync(
        self,
        query: str,
        depth: Optional[int] = None,
        engines: List[str] = ["google", "duckduckgo"]
    ) -> ResearchResult:
        """Synchronous research wrapper."""
        return asyncio.run(self.research(query, depth, engines))
