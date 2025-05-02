"""
Initialize node for research graph.
"""
import os
import time
from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from ..processors.content_processor import AgentState
from ..utils.agent_utils import log_chain_of_thought, _call_progress_callback
from ...config import get_current_date
from ...prompts import SYSTEM_PROMPTS, USER_PROMPTS

console = Console()

class ResearchPlan(BaseModel):
    """Structured output for research plan."""
    objectives: list[str] = Field(
        description="Clear objectives for the research",
        min_items=1
    )
    key_areas: list[str] = Field(
        description="Key areas to investigate",
        min_items=1
    )
    methodology: str = Field(
        description="Approach to conducting the research"
    )
    expected_outcomes: list[str] = Field(
        description="Expected outcomes of the research",
        min_items=1
    )

async def initialize_node(llm, date, progress_callback, state: AgentState) -> AgentState:
    """Initialize the research process with a research plan using structured output."""
    console.print(Panel(f"[bold blue]Starting Research:[/] {state['query']}", title="Research Process", border_style="blue"))
    state["start_time"] = time.time()
    state["status"] = "Initializing research"
    state["current_date"] = date or get_current_date()
    
    try:
        # Use a completely direct approach to avoid template issues
        direct_prompt = f"""You are an expert research agent tasked with creating a comprehensive research plan. Current date: {state['current_date']}

Please create a detailed research plan for this query: {state['query']}

Your plan must include the following sections clearly labeled:

## Objectives
- List 3-5 clear objectives for the research

## Key Areas to Investigate
- List 4-6 specific areas or aspects that need to be researched

## Methodology
- Describe the approach to conducting this research
- Include information sources and analysis methods

## Expected Outcomes
- List 3-5 expected results or deliverables from this research

Format your response with clear section headings and bullet points for clarity. Be specific and detailed in your planning.
"""
        # Send the direct prompt to the model
        response = await llm.ainvoke(direct_prompt)

        research_text = response.content

        import re
        objectives = []
        key_areas = []
        methodology = ""
        expected_outcomes = []

        objectives_section = re.search(r'(?:objectives|goals|aims)(?:\s*:|\s*\n)([^#]*?)(?:#|$)', research_text.lower(), re.IGNORECASE | re.DOTALL)
        if objectives_section:
            objectives_text = objectives_section.group(1).strip()
            objectives = [line.strip().strip('-*').strip() for line in objectives_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        areas_section = re.search(r'(?:key areas|areas to investigate|investigation areas)(?:\s*:|\s*\n)([^#]*?)(?:#|$)', research_text.lower(), re.IGNORECASE | re.DOTALL)
        if areas_section:
            areas_text = areas_section.group(1).strip()
            key_areas = [line.strip().strip('-*').strip() for line in areas_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        methodology_section = re.search(r'(?:methodology|approach|method)(?:\s*:|\s*\n)([^#]*?)(?:#|$)', research_text.lower(), re.IGNORECASE | re.DOTALL)
        if methodology_section:
            methodology = methodology_section.group(1).strip()
        
        outcomes_section = re.search(r'(?:expected outcomes|outcomes|results|expected results)(?:\s*:|\s*\n)([^#]*?)(?:#|$)', research_text.lower(), re.IGNORECASE | re.DOTALL)
        if outcomes_section:
            outcomes_text = outcomes_section.group(1).strip()
            expected_outcomes = [line.strip().strip('-*').strip() for line in outcomes_text.split('\n') if line.strip() and not line.strip().startswith('#')]

        if not objectives:
            objectives = ["Understand the key aspects of " + state['query']]
        if not key_areas:
            key_areas = ["Primary concepts and definitions", "Current applications and examples", "Future trends and developments"]
        if not methodology:
            methodology = "Systematic review of available literature and analysis of current applications and examples."
        if not expected_outcomes:
            expected_outcomes = ["Comprehensive understanding of " + state['query'], "Identification of key challenges and opportunities"]

        formatted_plan = "# Research Plan\n\n"
        
        formatted_plan += "## Objectives\n\n"
        for objective in objectives:
            formatted_plan += f"- {objective}\n"
        
        formatted_plan += "\n## Key Areas to Investigate\n\n"
        for area in key_areas:
            formatted_plan += f"- {area}\n"
        
        formatted_plan += f"\n## Methodology\n\n{methodology}\n"
        
        formatted_plan += "\n## Expected Outcomes\n\n"
        for outcome in expected_outcomes:
            formatted_plan += f"- {outcome}\n"
        
        state["messages"].append(HumanMessage(content=f"Planning research on: {state['query']}"))
        state["messages"].append(AIMessage(content=formatted_plan))
        state["findings"] = f"{formatted_plan}\n\n# Initial Findings\n\n"
        
    except Exception as e:
        from ...utils.logger import log_error
        log_error("Error in structured plan generation", e, 
                 context=f"Query: {state['query']}, Function: initialize_node")
        console.print(f"[dim red]Error in structured plan generation: {str(e)}. Using simpler approach.[/dim red]")
        try:
            # Even simpler fallback approach
            response = await llm.ainvoke(f"""Create a research plan for: {state['query']}

Include:
1. Main objectives
2. Key areas to investigate
3. Approach/methodology
4. Expected outcomes

Keep it concise and practical.
""")
            
            cleaned_plan = response.content.replace("**", "").replace("# ", "").replace("## ", "")
            
            state["messages"].append(HumanMessage(content=f"Planning research on: {state['query']}"))
            state["messages"].append(AIMessage(content=cleaned_plan))
            state["findings"] = f"# Research Plan\n\n{cleaned_plan}\n\n# Initial Findings\n\n"
        except Exception as e2:
            console.print(f"[dim red]Error in fallback plan generation: {str(e2)}. Using minimal plan.[/dim red]")
            
            minimal_plan = f"Research plan for: {state['query']}\n\n- Investigate key aspects\n- Analyze relevant sources\n- Synthesize findings"
            
            state["messages"].append(HumanMessage(content=f"Planning research on: {state['query']}"))
            state["messages"].append(AIMessage(content=minimal_plan))
            state["findings"] = f"# Research Plan\n\n{minimal_plan}\n\n# Initial Findings\n\n"
    
    log_chain_of_thought(state, f"Created research plan for query: {state['query']}")
    if progress_callback:
        await _call_progress_callback(progress_callback, state)
    return state
