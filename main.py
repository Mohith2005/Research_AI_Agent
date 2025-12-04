# main.py
import asyncio
import argparse
from src.agents.research_coordinator import ResearchCoordinator
from src.generators.presentation_generator import PresentationGenerator
from src.config.settings import settings

class ResearchAgent:
    def __init__(self):
        self.research_coordinator = ResearchCoordinator(settings)
        self.presentation_generator = PresentationGenerator(settings)
    
    async def research_topic(self, topic: str) -> str:
        """Main method to research a topic and generate presentation"""
        
        print(f"Starting research on: {topic}")
        
        # Step 1: Research and synthesize
        research_data = await self.research_coordinator.execute_research(topic)
        
        print("Research completed. Generating presentation...")
        
        # Step 2: Generate presentation
        presentation_file = await self.presentation_generator.generate_presentation(research_data)
        
        print(f"Presentation generated: {presentation_file}")
        
        return presentation_file

async def main():
    parser = argparse.ArgumentParser(description='AI Research Agent')
    parser.add_argument('topic', type=str, help='Technical topic to research')
    parser.add_argument('--output', '-o', type=str, help='Output file name')
    
    args = parser.parse_args()
    
    agent = ResearchAgent()
    result_file = await agent.research_topic(args.topic)
    
    print(f"Research completed! Output file: {result_file}")

if __name__ == "__main__":
    asyncio.run(main())