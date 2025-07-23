"""
🧠 Redis Memory Store for MESHNET Agents
Provides persistent long-term memory for Langflow, Langchain, and LangGraph agents
"""

import json
import redis
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import pickle

logger = logging.getLogger(__name__)

class RedisMemoryStore:
    """
    Redis-based memory store for agent long-term memory
    Supports conversation history, context, decisions, and knowledge base
    """

    def __init__(self, config: Dict):
        self.config = config
        self.redis_host = config.get('REDIS_HOST', 'localhost')
        self.redis_port = config.get('REDIS_PORT', 6379)
        self.redis_db = config.get('REDIS_DB', 0)
        self.redis_password = config.get('REDIS_PASSWORD', None)
        
        # Key prefixes for different data types
        self.prefixes = {
            'conversation': 'meshnet:conv:',
            'context': 'meshnet:ctx:',
            'decision': 'meshnet:decision:',
            'knowledge': 'meshnet:kb:',
            'agent_state': 'meshnet:state:',
            'memory_index': 'meshnet:index:',
            'embeddings': 'meshnet:embed:'
        }
        
        self.connect()

    def connect(self):
        """Establish Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    def store_conversation(self, agent_id: str, conversation_data: Dict) -> bool:
        """Store conversation history for an agent"""
        try:
            key = f"{self.prefixes['conversation']}{agent_id}"
            timestamp = datetime.utcnow().isoformat()
            
            conversation_entry = {
                'timestamp': timestamp,
                'data': conversation_data,
                'agent_id': agent_id
            }
            
            # Store as JSON string with timestamp as score for sorted set
            score = datetime.utcnow().timestamp()
            self.redis_client.zadd(key, {json.dumps(conversation_entry): score})
            
            # Keep only last 1000 conversations per agent
            self.redis_client.zremrangebyrank(key, 0, -1001)
            
            # Set expiration (30 days)
            self.redis_client.expire(key, 30 * 24 * 3600)
            
            logger.debug(f"💬 Stored conversation for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False

    def get_conversation_history(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve conversation history for an agent"""
        try:
            key = f"{self.prefixes['conversation']}{agent_id}"
            
            # Get recent conversations (highest scores first)
            conversations = self.redis_client.zrevrange(key, 0, limit - 1)
            
            history = []
            for conv_json in conversations:
                try:
                    conv_data = json.loads(conv_json)
                    history.append(conv_data)
                except json.JSONDecodeError:
                    continue
                    
            logger.debug(f"📜 Retrieved {len(history)} conversations for agent {agent_id}")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []

    def store_context(self, context_id: str, context_data: Dict, ttl: int = 3600) -> bool:
        """Store contextual information with TTL"""
        try:
            key = f"{self.prefixes['context']}{context_id}"
            
            context_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'data': context_data,
                'context_id': context_id
            }
            
            self.redis_client.setex(key, ttl, json.dumps(context_entry))
            
            logger.debug(f"🎯 Stored context {context_id} with TTL {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False

    def get_context(self, context_id: str) -> Optional[Dict]:
        """Retrieve contextual information"""
        try:
            key = f"{self.prefixes['context']}{context_id}"
            context_json = self.redis_client.get(key)
            
            if context_json:
                context_data = json.loads(context_json)
                logger.debug(f"🎯 Retrieved context {context_id}")
                return context_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return None

    def store_decision(self, agent_id: str, decision_data: Dict) -> bool:
        """Store agent decision with reasoning"""
        try:
            decision_id = hashlib.md5(
                f"{agent_id}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()
            
            key = f"{self.prefixes['decision']}{decision_id}"
            
            decision_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'agent_id': agent_id,
                'decision_id': decision_id,
                'data': decision_data
            }
            
            # Store decision
            self.redis_client.setex(key, 7 * 24 * 3600, json.dumps(decision_entry))  # 7 days TTL
            
            # Add to agent's decision index
            agent_decisions_key = f"{self.prefixes['decision']}index:{agent_id}"
            score = datetime.utcnow().timestamp()
            self.redis_client.zadd(agent_decisions_key, {decision_id: score})
            
            # Keep only last 500 decisions per agent
            self.redis_client.zremrangebyrank(agent_decisions_key, 0, -501)
            
            logger.debug(f"🎯 Stored decision {decision_id} for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store decision: {e}")
            return False

    def get_recent_decisions(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get recent decisions made by an agent"""
        try:
            agent_decisions_key = f"{self.prefixes['decision']}index:{agent_id}"
            decision_ids = self.redis_client.zrevrange(agent_decisions_key, 0, limit - 1)
            
            decisions = []
            for decision_id in decision_ids:
                key = f"{self.prefixes['decision']}{decision_id}"
                decision_json = self.redis_client.get(key)
                
                if decision_json:
                    try:
                        decision_data = json.loads(decision_json)
                        decisions.append(decision_data)
                    except json.JSONDecodeError:
                        continue
                        
            logger.debug(f"📊 Retrieved {len(decisions)} recent decisions for agent {agent_id}")
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to retrieve recent decisions: {e}")
            return []

    def store_knowledge(self, knowledge_id: str, knowledge_data: Dict, category: str = 'general') -> bool:
        """Store knowledge base information"""
        try:
            key = f"{self.prefixes['knowledge']}{category}:{knowledge_id}"
            
            knowledge_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'knowledge_id': knowledge_id,
                'category': category,
                'data': knowledge_data
            }
            
            self.redis_client.set(key, json.dumps(knowledge_entry))
            
            # Add to category index
            category_index_key = f"{self.prefixes['knowledge']}index:{category}"
            self.redis_client.sadd(category_index_key, knowledge_id)
            
            logger.debug(f"📚 Stored knowledge {knowledge_id} in category {category}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            return False

    def get_knowledge(self, knowledge_id: str, category: str = 'general') -> Optional[Dict]:
        """Retrieve knowledge base information"""
        try:
            key = f"{self.prefixes['knowledge']}{category}:{knowledge_id}"
            knowledge_json = self.redis_client.get(key)
            
            if knowledge_json:
                knowledge_data = json.loads(knowledge_json)
                logger.debug(f"📚 Retrieved knowledge {knowledge_id} from category {category}")
                return knowledge_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge: {e}")
            return None

    def get_knowledge_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """Get all knowledge items in a category"""
        try:
            category_index_key = f"{self.prefixes['knowledge']}index:{category}"
            knowledge_ids = self.redis_client.srandmember(category_index_key, limit)
            
            knowledge_items = []
            for knowledge_id in knowledge_ids:
                knowledge_data = self.get_knowledge(knowledge_id, category)
                if knowledge_data:
                    knowledge_items.append(knowledge_data)
                    
            logger.debug(f"📚 Retrieved {len(knowledge_items)} knowledge items from category {category}")
            return knowledge_items
            
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge by category: {e}")
            return []

    def store_agent_state(self, agent_id: str, state_data: Dict) -> bool:
        """Store current agent state"""
        try:
            key = f"{self.prefixes['agent_state']}{agent_id}"
            
            state_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'agent_id': agent_id,
                'state': state_data
            }
            
            self.redis_client.set(key, json.dumps(state_entry))
            
            logger.debug(f"🤖 Stored state for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store agent state: {e}")
            return False

    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Retrieve current agent state"""
        try:
            key = f"{self.prefixes['agent_state']}{agent_id}"
            state_json = self.redis_client.get(key)
            
            if state_json:
                state_data = json.loads(state_json)
                logger.debug(f"🤖 Retrieved state for agent {agent_id}")
                return state_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent state: {e}")
            return None

    def search_memory(self, query: str, agent_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search across all memory types for relevant information"""
        try:
            results = []
            
            # Search conversations
            if agent_id:
                conversations = self.get_conversation_history(agent_id, limit * 2)
            else:
                # Search across all agents (simplified)
                conversations = []
                
            for conv in conversations:
                if query.lower() in json.dumps(conv).lower():
                    results.append({
                        'type': 'conversation',
                        'relevance': 'high',
                        'data': conv
                    })
                    
            # Search decisions
            if agent_id:
                decisions = self.get_recent_decisions(agent_id, limit * 2)
                for decision in decisions:
                    if query.lower() in json.dumps(decision).lower():
                        results.append({
                            'type': 'decision',
                            'relevance': 'medium',
                            'data': decision
                        })
            
            # Limit results
            results = results[:limit]
            
            logger.debug(f"🔍 Found {len(results)} memory items matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []

    def get_memory_stats(self) -> Dict:
        """Get memory store statistics"""
        try:
            stats = {
                'redis_info': self.redis_client.info('memory'),
                'total_keys': self.redis_client.dbsize(),
                'key_counts': {}
            }
            
            # Count keys by prefix
            for prefix_name, prefix in self.prefixes.items():
                pattern = f"{prefix}*"
                keys = self.redis_client.keys(pattern)
                stats['key_counts'][prefix_name] = len(keys)
                
            logger.debug(f"📊 Retrieved memory statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for a specific agent"""
        try:
            patterns = [
                f"{self.prefixes['conversation']}{agent_id}",
                f"{self.prefixes['decision']}index:{agent_id}",
                f"{self.prefixes['agent_state']}{agent_id}"
            ]
            
            deleted_count = 0
            for pattern in patterns:
                if self.redis_client.exists(pattern):
                    self.redis_client.delete(pattern)
                    deleted_count += 1
                    
            # Also clear individual decision keys
            agent_decisions_key = f"{self.prefixes['decision']}index:{agent_id}"
            decision_ids = self.redis_client.zrange(agent_decisions_key, 0, -1)
            
            for decision_id in decision_ids:
                decision_key = f"{self.prefixes['decision']}{decision_id}"
                if self.redis_client.exists(decision_key):
                    self.redis_client.delete(decision_key)
                    deleted_count += 1
                    
            logger.info(f"🗑️ Cleared {deleted_count} memory items for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear agent memory: {e}")
            return False

    def health_check(self) -> Dict:
        """Check Redis connection and memory store health"""
        try:
            # Test basic operations
            test_key = "meshnet:health:test"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            # Write test
            self.redis_client.setex(test_key, 60, json.dumps(test_value))
            
            # Read test
            retrieved = self.redis_client.get(test_key)
            
            # Clean up
            self.redis_client.delete(test_key)
            
            if retrieved:
                return {
                    'status': 'healthy',
                    'redis_connected': True,
                    'read_write_ok': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'redis_connected': True,
                    'read_write_ok': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'redis_connected': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class LangChainRedisMemory:
    """
    LangChain-compatible memory interface using Redis backend
    """
    
    def __init__(self, redis_store: RedisMemoryStore, agent_id: str):
        self.redis_store = redis_store
        self.agent_id = agent_id
        self.memory_key = "chat_history"
        
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context to Redis"""
        conversation_data = {
            'inputs': inputs,
            'outputs': outputs,
            'type': 'langchain_context'
        }
        self.redis_store.store_conversation(self.agent_id, conversation_data)
        
    def clear(self) -> None:
        """Clear conversation history"""
        self.redis_store.clear_agent_memory(self.agent_id)
        
    @property
    def buffer(self) -> str:
        """Get conversation buffer as string"""
        history = self.redis_store.get_conversation_history(self.agent_id, 10)
        
        buffer_parts = []
        for entry in history:
            if entry.get('data', {}).get('type') == 'langchain_context':
                data = entry['data']
                inputs = data.get('inputs', {})
                outputs = data.get('outputs', {})
                
                for key, value in inputs.items():
                    buffer_parts.append(f"Human: {value}")
                    
                for key, value in outputs.items():
                    buffer_parts.append(f"AI: {value}")
                    
        return "\n".join(buffer_parts)


class LangGraphRedisCheckpoint:
    """
    LangGraph-compatible checkpoint store using Redis backend
    """
    
    def __init__(self, redis_store: RedisMemoryStore):
        self.redis_store = redis_store
        
    def save_checkpoint(self, thread_id: str, checkpoint_data: Dict) -> None:
        """Save checkpoint state"""
        self.redis_store.store_context(
            f"langgraph_checkpoint_{thread_id}",
            checkpoint_data,
            ttl=24 * 3600  # 24 hours
        )
        
    def load_checkpoint(self, thread_id: str) -> Optional[Dict]:
        """Load checkpoint state"""
        context = self.redis_store.get_context(f"langgraph_checkpoint_{thread_id}")
        return context.get('data') if context else None
        
    def list_checkpoints(self, thread_id: str) -> List[Dict]:
        """List available checkpoints for a thread"""
        # Simplified implementation
        checkpoint = self.load_checkpoint(thread_id)
        return [checkpoint] if checkpoint else []

