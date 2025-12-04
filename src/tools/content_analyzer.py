# src/tools/content_analyzer.py
from typing import List, Dict, Any
import asyncio
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from src.models.research_plan import ResearchPlan

class ContentAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model_name=settings.research_model,
            temperature=0.1
        )
    
    async def analyze_and_synthesize(self, 
                                   search_results: List[Dict], 
                                   research_plan: ResearchPlan) -> Dict[str, Any]:
        """Analyze search results and synthesize findings"""
        
        # Extract relevant content
        relevant_content = await self._extract_relevant_content(search_results, research_plan)
        
        # Synthesize information by subtopic
        synthesis_tasks = []
        for subtopic in research_plan.subtopics:
            task = self._synthesize_subtopic(subtopic, relevant_content)
            synthesis_tasks.append(task)
        
        subtopic_syntheses = await asyncio.gather(*synthesis_tasks)
        
        # Create executive summary
        executive_summary = await self._create_executive_summary(subtopic_syntheses)
        
        return {
            "executive_summary": executive_summary,
            "subtopic_syntheses": subtopic_syntheses,
            "key_findings": await self._extract_key_findings(subtopic_syntheses),
            "sources": self._compile_sources(search_results)
        }
    
    async def _extract_relevant_content(self, search_results: List[Dict], 
                                      research_plan: ResearchPlan) -> List[Dict]:
        """Extract content relevant to the research plan"""
        
        relevant_content = []
        
        for result in search_results:
            if 'content' not in result:
                continue
                
            # Use LLM to assess relevance
            relevance_prompt = f"""
            Assess relevance of this content to the research topic: {research_plan.topic}
            
            Content snippet: {result['content'][:1000]}...
            
            Is this content highly relevant, somewhat relevant, or not relevant?
            Provide a relevance score (1-10) and brief explanation.
            """
            
            response = await self.llm.agenerate([[HumanMessage(content=relevance_prompt)]])
            relevance_assessment = response.generations[0][0].text
            
            # Simple relevance scoring (in practice, parse the response properly)
            if "highly relevant" in relevance_assessment.lower() or "8" in relevance_assessment:
                relevant_content.append({
                    'source': result['title'],
                    'url': result['url'],
                    'content': result['content'],
                    'relevance_score': 8  # Simplified
                })
        
        return relevant_content