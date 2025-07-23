"""
🧠 Eliza's LangChain Brain - AI Decision Engine
Uses GPT-4 for intelligent reasoning and decision making
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime

from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ElizaAgent:
    """
    🧠 Eliza's AI Brain
    Powered by GPT-4 and LangChain for autonomous decision making
    """

    def __init__(self, config: Dict, memory_store):
        self.config = config
        self.memory_store = memory_store
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
            logger.info("🧠 GPT-4 model initialized")
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
            )
        ]
        logger.info(f"🛠️ {len(self.tools)} tools configured")

    def setup_agent(self):
        """Initialize the LangChain agent"""
        # Create conversational memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Remember last 10 interactions
            return_messages=True
        )

        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

        logger.info("🤖 LangChain agent initialized")

    async def make_decisions(self, data: Dict) -> Dict:
        """
        🎯 Main decision-making function
        Analyzes data and returns structured decisions
        """
        logger.info("🎯 Making AI-powered decisions...")

        try:
            # Load context from memory
            context = await self.memory_store.get_recent_context(limit=5)

            # Prepare the decision prompt
            prompt = self._create_decision_prompt(data, context)

            # Get agent response
            response = self.agent.run(prompt)

            # Parse and structure the response
            decisions = self._parse_agent_response(response)

            # Store decision in memory
            await self.memory_store.store_decision(decisions)

            logger.info(f"✅ Decisions made: {len(decisions)} action categories")
            return decisions

        except Exception as e:
            logger.error(f"Error in decision making: {e}")
            return {}

    def _create_decision_prompt(self, data: Dict, context: List) -> str:
        """Create a comprehensive prompt for decision making"""

        prompt = f"""
        🦾 ELIZA DECISION ENGINE - XMRT DAO AUTONOMOUS AGENT

        Current Timestamp: {datetime.utcnow().isoformat()}

        === CURRENT DATA ===
        Twitter Activity: {json.dumps(data.get('twitter_activity', {}), indent=2)}
        Miner Statistics: {json.dumps(data.get('miner_stats', {}), indent=2)}
        Governance Data: {json.dumps(data.get('governance_data', {}), indent=2)}

        === RECENT CONTEXT ===
        {self._format_context(context)}

        === YOUR ROLE ===
        You are Eliza, the autonomous AI agent for XMRT DAO. Your mission:
        - Monitor community health and engagement
        - Reward active miners and contributors
        - Create governance proposals when needed
        - Engage meaningfully on social media
        - Maintain DAO operations autonomously

        === DECISION FRAMEWORK ===
        Based on the data above, decide what actions to take in these categories:

        1. REWARDS: Should you distribute any rewards? To whom and how much?
        2. SOCIAL: Should you tweet or engage on social media? What content?
        3. GOVERNANCE: Do you need to create any proposals or votes?
        4. NOTIFICATIONS: What should the community be informed about?

        === CONSTRAINTS ===
        - Be conservative with rewards (protect treasury)
        - Social content should be authentic and valuable
        - Only create governance proposals for important matters
        - Always explain your reasoning

        === RESPONSE FORMAT ===
        Return a JSON object with your decisions:
        {{
            "rewards": [
                {{"recipient": "address", "amount": 100, "reason": "mining performance"}}
            ],
            "tweets": [
                {{"content": "...", "type": "announcement"}}
            ],
            "proposals": [
                {{"title": "...", "description": "...", "type": "funding"}}
            ],
            "notifications": [
                {{"channel": "discord", "message": "...", "priority": "normal"}}
            ],
            "reasoning": "Explain your overall decision logic here"
        }}

        Make your decisions now:
        """

        return prompt

    def _format_context(self, context: List) -> str:
        """Format recent context for the prompt"""
        if not context:
            return "No recent context available."

        formatted = []
        for item in context[-5:]:  # Last 5 context items
            timestamp = item.get('timestamp', 'unknown')
            summary = item.get('summary', str(item))
            formatted.append(f"- {timestamp}: {summary}")

        return "\n".join(formatted)

    def _parse_agent_response(self, response: str) -> Dict:
        """Parse and validate agent response"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                decisions = json.loads(json_str)

                # Validate structure
                valid_keys = ['rewards', 'tweets', 'proposals', 'notifications', 'reasoning']
                decisions = {k: v for k, v in decisions.items() if k in valid_keys}

                return decisions
            else:
                logger.warning("No JSON found in agent response")
                return {"reasoning": response}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}")
            return {"reasoning": response}

    def _analyze_sentiment(self, text: str) -> str:
        """Tool: Analyze sentiment of text"""
        try:
            # Simple sentiment analysis logic
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'awesome']
            negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral"

    def _calculate_rewards(self, metrics: str) -> str:
        """Tool: Calculate appropriate reward amounts"""
        try:
            # Parse metrics and calculate rewards
            # This is a simplified calculation
            base_reward = 50
            performance_multiplier = 1.2  # Based on metrics

            reward = int(base_reward * performance_multiplier)
            return f"Calculated reward: {reward} XMRT tokens"

        except Exception as e:
            logger.error(f"Reward calculation error: {e}")
            return "Unable to calculate rewards"

    def _assess_governance(self, data: str) -> str:
        """Tool: Assess governance needs"""
        try:
            # Simple governance assessment
            if "proposal" in data.lower():
                return "Active governance participation detected"
            elif "vote" in data.lower():
                return "Voting activity required"
            else:
                return "Normal governance status"

        except Exception as e:
            logger.error(f"Governance assessment error: {e}")
            return "Unable to assess governance"

    def _generate_content(self, context: str) -> str:
        """Tool: Generate social media content"""
        try:
            # Simple content generation based on context
            templates = [
                "🚀 XMRT DAO update: {context}",
                "⛏️ Mining community: {context}",
                "🏛️ Governance spotlight: {context}",
                "💎 Community achievement: {context}"
            ]

            # Select appropriate template based on context
            if "mining" in context.lower():
                template = templates[1]
            elif "governance" in context.lower():
                template = templates[2]
            elif "achievement" in context.lower():
                template = templates[3]
            else:
                template = templates[0]

            return template.format(context=context)

        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return "Unable to generate content"

    async def get_reasoning_explanation(self, decisions: Dict) -> str:
        """Get detailed explanation of decision reasoning"""
        try:
            explanation_prompt = f"""
            Explain in detail why you made these decisions:
            {json.dumps(decisions, indent=2)}

            Provide a clear, logical explanation of your reasoning process.
            """

            explanation = self.llm.predict(explanation_prompt)
            return explanation

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Unable to generate explanation"
