"""
🧠 Enhanced Eliza's LangChain Brain with Redis Memory
Uses GPT-4 for intelligent reasoning with persistent long-term memory
"""

import json
import logging
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

from memory.redis_memory import RedisMemoryStore, LangChainRedisMemory

logger = logging.getLogger(__name__)

class EnhancedElizaAgent:
    """
    🧠 Enhanced Eliza's AI Brain with Redis Memory
    Powered by GPT-4 and LangChain with persistent long-term memory
    """

    def __init__(self, config: Dict):
        self.config = config
        self.agent_id = "eliza_meshnet"
        
        # Initialize Redis memory store
        self.redis_config = {
            'REDIS_HOST': config.get('REDIS_HOST', 'localhost'),
            'REDIS_PORT': config.get('REDIS_PORT', 6379),
            'REDIS_DB': config.get('REDIS_DB', 0),
            'REDIS_PASSWORD': config.get('REDIS_PASSWORD', None)
        }
        
        self.memory_store = RedisMemoryStore(self.redis_config)
        self.setup_llm()
        self.setup_tools()
        self.setup_agent()

    def setup_llm(self):
        """Initialize the language model"""
        try:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.3,  # Balanced creativity and consistency
                openai_api_key=self.config.get("OPENAI_API_KEY"),
                max_tokens=2000
            )
            logger.info("🧠 GPT-4 model initialized with Redis memory")
        except Exception as e:
            logger.error(f"Failed to initialize GPT-4: {e}")
            raise

    def setup_tools(self):
        """Define tools available to the agent"""
        self.tools = [
            Tool(
                name="analyze_sentiment",
                description="Analyze sentiment of social media data",
                func=self._analyze_sentiment
            ),
            Tool(
                name="calculate_rewards",
                description="Calculate reward amounts based on performance metrics",
                func=self._calculate_rewards
            ),
            Tool(
                name="assess_governance",
                description="Evaluate governance proposals and community needs",
                func=self._assess_governance
            ),
            Tool(
                name="generate_content",
                description="Generate appropriate social media content",
                func=self._generate_content
            ),
            Tool(
                name="search_memory",
                description="Search long-term memory for relevant past information",
                func=self._search_memory
            ),
            Tool(
                name="get_recent_decisions",
                description="Retrieve recent decisions made by the agent",
                func=self._get_recent_decisions
            ),
            Tool(
                name="store_knowledge",
                description="Store important information in long-term knowledge base",
                func=self._store_knowledge
            )
        ]
        logger.info(f"🛠️ {len(self.tools)} tools configured with memory integration")

    def setup_agent(self):
        """Initialize the LangChain agent with Redis memory"""
        # Create Redis-backed conversational memory
        self.memory = LangChainRedisMemory(self.memory_store, self.agent_id)

        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

        logger.info("🤖 Enhanced LangChain agent initialized with Redis memory")

    async def make_decisions(self, data: Dict) -> Dict:
        """
        🎯 Main decision-making function with memory integration
        Analyzes data and returns structured decisions using long-term memory
        """
        logger.info("🎯 Making AI-powered decisions with memory context...")

        try:
            # Load recent context and decisions from memory
            recent_decisions = self.memory_store.get_recent_decisions(self.agent_id, limit=5)
            conversation_history = self.memory_store.get_conversation_history(self.agent_id, limit=10)
            
            # Search for relevant past experiences
            relevant_memories = self.memory_store.search_memory(
                query=f"mining rewards governance {data.get('context', '')}",
                agent_id=self.agent_id,
                limit=5
            )

            # Prepare the enhanced decision prompt with memory context
            prompt = self._create_enhanced_decision_prompt(data, recent_decisions, relevant_memories)

            # Get agent response
            response = self.agent.run(prompt)

            # Parse and structure the response
            decisions = self._parse_agent_response(response)

            # Store decision in Redis memory
            decision_data = {
                'decisions': decisions,
                'input_data': data,
                'reasoning': decisions.get('reasoning', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self._store_decision_async(decision_data)

            # Store conversation context
            conversation_data = {
                'type': 'decision_making',
                'input': data,
                'output': decisions,
                'memory_used': len(relevant_memories)
            }
            
            self.memory_store.store_conversation(self.agent_id, conversation_data)

            logger.info(f"✅ Decisions made with memory: {len(decisions)} action categories")
            return decisions

        except Exception as e:
            logger.error(f"Error in enhanced decision making: {e}")
            return {}

    def _create_enhanced_decision_prompt(self, data: Dict, recent_decisions: List, relevant_memories: List) -> str:
        """Create a comprehensive prompt with memory context"""

        memory_context = self._format_memory_context(relevant_memories)
        recent_context = self._format_recent_decisions(recent_decisions)

        prompt = f"""
        🦾 ELIZA ENHANCED DECISION ENGINE - XMRT DAO AUTONOMOUS AGENT WITH MEMORY

        Current Timestamp: {datetime.utcnow().isoformat()}

        === CURRENT DATA ===
        Twitter Activity: {json.dumps(data.get('twitter_activity', {}), indent=2)}
        Miner Statistics: {json.dumps(data.get('miner_stats', {}), indent=2)}
        Governance Data: {json.dumps(data.get('governance_data', {}), indent=2)}

        === MEMORY CONTEXT ===
        {memory_context}

        === RECENT DECISIONS ===
        {recent_context}

        === YOUR ENHANCED ROLE ===
        You are Eliza, the autonomous AI agent for XMRT DAO with persistent memory.
        Your mission:
        - Monitor community health and engagement
        - Reward active miners and contributors
        - Create governance proposals when needed
        - Engage meaningfully on social media
        - Maintain DAO operations autonomously
        - LEARN from past decisions and outcomes
        - AVOID repeating unsuccessful strategies
        - BUILD on successful patterns from memory

        === ENHANCED DECISION FRAMEWORK ===
        Based on the current data AND your memory context, decide what actions to take:

        1. REWARDS: Should you distribute any rewards? Consider past reward patterns and outcomes.
        2. SOCIAL: Should you tweet or engage? Learn from past social media performance.
        3. GOVERNANCE: Do you need proposals? Reference similar past governance decisions.
        4. NOTIFICATIONS: What should the community know? Avoid redundant notifications.
        5. LEARNING: What patterns do you notice? How can you improve based on memory?

        === MEMORY-INFORMED CONSTRAINTS ===
        - Be conservative with rewards (protect treasury) - check past reward amounts
        - Social content should be authentic - reference successful past content
        - Only create governance proposals for important matters - avoid duplicating recent proposals
        - Learn from past mistakes and successes in your memory
        - Always explain how memory influenced your decisions

        === ENHANCED RESPONSE FORMAT ===
        Return a JSON object with your memory-informed decisions:
        {{
            "rewards": [
                {{"recipient": "address", "amount": 100, "reason": "mining performance", "memory_basis": "similar reward in memory"}}
            ],
            "tweets": [
                {{"content": "...", "type": "announcement", "memory_basis": "successful pattern from past"}}
            ],
            "proposals": [
                {{"title": "...", "description": "...", "type": "funding", "memory_basis": "learned from past proposals"}}
            ],
            "notifications": [
                {{"channel": "discord", "message": "...", "priority": "normal", "memory_basis": "avoiding recent duplicates"}}
            ],
            "learning": [
                {{"observation": "pattern noticed", "action": "how this influences future decisions"}}
            ],
            "reasoning": "Explain your overall decision logic and how memory influenced your choices"
        }}

        Make your memory-informed decisions now:
        """

        return prompt

    def _format_memory_context(self, relevant_memories: List) -> str:
        """Format relevant memories for the prompt"""
        if not relevant_memories:
            return "No relevant memories found."

        formatted = []
        for memory in relevant_memories:
            memory_type = memory.get('type', 'unknown')
            relevance = memory.get('relevance', 'unknown')
            data = memory.get('data', {})
            
            if memory_type == 'decision':
                timestamp = data.get('timestamp', 'unknown')
                decisions = data.get('data', {}).get('decisions', {})
                reasoning = decisions.get('reasoning', 'No reasoning provided')
                formatted.append(f"- {timestamp} ({relevance} relevance): Decision - {reasoning[:100]}...")
            elif memory_type == 'conversation':
                timestamp = data.get('timestamp', 'unknown')
                conv_data = data.get('data', {})
                formatted.append(f"- {timestamp} ({relevance} relevance): Conversation - {str(conv_data)[:100]}...")

        return "\n".join(formatted)

    def _format_recent_decisions(self, recent_decisions: List) -> str:
        """Format recent decisions for context"""
        if not recent_decisions:
            return "No recent decisions found."

        formatted = []
        for decision in recent_decisions[-3:]:  # Last 3 decisions
            timestamp = decision.get('timestamp', 'unknown')
            decisions = decision.get('data', {}).get('decisions', {})
            reasoning = decisions.get('reasoning', 'No reasoning provided')
            formatted.append(f"- {timestamp}: {reasoning[:150]}...")

        return "\n".join(formatted)

    async def _store_decision_async(self, decision_data: Dict):
        """Store decision asynchronously"""
        try:
            self.memory_store.store_decision(self.agent_id, decision_data)
        except Exception as e:
            logger.error(f"Failed to store decision in memory: {e}")

    def _parse_agent_response(self, response: str) -> Dict:
        """Parse and validate agent response with enhanced structure"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                decisions = json.loads(json_str)

                # Validate enhanced structure
                valid_keys = ['rewards', 'tweets', 'proposals', 'notifications', 'learning', 'reasoning']
                decisions = {k: v for k, v in decisions.items() if k in valid_keys}

                return decisions
            else:
                logger.warning("No JSON found in agent response")
                return {"reasoning": response}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}")
            return {"reasoning": response}

    # Enhanced tool functions with memory integration

    def _search_memory(self, query: str) -> str:
        """Tool: Search long-term memory for relevant information"""
        try:
            memories = self.memory_store.search_memory(query, self.agent_id, limit=5)
            
            if not memories:
                return f"No relevant memories found for query: {query}"
            
            results = []
            for memory in memories:
                memory_type = memory.get('type', 'unknown')
                relevance = memory.get('relevance', 'unknown')
                data = memory.get('data', {})
                
                if memory_type == 'decision':
                    timestamp = data.get('timestamp', 'unknown')
                    reasoning = data.get('data', {}).get('decisions', {}).get('reasoning', 'No reasoning')
                    results.append(f"Decision ({timestamp}): {reasoning[:100]}...")
                elif memory_type == 'conversation':
                    timestamp = data.get('timestamp', 'unknown')
                    conv_type = data.get('data', {}).get('type', 'conversation')
                    results.append(f"Conversation ({timestamp}): {conv_type}")
            
            return f"Found {len(memories)} relevant memories:\n" + "\n".join(results)
            
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return f"Memory search failed: {str(e)}"

    def _get_recent_decisions(self, context: str) -> str:
        """Tool: Get recent decisions from memory"""
        try:
            decisions = self.memory_store.get_recent_decisions(self.agent_id, limit=5)
            
            if not decisions:
                return "No recent decisions found in memory."
            
            results = []
            for decision in decisions:
                timestamp = decision.get('timestamp', 'unknown')
                decision_data = decision.get('data', {}).get('decisions', {})
                reasoning = decision_data.get('reasoning', 'No reasoning provided')
                results.append(f"- {timestamp}: {reasoning[:100]}...")
            
            return f"Recent decisions:\n" + "\n".join(results)
            
        except Exception as e:
            logger.error(f"Recent decisions retrieval error: {e}")
            return f"Failed to retrieve recent decisions: {str(e)}"

    def _store_knowledge(self, knowledge_data: str) -> str:
        """Tool: Store important information in knowledge base"""
        try:
            # Parse knowledge data (expecting format: "category:id:data")
            parts = knowledge_data.split(':', 2)
            if len(parts) != 3:
                return "Invalid knowledge format. Use 'category:id:data'"
            
            category, knowledge_id, data = parts
            
            knowledge_entry = {
                'content': data,
                'source': 'agent_tool',
                'importance': 'high'
            }
            
            success = self.memory_store.store_knowledge(knowledge_id, knowledge_entry, category)
            
            if success:
                return f"Successfully stored knowledge '{knowledge_id}' in category '{category}'"
            else:
                return "Failed to store knowledge in memory"
                
        except Exception as e:
            logger.error(f"Knowledge storage error: {e}")
            return f"Failed to store knowledge: {str(e)}"

    # Original tool functions (enhanced with memory awareness)

    def _analyze_sentiment(self, text: str) -> str:
        """Tool: Analyze sentiment with memory context"""
        try:
            # Get past sentiment analyses for comparison
            past_analyses = self.memory_store.search_memory(
                f"sentiment analysis {text[:50]}", 
                self.agent_id, 
                limit=3
            )
            
            # Simple sentiment analysis logic
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'awesome']
            negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Store this analysis in memory
            analysis_data = {
                'text': text[:100],
                'sentiment': sentiment,
                'positive_count': positive_count,
                'negative_count': negative_count
            }
            
            self.memory_store.store_knowledge(
                f"sentiment_{datetime.utcnow().timestamp()}", 
                analysis_data, 
                'sentiment_analysis'
            )
            
            memory_context = f" (Found {len(past_analyses)} similar past analyses)" if past_analyses else ""
            return f"Sentiment: {sentiment}{memory_context}"
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral"

    def _calculate_rewards(self, metrics: str) -> str:
        """Tool: Calculate rewards with memory of past distributions"""
        try:
            # Get past reward calculations for pattern learning
            past_rewards = self.memory_store.search_memory(
                "reward calculation distribution", 
                self.agent_id, 
                limit=5
            )
            
            # Parse metrics and calculate rewards
            base_reward = 50
            performance_multiplier = 1.2
            
            # Adjust based on memory patterns
            if past_rewards:
                # Simple adjustment based on past patterns
                recent_rewards = len([r for r in past_rewards if 'reward' in str(r).lower()])
                if recent_rewards > 3:
                    performance_multiplier *= 0.9  # Be more conservative
            
            reward = int(base_reward * performance_multiplier)
            
            # Store this calculation in memory
            calc_data = {
                'metrics': metrics[:100],
                'base_reward': base_reward,
                'multiplier': performance_multiplier,
                'final_reward': reward,
                'past_rewards_considered': len(past_rewards)
            }
            
            self.memory_store.store_knowledge(
                f"reward_calc_{datetime.utcnow().timestamp()}", 
                calc_data, 
                'reward_calculations'
            )
            
            return f"Calculated reward: {reward} XMRT tokens (based on {len(past_rewards)} past calculations)"

        except Exception as e:
            logger.error(f"Reward calculation error: {e}")
            return "Unable to calculate rewards"

    def _assess_governance(self, data: str) -> str:
        """Tool: Assess governance with historical context"""
        try:
            # Get past governance assessments
            past_governance = self.memory_store.search_memory(
                "governance proposal assessment", 
                self.agent_id, 
                limit=5
            )
            
            assessment = "Normal governance status"
            
            if "proposal" in data.lower():
                assessment = "Active governance participation detected"
            elif "vote" in data.lower():
                assessment = "Voting activity required"
            
            # Store governance assessment
            gov_data = {
                'input_data': data[:100],
                'assessment': assessment,
                'past_assessments_count': len(past_governance)
            }
            
            self.memory_store.store_knowledge(
                f"governance_{datetime.utcnow().timestamp()}", 
                gov_data, 
                'governance_assessments'
            )
            
            context = f" (Informed by {len(past_governance)} past assessments)" if past_governance else ""
            return f"{assessment}{context}"

        except Exception as e:
            logger.error(f"Governance assessment error: {e}")
            return "Unable to assess governance"

    def _generate_content(self, context: str) -> str:
        """Tool: Generate content with memory of successful patterns"""
        try:
            # Get past successful content patterns
            past_content = self.memory_store.search_memory(
                "social media content generation", 
                self.agent_id, 
                limit=5
            )
            
            templates = [
                "🚀 XMRT DAO update: {context}",
                "⛏️ Mining community: {context}",
                "🏛️ Governance spotlight: {context}",
                "💎 Community achievement: {context}"
            ]

            # Select template based on context and past success
            if "mining" in context.lower():
                template = templates[1]
            elif "governance" in context.lower():
                template = templates[2]
            elif "achievement" in context.lower():
                template = templates[3]
            else:
                template = templates[0]

            content = template.format(context=context)
            
            # Store content generation in memory
            content_data = {
                'context': context[:100],
                'generated_content': content,
                'template_used': template,
                'past_patterns_considered': len(past_content)
            }
            
            self.memory_store.store_knowledge(
                f"content_{datetime.utcnow().timestamp()}", 
                content_data, 
                'content_generation'
            )
            
            memory_note = f" (Informed by {len(past_content)} past patterns)" if past_content else ""
            return f"{content}{memory_note}"

        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return "Unable to generate content"

    async def get_memory_stats(self) -> Dict:
        """Get comprehensive memory statistics"""
        try:
            stats = self.memory_store.get_memory_stats()
            health = self.memory_store.health_check()
            
            return {
                'memory_stats': stats,
                'health_check': health,
                'agent_id': self.agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}

    async def clear_memory(self) -> bool:
        """Clear all memory for this agent"""
        try:
            return self.memory_store.clear_agent_memory(self.agent_id)
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False

