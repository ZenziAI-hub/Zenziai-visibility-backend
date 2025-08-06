import openai
import requests
import json
import re
from typing import Dict, List, Any
import time
import random

class AIAnalyzer:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.platforms = ['chatgpt', 'claude', 'perplexity', 'arc_search', 'searchgpt']
        self.methodologies = ['cidr', 'scvs', 'acso', 'uifl']
        
        # Query templates for different analysis types
        self.query_templates = {
            'general': "What does {platform} know about {company}?",
            'services': "Summarize {company}'s services and reputation.",
            'sources': "List reliable sources for information about {company}.",
            'industry': "How is {company} related to {industry} industry?",
            'reputation': "What is {company}'s reputation in the market?",
            'products': "What are {company}'s main products or services?"
        }
    
    def analyze_company(self, company_name: str) -> Dict[str, Any]:
        """Main method to analyze a company across all platforms and methodologies"""
        print(f"Starting analysis for company: {company_name}")
        
        platform_scores = {}
        overall_insights = []
        
        for platform in self.platforms:
            print(f"Analyzing platform: {platform}")
            platform_scores[platform] = self._analyze_platform(company_name, platform)
            time.sleep(1)  # Rate limiting
        
        # Generate overall insights
        insights = self._generate_insights(company_name, platform_scores)
        
        return {
            'platform_scores': platform_scores,
            'insights': insights
        }
    
    def _analyze_platform(self, company_name: str, platform: str) -> Dict[str, Any]:
        """Analyze a company on a specific platform"""
        scores = {}
        
        for methodology in self.methodologies:
            score, comment = self._calculate_methodology_score(company_name, platform, methodology)
            scores[methodology] = {
                'score': score,
                'comment': comment
            }
        
        return scores
    
    def _calculate_methodology_score(self, company_name: str, platform: str, methodology: str) -> tuple:
        """Calculate score for a specific methodology on a platform"""
        
        if methodology == 'cidr':
            return self._calculate_cidr_score(company_name, platform)
        elif methodology == 'scvs':
            return self._calculate_scvs_score(company_name, platform)
        elif methodology == 'acso':
            return self._calculate_acso_score(company_name, platform)
        elif methodology == 'uifl':
            return self._calculate_uifl_score(company_name, platform)
        else:
            return 0, "Unknown methodology"
    
    def _calculate_cidr_score(self, company_name: str, platform: str) -> tuple:
        """Calculate Contextual Intent-Driven Ranking score"""
        try:
            # Generate diverse queries about the company
            queries = [
                f"What does {company_name} do?",
                f"Tell me about {company_name}'s services",
                f"What is {company_name} known for?",
                f"How does {company_name} compare to competitors?"
            ]
            
            total_score = 0
            responses = []
            
            for query in queries:
                if platform in ['chatgpt', 'searchgpt']:
                    response = self._query_openai(query, company_name)
                elif platform == 'claude':
                    response = self._query_claude(query, company_name)
                elif platform == 'perplexity':
                    response = self._query_perplexity(query, company_name)
                else:  # arc_search - simulated
                    response = self._simulate_arc_search(query, company_name)
                
                responses.append(response)
                
                # Analyze response quality
                relevance = self._analyze_relevance(response, company_name, query)
                completeness = self._analyze_completeness(response)
                accuracy = self._analyze_accuracy(response, company_name)
                context = self._analyze_context(response, company_name)
                
                query_score = (relevance + completeness + accuracy + context) / 4
                total_score += query_score
            
            final_score = min(100, max(0, total_score / len(queries)))
            comment = f"Intent understanding score based on {len(queries)} diverse queries. Average response quality: {final_score:.1f}/100"
            
            return final_score, comment
            
        except Exception as e:
            return 0, f"Error calculating CIDR score: {str(e)}"
    
    def _calculate_scvs_score(self, company_name: str, platform: str) -> tuple:
        """Calculate Source Credibility & Verifiability Score"""
        try:
            query = f"List reliable and credible sources for information about {company_name}"
            
            if platform in ['chatgpt', 'searchgpt']:
                response = self._query_openai(query, company_name)
            elif platform == 'claude':
                response = self._query_claude(query, company_name)
            elif platform == 'perplexity':
                response = self._query_perplexity(query, company_name)
            else:  # arc_search - simulated
                response = self._simulate_arc_search(query, company_name)
            
            # Extract and analyze sources
            sources = self._extract_sources(response)
            credibility_score = self._analyze_source_credibility(sources)
            verifiability_score = self._analyze_verifiability(sources, company_name)
            
            final_score = (credibility_score + verifiability_score) / 2
            comment = f"Found {len(sources)} sources. Credibility: {credibility_score:.1f}, Verifiability: {verifiability_score:.1f}"
            
            return final_score, comment
            
        except Exception as e:
            return 0, f"Error calculating SCVS score: {str(e)}"
    
    def _calculate_acso_score(self, company_name: str, platform: str) -> tuple:
        """Calculate Adaptive Content Structure Optimization score"""
        try:
            query = f"Analyze the structure and organization of {company_name}'s online content"
            
            if platform in ['chatgpt', 'searchgpt']:
                response = self._query_openai(query, company_name)
            elif platform == 'claude':
                response = self._query_claude(query, company_name)
            elif platform == 'perplexity':
                response = self._query_perplexity(query, company_name)
            else:  # arc_search - simulated
                response = self._simulate_arc_search(query, company_name)
            
            # Analyze content structure indicators
            readability = self._analyze_readability(response)
            structure = self._analyze_structure_quality(response)
            summarizability = self._analyze_summarizability(response)
            
            final_score = (readability + structure + summarizability) / 3
            comment = f"Content structure analysis. Readability: {readability:.1f}, Structure: {structure:.1f}, Summarizability: {summarizability:.1f}"
            
            return final_score, comment
            
        except Exception as e:
            return 0, f"Error calculating ACSO score: {str(e)}"
    
    def _calculate_uifl_score(self, company_name: str, platform: str) -> tuple:
        """Calculate User Interaction & Feedback Loop score"""
        try:
            query = f"How engaging and actionable is information about {company_name}?"
            
            if platform in ['chatgpt', 'searchgpt']:
                response = self._query_openai(query, company_name)
            elif platform == 'claude':
                response = self._query_claude(query, company_name)
            elif platform == 'perplexity':
                response = self._query_perplexity(query, company_name)
            else:  # arc_search - simulated
                response = self._simulate_arc_search(query, company_name)
            
            # Analyze engagement potential
            positivity = self._analyze_sentiment(response)
            actionability = self._analyze_actionability(response)
            follow_up_potential = self._analyze_follow_up_potential(response)
            
            final_score = (positivity + actionability + follow_up_potential) / 3
            comment = f"Engagement analysis. Positivity: {positivity:.1f}, Actionability: {actionability:.1f}, Follow-up potential: {follow_up_potential:.1f}"
            
            return final_score, comment
            
        except Exception as e:
            return 0, f"Error calculating UIFL score: {str(e)}"
    
    def _query_openai(self, query: str, company_name: str) -> str:
        """Query OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant providing information about companies."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying OpenAI: {str(e)}"
    
    def _query_claude(self, query: str, company_name: str) -> str:
        """Query Claude API (simulated for now)"""
        # Note: This would require Anthropic API key and proper implementation
        return f"Simulated Claude response for: {query}. Claude would provide detailed analysis about {company_name} with focus on accuracy and helpfulness."
    
    def _query_perplexity(self, query: str, company_name: str) -> str:
        """Query Perplexity API (simulated for now)"""
        # Note: This would require Perplexity API key and proper implementation
        return f"Simulated Perplexity response for: {query}. Perplexity would provide search-grounded information about {company_name} with citations."
    
    def _simulate_arc_search(self, query: str, company_name: str) -> str:
        """Simulate Arc Search response"""
        return f"Simulated Arc Search response for: {query}. Arc Search would provide browser-integrated search results about {company_name}."
    
    # Analysis helper methods
    def _analyze_relevance(self, response: str, company_name: str, query: str) -> float:
        """Analyze how relevant the response is to the query"""
        company_mentions = response.lower().count(company_name.lower())
        response_length = len(response.split())
        
        if response_length == 0:
            return 0
        
        relevance_ratio = min(1.0, company_mentions / max(1, response_length / 50))
        return relevance_ratio * 100
    
    def _analyze_completeness(self, response: str) -> float:
        """Analyze completeness of the response"""
        word_count = len(response.split())
        # Assume 50-200 words is a complete response
        if word_count < 20:
            return 30
        elif word_count < 50:
            return 60
        elif word_count < 200:
            return 90
        else:
            return 100
    
    def _analyze_accuracy(self, response: str, company_name: str) -> float:
        """Analyze accuracy indicators in the response"""
        # Look for uncertainty indicators
        uncertainty_words = ['might', 'could', 'possibly', 'unclear', 'unknown']
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        
        # Look for confidence indicators
        confidence_words = ['established', 'founded', 'known for', 'specializes']
        confidence_count = sum(1 for word in confidence_words if word in response.lower())
        
        if uncertainty_count > confidence_count:
            return 60
        else:
            return 85
    
    def _analyze_context(self, response: str, company_name: str) -> float:
        """Analyze contextual understanding"""
        context_indicators = ['industry', 'market', 'competitors', 'sector', 'business']
        context_count = sum(1 for indicator in context_indicators if indicator in response.lower())
        
        return min(100, context_count * 20)
    
    def _extract_sources(self, response: str) -> List[str]:
        """Extract sources from response"""
        # Simple URL extraction
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, response)
        
        # Extract domain names mentioned
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, response)
        
        return urls + domains
    
    def _analyze_source_credibility(self, sources: List[str]) -> float:
        """Analyze credibility of sources"""
        if not sources:
            return 40
        
        credible_domains = ['wikipedia.org', 'reuters.com', 'bloomberg.com', 'forbes.com', 'wsj.com']
        credible_count = sum(1 for source in sources if any(domain in source.lower() for domain in credible_domains))
        
        return min(100, (credible_count / len(sources)) * 100 + 40)
    
    def _analyze_verifiability(self, sources: List[str], company_name: str) -> float:
        """Analyze verifiability of sources"""
        if not sources:
            return 30
        
        # Assume sources are verifiable if they're from known domains
        return min(100, len(sources) * 15 + 40)
    
    def _analyze_readability(self, response: str) -> float:
        """Analyze readability of content"""
        sentences = response.split('.')
        words = response.split()
        
        if not sentences or not words:
            return 50
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            return 90
        elif 5 <= avg_sentence_length <= 35:
            return 70
        else:
            return 50
    
    def _analyze_structure_quality(self, response: str) -> float:
        """Analyze structure quality"""
        # Look for structure indicators
        structure_indicators = ['first', 'second', 'additionally', 'furthermore', 'in conclusion']
        structure_count = sum(1 for indicator in structure_indicators if indicator in response.lower())
        
        return min(100, structure_count * 25 + 50)
    
    def _analyze_summarizability(self, response: str) -> float:
        """Analyze how easily content can be summarized"""
        # Look for key information density
        key_phrases = ['founded', 'established', 'specializes', 'offers', 'provides', 'known for']
        key_count = sum(1 for phrase in key_phrases if phrase in response.lower())
        
        return min(100, key_count * 20 + 40)
    
    def _analyze_sentiment(self, response: str) -> float:
        """Analyze sentiment of the response"""
        positive_words = ['excellent', 'leading', 'innovative', 'successful', 'trusted', 'reliable']
        negative_words = ['poor', 'failing', 'problematic', 'controversial', 'declining']
        
        positive_count = sum(1 for word in positive_words if word in response.lower())
        negative_count = sum(1 for word in negative_words if word in response.lower())
        
        if positive_count > negative_count:
            return 80
        elif negative_count > positive_count:
            return 40
        else:
            return 60
    
    def _analyze_actionability(self, response: str) -> float:
        """Analyze actionability of the response"""
        action_words = ['visit', 'contact', 'learn more', 'explore', 'discover', 'check out']
        action_count = sum(1 for word in action_words if word in response.lower())
        
        return min(100, action_count * 30 + 50)
    
    def _analyze_follow_up_potential(self, response: str) -> float:
        """Analyze follow-up potential"""
        follow_up_indicators = ['more information', 'details', 'specific', 'particular', 'additional']
        follow_up_count = sum(1 for indicator in follow_up_indicators if indicator in response.lower())
        
        return min(100, follow_up_count * 25 + 60)
    
    def _generate_insights(self, company_name: str, platform_scores: Dict) -> str:
        """Generate overall insights from the analysis"""
        insights = []
        
        # Calculate average scores per methodology
        methodology_averages = {}
        for methodology in self.methodologies:
            total = sum(platform_scores[platform][methodology]['score'] for platform in self.platforms)
            methodology_averages[methodology] = total / len(self.platforms)
        
        # Find best and worst performing methodologies
        best_methodology = max(methodology_averages, key=methodology_averages.get)
        worst_methodology = min(methodology_averages, key=methodology_averages.get)
        
        insights.append(f"{company_name} performs best in {best_methodology.upper()} with an average score of {methodology_averages[best_methodology]:.1f}/100.")
        insights.append(f"The area needing most improvement is {worst_methodology.upper()} with an average score of {methodology_averages[worst_methodology]:.1f}/100.")
        
        # Platform analysis
        platform_averages = {}
        for platform in self.platforms:
            total = sum(platform_scores[platform][methodology]['score'] for methodology in self.methodologies)
            platform_averages[platform] = total / len(self.methodologies)
        
        best_platform = max(platform_averages, key=platform_averages.get)
        worst_platform = min(platform_averages, key=platform_averages.get)
        
        insights.append(f"Highest visibility on {best_platform} with an average score of {platform_averages[best_platform]:.1f}/100.")
        insights.append(f"Lowest visibility on {worst_platform} with an average score of {platform_averages[worst_platform]:.1f}/100.")
        
        return " ".join(insights)

