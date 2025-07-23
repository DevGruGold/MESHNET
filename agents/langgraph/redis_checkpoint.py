"""
🔄 LangGraph Redis Checkpoint Integration for MESHNET
Provides Redis-based checkpointing and state management for LangGraph agents
"""

import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import pickle

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.redis_memory import RedisMemoryStore

logger = logging.getLogger(__name__)

class LangGraphRedisCheckpointer:
    """
    Redis-based checkpointer for LangGraph
    Provides persistent state management and recovery capabilities
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.checkpointer_id = "langgraph_meshnet"
        
        # Initialize Redis memory store
        self.redis_config = {
            'REDIS_HOST': config.get('REDIS_HOST', 'localhost'),
            'REDIS_PORT': config.get('REDIS_PORT', 6379),
            'REDIS_DB': config.get('REDIS_DB', 2),  # Different DB for LangGraph
            'REDIS_PASSWORD': config.get('REDIS_PASSWORD', None)
        }
        
        self.memory_store = RedisMemoryStore(self.redis_config)
        
        # Checkpoint-specific prefixes
        self.checkpoint_prefix = "langgraph:checkpoint:"
        self.thread_prefix = "langgraph:thread:"
        self.metadata_prefix = "langgraph:metadata:"
        
        logger.info("🔄 LangGraph Redis checkpointer initialized")

    def save_checkpoint(self, thread_id: str, checkpoint_data: Dict, metadata: Optional[Dict] = None) -> str:
        """Save a checkpoint for a thread"""
        try:
            checkpoint_id = self._generate_checkpoint_id(thread_id)
            
            checkpoint_entry = {
                'thread_id': thread_id,
                'checkpoint_id': checkpoint_id,
                'data': checkpoint_data,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat(),
                'component': 'langgraph'
            }
            
            # Store checkpoint data
            checkpoint_key = f"{self.checkpoint_prefix}{checkpoint_id}"
            success = self.memory_store.redis_client.setex(
                checkpoint_key,
                24 * 3600,  # 24 hours TTL
                json.dumps(checkpoint_entry)
            )
            
            if success:
                # Add to thread's checkpoint list
                thread_key = f"{self.thread_prefix}{thread_id}"
                score = datetime.utcnow().timestamp()
                self.memory_store.redis_client.zadd(thread_key, {checkpoint_id: score})
                
                # Keep only last 50 checkpoints per thread
                self.memory_store.redis_client.zremrangebyrank(thread_key, 0, -51)
                
                # Store metadata separately for faster queries
                if metadata:
                    metadata_key = f"{self.metadata_prefix}{checkpoint_id}"
                    self.memory_store.redis_client.setex(
                        metadata_key,
                        24 * 3600,
                        json.dumps(metadata)
                    )
                
                logger.debug(f"🔄 Saved checkpoint {checkpoint_id} for thread {thread_id}")
                return checkpoint_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return None

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Load a specific checkpoint"""
        try:
            checkpoint_key = f"{self.checkpoint_prefix}{checkpoint_id}"
            checkpoint_json = self.memory_store.redis_client.get(checkpoint_key)
            
            if checkpoint_json:
                checkpoint_data = json.loads(checkpoint_json)
                logger.debug(f"🔄 Loaded checkpoint {checkpoint_id}")
                return checkpoint_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def get_latest_checkpoint(self, thread_id: str) -> Optional[Dict]:
        """Get the latest checkpoint for a thread"""
        try:
            thread_key = f"{self.thread_prefix}{thread_id}"
            
            # Get the most recent checkpoint ID
            latest_checkpoints = self.memory_store.redis_client.zrevrange(thread_key, 0, 0)
            
            if latest_checkpoints:
                latest_checkpoint_id = latest_checkpoints[0]
                return self.load_checkpoint(latest_checkpoint_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest checkpoint: {e}")
            return None

    def list_checkpoints(self, thread_id: str, limit: int = 10) -> List[Dict]:
        """List checkpoints for a thread"""
        try:
            thread_key = f"{self.thread_prefix}{thread_id}"
            
            # Get recent checkpoint IDs
            checkpoint_ids = self.memory_store.redis_client.zrevrange(thread_key, 0, limit - 1)
            
            checkpoints = []
            for checkpoint_id in checkpoint_ids:
                checkpoint_data = self.load_checkpoint(checkpoint_id)
                if checkpoint_data:
                    checkpoints.append(checkpoint_data)
            
            logger.debug(f"🔄 Listed {len(checkpoints)} checkpoints for thread {thread_id}")
            return checkpoints
            
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []

    def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Restore state from a checkpoint"""
        try:
            checkpoint_data = self.load_checkpoint(checkpoint_id)
            
            if checkpoint_data:
                # Extract the actual state data
                state_data = checkpoint_data.get('data', {})
                
                logger.info(f"🔄 Restored state from checkpoint {checkpoint_id}")
                return {
                    'state': state_data,
                    'metadata': checkpoint_data.get('metadata', {}),
                    'thread_id': checkpoint_data.get('thread_id'),
                    'timestamp': checkpoint_data.get('timestamp'),
                    'checkpoint_id': checkpoint_id
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to restore from checkpoint: {e}")
            return None

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        try:
            checkpoint_key = f"{self.checkpoint_prefix}{checkpoint_id}"
            metadata_key = f"{self.metadata_prefix}{checkpoint_id}"
            
            # Delete checkpoint and metadata
            deleted_count = 0
            if self.memory_store.redis_client.exists(checkpoint_key):
                self.memory_store.redis_client.delete(checkpoint_key)
                deleted_count += 1
            
            if self.memory_store.redis_client.exists(metadata_key):
                self.memory_store.redis_client.delete(metadata_key)
                deleted_count += 1
            
            # Remove from thread index (we'd need to know the thread_id for this)
            # This is a simplified implementation
            
            logger.debug(f"🔄 Deleted checkpoint {checkpoint_id} ({deleted_count} keys)")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")
            return False

    def clear_thread_checkpoints(self, thread_id: str) -> int:
        """Clear all checkpoints for a thread"""
        try:
            thread_key = f"{self.thread_prefix}{thread_id}"
            
            # Get all checkpoint IDs for this thread
            checkpoint_ids = self.memory_store.redis_client.zrange(thread_key, 0, -1)
            
            deleted_count = 0
            for checkpoint_id in checkpoint_ids:
                if self.delete_checkpoint(checkpoint_id):
                    deleted_count += 1
            
            # Clear the thread index
            self.memory_store.redis_client.delete(thread_key)
            
            logger.info(f"🔄 Cleared {deleted_count} checkpoints for thread {thread_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to clear thread checkpoints: {e}")
            return 0

    def get_checkpoint_metadata(self, checkpoint_id: str) -> Optional[Dict]:
        """Get metadata for a checkpoint without loading full data"""
        try:
            metadata_key = f"{self.metadata_prefix}{checkpoint_id}"
            metadata_json = self.memory_store.redis_client.get(metadata_key)
            
            if metadata_json:
                metadata = json.loads(metadata_json)
                logger.debug(f"🔄 Retrieved metadata for checkpoint {checkpoint_id}")
                return metadata
            
            # Fallback to loading full checkpoint
            checkpoint_data = self.load_checkpoint(checkpoint_id)
            if checkpoint_data:
                return checkpoint_data.get('metadata', {})
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get checkpoint metadata: {e}")
            return None

    def search_checkpoints(self, query: str, limit: int = 10) -> List[Dict]:
        """Search checkpoints by content"""
        try:
            # This is a simplified search - in production, you might want
            # to use Redis search modules or maintain search indices
            
            results = []
            
            # Get all checkpoint keys
            pattern = f"{self.checkpoint_prefix}*"
            checkpoint_keys = self.memory_store.redis_client.keys(pattern)
            
            for key in checkpoint_keys[:limit * 2]:  # Search more than limit
                try:
                    checkpoint_json = self.memory_store.redis_client.get(key)
                    if checkpoint_json:
                        checkpoint_data = json.loads(checkpoint_json)
                        
                        # Simple text search in checkpoint data
                        checkpoint_str = json.dumps(checkpoint_data).lower()
                        if query.lower() in checkpoint_str:
                            results.append(checkpoint_data)
                            
                            if len(results) >= limit:
                                break
                                
                except (json.JSONDecodeError, Exception):
                    continue
            
            logger.debug(f"🔄 Found {len(results)} checkpoints matching query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search checkpoints: {e}")
            return []

    def get_thread_statistics(self, thread_id: str) -> Dict:
        """Get statistics for a thread"""
        try:
            thread_key = f"{self.thread_prefix}{thread_id}"
            
            # Get checkpoint count
            checkpoint_count = self.memory_store.redis_client.zcard(thread_key)
            
            # Get first and last checkpoint timestamps
            first_checkpoint = None
            last_checkpoint = None
            
            if checkpoint_count > 0:
                # Get oldest checkpoint
                oldest_ids = self.memory_store.redis_client.zrange(thread_key, 0, 0)
                if oldest_ids:
                    oldest_checkpoint = self.load_checkpoint(oldest_ids[0])
                    if oldest_checkpoint:
                        first_checkpoint = oldest_checkpoint.get('timestamp')
                
                # Get newest checkpoint
                newest_ids = self.memory_store.redis_client.zrevrange(thread_key, 0, 0)
                if newest_ids:
                    newest_checkpoint = self.load_checkpoint(newest_ids[0])
                    if newest_checkpoint:
                        last_checkpoint = newest_checkpoint.get('timestamp')
            
            stats = {
                'thread_id': thread_id,
                'checkpoint_count': checkpoint_count,
                'first_checkpoint': first_checkpoint,
                'last_checkpoint': last_checkpoint,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.debug(f"🔄 Generated statistics for thread {thread_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get thread statistics: {e}")
            return {'error': str(e)}

    def _generate_checkpoint_id(self, thread_id: str) -> str:
        """Generate a unique checkpoint ID"""
        timestamp = datetime.utcnow().isoformat()
        unique_string = f"{thread_id}_{timestamp}_{os.urandom(8).hex()}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def health_check(self) -> Dict:
        """Check LangGraph Redis checkpointer health"""
        try:
            redis_health = self.memory_store.health_check()
            
            # Test checkpoint operations
            test_thread_id = "health_check_test"
            test_checkpoint_data = {
                'state': {'test': True},
                'step': 1,
                'timestamp': datetime.utcnow().isoformat()
            }
            test_metadata = {'test': True, 'health_check': True}
            
            # Test save and load
            checkpoint_id = self.save_checkpoint(test_thread_id, test_checkpoint_data, test_metadata)
            load_success = self.load_checkpoint(checkpoint_id) is not None if checkpoint_id else False
            
            # Cleanup test data
            if checkpoint_id:
                self.delete_checkpoint(checkpoint_id)
            self.clear_thread_checkpoints(test_thread_id)
            
            langgraph_health = {
                'component': 'langgraph_redis_checkpointer',
                'redis_connection': redis_health.get('status') == 'healthy',
                'checkpoint_operations': checkpoint_id is not None and load_success,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'redis_health': redis_health,
                'langgraph_health': langgraph_health,
                'overall_status': 'healthy' if langgraph_health['checkpoint_operations'] else 'unhealthy'
            }
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class LangGraphMemoryManager:
    """
    High-level memory manager for LangGraph agents
    Combines checkpointing with conversation memory
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.checkpointer = LangGraphRedisCheckpointer(config)
        self.memory_store = self.checkpointer.memory_store
        self.agent_id = "langgraph_agent"
        
    def save_agent_state(self, thread_id: str, state: Dict, metadata: Optional[Dict] = None) -> str:
        """Save complete agent state including memory"""
        try:
            # Get current conversation history
            conversation_history = self.memory_store.get_conversation_history(self.agent_id, limit=20)
            
            # Combine state with conversation memory
            complete_state = {
                'agent_state': state,
                'conversation_history': conversation_history,
                'memory_context': {
                    'thread_id': thread_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            # Save as checkpoint
            checkpoint_id = self.checkpointer.save_checkpoint(thread_id, complete_state, metadata)
            
            # Also store in conversation memory
            if checkpoint_id:
                conversation_data = {
                    'type': 'state_checkpoint',
                    'checkpoint_id': checkpoint_id,
                    'thread_id': thread_id,
                    'state_summary': str(state)[:200]
                }
                self.memory_store.store_conversation(self.agent_id, conversation_data)
            
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to save agent state: {e}")
            return None
    
    def restore_agent_state(self, checkpoint_id: str) -> Optional[Dict]:
        """Restore complete agent state including memory"""
        try:
            restored_data = self.checkpointer.restore_from_checkpoint(checkpoint_id)
            
            if restored_data:
                state_data = restored_data.get('state', {})
                agent_state = state_data.get('agent_state', {})
                conversation_history = state_data.get('conversation_history', [])
                
                # Restore conversation history to memory
                for conversation in conversation_history:
                    self.memory_store.store_conversation(self.agent_id, conversation.get('data', {}))
                
                return {
                    'agent_state': agent_state,
                    'restored_conversations': len(conversation_history),
                    'checkpoint_metadata': restored_data.get('metadata', {}),
                    'thread_id': restored_data.get('thread_id'),
                    'timestamp': restored_data.get('timestamp')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to restore agent state: {e}")
            return None
    
    def get_memory_context(self, thread_id: str) -> Dict:
        """Get comprehensive memory context for a thread"""
        try:
            # Get latest checkpoint
            latest_checkpoint = self.checkpointer.get_latest_checkpoint(thread_id)
            
            # Get conversation history
            conversation_history = self.memory_store.get_conversation_history(self.agent_id, limit=10)
            
            # Get thread statistics
            thread_stats = self.checkpointer.get_thread_statistics(thread_id)
            
            # Get recent decisions
            recent_decisions = self.memory_store.get_recent_decisions(self.agent_id, limit=5)
            
            return {
                'thread_id': thread_id,
                'latest_checkpoint': latest_checkpoint,
                'conversation_history': conversation_history,
                'thread_statistics': thread_stats,
                'recent_decisions': recent_decisions,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory context: {e}")
            return {'error': str(e)}


# Helper functions for LangGraph integration

def create_redis_checkpointer(config: Dict) -> LangGraphRedisCheckpointer:
    """Create a Redis checkpointer for LangGraph"""
    return LangGraphRedisCheckpointer(config)

def create_memory_manager(config: Dict) -> LangGraphMemoryManager:
    """Create a complete memory manager for LangGraph agents"""
    return LangGraphMemoryManager(config)

def checkpoint_decorator(checkpointer: LangGraphRedisCheckpointer, thread_id: str):
    """Decorator to automatically checkpoint function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Create checkpoint data
                checkpoint_data = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # Truncate for storage
                    'kwargs': str(kwargs)[:200],
                    'result': str(result)[:500],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Save checkpoint
                checkpoint_id = checkpointer.save_checkpoint(
                    thread_id, 
                    checkpoint_data,
                    {'function': func.__name__, 'auto_checkpoint': True}
                )
                
                logger.debug(f"🔄 Auto-checkpointed function {func.__name__}: {checkpoint_id}")
                
                return result
                
            except Exception as e:
                # Checkpoint the error as well
                error_data = {
                    'function': func.__name__,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                checkpointer.save_checkpoint(
                    thread_id,
                    error_data,
                    {'function': func.__name__, 'error': True}
                )
                
                raise
        
        return wrapper
    return decorator

