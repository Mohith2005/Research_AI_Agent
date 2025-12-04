import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI
import json
import time
import os
import re

class ResearchAgent:
    def __init__(self):
        self.sources = []
        self.research_data = {
            'key_points': [],
            'recent_developments': [],
            'challenges': [],
            'future_outlook': [],
            'sources': []
        }
        self.setup_openai()
    
    def setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.client_available = True
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"❌ OpenAI setup failed: {e}")
                self.client_available = False
        else:
            self.client_available = False
            print("⚠️  OpenAI API key not found. Using basic analysis.")
    
    def research_topic(self, topic, num_sources=3):
        """Enhanced research with OpenAI analysis"""
        try:
            print(f"🌐 Searching for sources about: {topic}")
            sources = self._search_web(topic, num_sources)
            
            if not sources:
                print("❌ No reliable sources found. Using demonstration data.")
                return self._get_mock_research_data(topic)
            
            print(f"📚 Found {len(sources)} sources. Extracting content...")
            all_content = []
            for i, url in enumerate(sources, 1):
                print(f"   📖 Reading source {i}/{len(sources)}: {self._shorten_url(url)}")
                content = self._extract_content(url)
                if content:
                    all_content.append({
                        'content': content,
                        'source': url
                    })
                time.sleep(1)  # Be polite to servers
            
            if not all_content:
                print("❌ Could not extract content from sources. Using demonstration data.")
                return self._get_mock_research_data(topic)
            
            # Analyze all content with OpenAI
            if self.client_available and all_content:
                print("🤖 Analyzing content with AI...")
                self.research_data = self._analyze_with_openai(all_content, topic)
            else:
                print("🔍 Analyzing content with basic analysis...")
                for item in all_content:
                    self._keyword_analysis(item['content'], item['source'])
            
            print("✅ Research completed successfully!")
            return self.research_data
            
        except Exception as e:
            print(f"❌ Research error: {e}")
            return self._get_mock_research_data(topic)
    
    def _analyze_with_openai(self, content_list, topic):
        """Use OpenAI to analyze and synthesize research"""
        try:
            # Prepare content for analysis
            combined_content = "\n\n".join([
                f"Source: {item['source']}\nContent: {item['content'][:800]}"
                for item in content_list
            ])
            
            prompt = f"""
            Analyze the following research content about {topic} and extract structured information.
            
            RESEARCH CONTENT:
            {combined_content}
            
            Please provide a JSON response with the following structure:
            {{
                "key_points": ["list 3-5 key findings"],
                "recent_developments": ["list 2-3 recent advancements"], 
                "challenges": ["list 2-3 main challenges"],
                "future_outlook": ["list 2-3 future predictions"],
                "sources": {[item['source'] for item in content_list]}
            }}
            
            Be concise and factual. Focus on the most important information.
            Return only valid JSON, no additional text.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a research analyst that extracts structured information from technical content. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the JSON response
            analysis = response.choices[0].message.content.strip()
            
            # Clean the response
            if analysis.startswith('```json'):
                analysis = analysis[7:]
            if analysis.endswith('```'):
                analysis = analysis[:-3]
            analysis = analysis.strip()
            
            return json.loads(analysis)
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse AI response as JSON: {e}")
            return self._fallback_analysis(content_list)
        except Exception as e:
            print(f"   ❌ OpenAI analysis failed: {e}")
            return self._fallback_analysis(content_list)
    
    def _search_web(self, topic, num_sources):
        """Search for relevant sources using DuckDuckGo"""
        try:
            print("   🔎 Searching DuckDuckGo...")
            ddgs = DDGS()
            search_query = f"{topic} technology research 2024"
            sources = []

            results = ddgs.text(
                keywords=search_query, 
                max_results=num_sources + 2,
                region='wt-wt'
            )
            
            for result in results:
                url = result['href']
                if self._is_reliable_source(url):
                    sources.append(url)
                    print(f"   ✅ Reliable source found: {self._shorten_url(url)}")
                    if len(sources) >= num_sources:
                        break
            
            return sources if sources else self._get_mock_sources(topic)
            
        except Exception as e:
            print(f"   ❌ Search error: {e}")
            return self._get_mock_sources(topic)
    
    def _shorten_url(self, url):
        """Shorten URL for display"""
        return url[:50] + "..." if len(url) > 50 else url
    
    def _is_reliable_source(self, url):
        """Check if source is from reliable domains"""
        reliable_domains = [
            'wikipedia.org', 'arxiv.org', 'nature.com', 'science.org',
            'technologyreview.com', 'ieee.org', 'acm.org', 'nist.gov',
            'mit.edu', 'stanford.edu', 'researchgate.net', 'springer.com',
            'sciencedirect.com', 'towardsdatascience.com', 'techcrunch.com',
            'medium.com', 'github.com', 'stackoverflow.com'
        ]
        return any(domain in url.lower() for domain in reliable_domains)
    
    def _extract_content(self, url):
        """Extract content from webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted tags
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try to get main content from common content containers
            content_selectors = [
                'main', 'article', 
                '[role="main"]', '.content', '.main', '.article',
                '.post-content', '.entry-content', '.story-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                text = main_content.get_text()
            else:
                # Fallback to body
                text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text[:2500].strip() if text else None
            
        except Exception as e:
            print(f"   ❌ Error extracting content from {url}: {e}")
            return None
    
    def _fallback_analysis(self, content_list):
        """Fallback analysis when AI fails"""
        research_data = {
            'key_points': [], 'recent_developments': [], 
            'challenges': [], 'future_outlook': [], 'sources': []
        }
        for item in content_list:
            self._keyword_analysis(item['content'], item['source'], research_data)
        
        # Ensure we have some data
        if not research_data['key_points']:
            research_data['key_points'] = ["Key findings extracted from research content"]
        if not research_data['challenges']:
            research_data['challenges'] = ["Various technical challenges identified"]
        if not research_data['future_outlook']:
            research_data['future_outlook'] = ["Promising future developments expected"]
        
        research_data['sources'] = [item['source'] for item in content_list]
        return research_data
    
    def _keyword_analysis(self, content, source_url, research_data=None):
        """Fallback keyword analysis"""
        if research_data is None:
            research_data = self.research_data
            
        content_lower = content.lower()
        sentences = content.split('.')

        key_point_keywords = ['breakthrough', 'advance', 'discovery', 'innovation', 'developed', 'created', 'achieved', 'successful']
        challenge_keywords = ['challenge', 'limitation', 'problem', 'issue', 'difficult', 'hard', 'bottleneck', 'constraint']
        future_keywords = ['future', 'outlook', 'prediction', 'trend', 'will', 'expected', 'potential', 'prospect']
        
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 30 and len(clean_sentence) < 300:
                sentence_lower = clean_sentence.lower()
                
                if any(keyword in sentence_lower for keyword in key_point_keywords):
                    research_data['key_points'].append(clean_sentence[:250])
                
                if any(keyword in sentence_lower for keyword in challenge_keywords):
                    research_data['challenges'].append(clean_sentence[:250])
                
                if any(keyword in sentence_lower for keyword in future_keywords):
                    research_data['future_outlook'].append(clean_sentence[:250])
        
        # Use recent_developments as a copy of key_points for basic analysis
        research_data['recent_developments'] = research_data['key_points'][:2] if research_data['key_points'] else ["Recent developments in the field"]
        
        if source_url not in research_data['sources']:
            research_data['sources'].append(source_url)
        
        # Limit to reasonable numbers
        for key in ['key_points', 'challenges', 'future_outlook']:
            research_data[key] = list(set(research_data[key]))[:4]  # Remove duplicates, max 4
    
    def _get_mock_sources(self, topic):
        """Get mock sources for demonstration"""
        return [
            f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "https://arxiv.org/list/cs/recent",
            "https://www.technologyreview.com/"
        ]
    
    def _get_mock_research_data(self, topic):
        """Provide realistic mock data when APIs fail"""
        return {
            'key_points': [
                f"Recent advances in {topic} show promising results for practical applications",
                f"Major tech companies are investing heavily in {topic} research and development",
                f"New algorithms and approaches in {topic} are solving previously intractable problems"
            ],
            'recent_developments': [
                f"Breakthrough in {topic} stability and performance achieved in recent studies",
                f"New government and private funding initiatives for {topic} research announced"
            ],
            'challenges': [
                f"Scalability remains a major challenge for widespread {topic} adoption",
                f"Technical limitations and resource requirements in {topic} need further research"
            ],
            'future_outlook': [
                f"Industry experts predict {topic} will become commercially viable within 5-10 years",
                f"{topic} is expected to revolutionize multiple industries including healthcare, finance, and logistics"
            ],
            'sources': [
                "https://en.wikipedia.org/wiki/Demonstration",
                "https://example.com/technical-research",
                "https://example.com/industry-analysis"
            ]
        }