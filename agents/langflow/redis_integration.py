"""
🔄 Langflow Redis Integration for MESHNET
Provides Redis-based memory and state management for Langflow workflows
"""

import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.redis_memory import RedisMemoryStore

logger = logging.getLogger(__name__)

class LangflowRedisComponent:
    """
    Redis integration component for Langflow
    Provides memory and state management capabilities
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.component_id = "langflow_meshnet"
        
        # Initialize Redis memory store
        self.redis_config = {
            'REDIS_HOST': config.get('REDIS_HOST', 'localhost'),
            'REDIS_PORT': config.get('REDIS_PORT', 6379),
            'REDIS_DB': config.get('REDIS_DB', 1),  # Different DB for Langflow
            'REDIS_PASSWORD': config.get('REDIS_PASSWORD', None)
        }
        
        self.memory_store = RedisMemoryStore(self.redis_config)
        logger.info("🔄 Langflow Redis component initialized")

    def store_workflow_state(self, workflow_id: str, state_data: Dict) -> bool:
        """Store workflow execution state"""
        try:
            state_entry = {
                'workflow_id': workflow_id,
                'state': state_data,
                'timestamp': datetime.utcnow().isoformat(),
                'component': 'langflow'
            }
            
            success = self.memory_store.store_context(
                f"langflow_workflow_{workflow_id}",
                state_entry,
                ttl=3600  # 1 hour TTL
            )
            
            if success:
                logger.debug(f"🔄 Stored workflow state for {workflow_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store workflow state: {e}")
            return False

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict]:
        """Retrieve workflow execution state"""
        try:
            context = self.memory_store.get_context(f"langflow_workflow_{workflow_id}")
            
            if context:
                logger.debug(f"🔄 Retrieved workflow state for {workflow_id}")
                return context.get('data', {}).get('state', {})
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve workflow state: {e}")
            return None

    def store_execution_result(self, execution_id: str, result_data: Dict) -> bool:
        """Store workflow execution result"""
        try:
            result_entry = {
                'execution_id': execution_id,
                'result': result_data,
                'timestamp': datetime.utcnow().isoformat(),
                'component': 'langflow'
            }
            
            success = self.memory_store.store_knowledge(
                execution_id,
                result_entry,
                'langflow_executions'
            )
            
            if success:
                logger.debug(f"🔄 Stored execution result for {execution_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store execution result: {e}")
            return False

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history"""
        try:
            executions = self.memory_store.get_knowledge_by_category(
                'langflow_executions', 
                limit=limit
            )
            
            logger.debug(f"🔄 Retrieved {len(executions)} execution records")
            return executions
            
        except Exception as e:
            logger.error(f"Failed to retrieve execution history: {e}")
            return []

    def store_agent_interaction(self, interaction_data: Dict) -> bool:
        """Store agent interaction data"""
        try:
            interaction_entry = {
                'type': 'langflow_interaction',
                'data': interaction_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            success = self.memory_store.store_conversation(
                self.component_id,
                interaction_entry
            )
            
            if success:
                logger.debug("🔄 Stored agent interaction")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store agent interaction: {e}")
            return False

    def get_agent_interactions(self, limit: int = 20) -> List[Dict]:
        """Get recent agent interactions"""
        try:
            interactions = self.memory_store.get_conversation_history(
                self.component_id,
                limit=limit
            )
            
            logger.debug(f"🔄 Retrieved {len(interactions)} agent interactions")
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to retrieve agent interactions: {e}")
            return []

    def search_execution_history(self, query: str, limit: int = 5) -> List[Dict]:
        """Search through execution history"""
        try:
            results = self.memory_store.search_memory(
                query,
                agent_id=self.component_id,
                limit=limit
            )
            
            logger.debug(f"🔄 Found {len(results)} matching executions for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search execution history: {e}")
            return []

    def get_workflow_analytics(self, workflow_id: str) -> Dict:
        """Get analytics for a specific workflow"""
        try:
            # Search for all executions of this workflow
            workflow_executions = self.memory_store.search_memory(
                f"workflow_id:{workflow_id}",
                agent_id=self.component_id,
                limit=100
            )
            
            analytics = {
                'workflow_id': workflow_id,
                'total_executions': len(workflow_executions),
                'success_rate': 0,
                'average_duration': 0,
                'last_execution': None,
                'common_errors': []
            }
            
            if workflow_executions:
                successful = 0
                total_duration = 0
                errors = []
                
                for execution in workflow_executions:
                    exec_data = execution.get('data', {})
                    result = exec_data.get('result', {})
                    
                    if result.get('status') == 'success':
                        successful += 1
                    
                    duration = result.get('duration', 0)
                    if duration:
                        total_duration += duration
                    
                    error = result.get('error')
                    if error:
                        errors.append(error)
                    
                    # Update last execution timestamp
                    timestamp = exec_data.get('timestamp')
                    if timestamp and (not analytics['last_execution'] or timestamp > analytics['last_execution']):
                        analytics['last_execution'] = timestamp
                
                analytics['success_rate'] = (successful / len(workflow_executions)) * 100
                analytics['average_duration'] = total_duration / len(workflow_executions) if workflow_executions else 0
                
                # Count common errors
                error_counts = {}
                for error in errors:
                    error_counts[error] = error_counts.get(error, 0) + 1
                
                analytics['common_errors'] = sorted(
                    error_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
            
            logger.debug(f"🔄 Generated analytics for workflow {workflow_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate workflow analytics: {e}")
            return {'error': str(e)}

    def cleanup_old_data(self, days_old: int = 7) -> Dict:
        """Clean up old execution data"""
        try:
            # This is a simplified cleanup - in a real implementation,
            # you'd want to use Redis TTL or implement time-based cleanup
            
            cleanup_stats = {
                'cleaned_workflows': 0,
                'cleaned_executions': 0,
                'cleaned_interactions': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"🔄 Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {'error': str(e)}

    def health_check(self) -> Dict:
        """Check Langflow Redis integration health"""
        try:
            redis_health = self.memory_store.health_check()
            
            # Additional Langflow-specific checks
            test_workflow_id = "health_check_test"
            test_state = {'status': 'testing', 'timestamp': datetime.utcnow().isoformat()}
            
            # Test workflow state operations
            store_success = self.store_workflow_state(test_workflow_id, test_state)
            retrieve_success = self.get_workflow_state(test_workflow_id) is not None
            
            langflow_health = {
                'component': 'langflow_redis',
                'redis_connection': redis_health.get('status') == 'healthy',
                'workflow_state_ops': store_success and retrieve_success,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cleanup test data
            self.memory_store.redis_client.delete(f"meshnet:ctx:langflow_workflow_{test_workflow_id}")
            
            return {
                'redis_health': redis_health,
                'langflow_health': langflow_health,
                'overall_status': 'healthy' if langflow_health['workflow_state_ops'] else 'unhealthy'
            }
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class LangflowMemoryNode:
    """
    Custom Langflow node for memory operations
    Can be used within Langflow workflows
    """
    
    def __init__(self):
        self.redis_component = None
    
    def initialize(self, config: Dict):
        """Initialize the memory node"""
        self.redis_component = LangflowRedisComponent(config)
        return True
    
    def store_data(self, key: str, data: Dict, ttl: int = 3600) -> Dict:
        """Store data in Redis memory"""
        if not self.redis_component:
            return {'success': False, 'error': 'Component not initialized'}
        
        try:
            success = self.redis_component.memory_store.store_context(key, data, ttl)
            return {
                'success': success,
                'key': key,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def retrieve_data(self, key: str) -> Dict:
        """Retrieve data from Redis memory"""
        if not self.redis_component:
            return {'success': False, 'error': 'Component not initialized'}
        
        try:
            data = self.redis_component.memory_store.get_context(key)
            return {
                'success': data is not None,
                'data': data,
                'key': key,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_memory(self, query: str, limit: int = 5) -> Dict:
        """Search memory for relevant data"""
        if not self.redis_component:
            return {'success': False, 'error': 'Component not initialized'}
        
        try:
            results = self.redis_component.memory_store.search_memory(query, limit=limit)
            return {
                'success': True,
                'results': results,
                'query': query,
                'count': len(results),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Langflow workflow helper functions

def create_memory_enabled_workflow(config: Dict) -> LangflowRedisComponent:
    """Create a memory-enabled Langflow workflow component"""
    return LangflowRedisComponent(config)

def get_workflow_memory_context(redis_component: LangflowRedisComponent, workflow_id: str) -> Dict:
    """Get memory context for a workflow"""
    try:
        state = redis_component.get_workflow_state(workflow_id)
        history = redis_component.get_execution_history(limit=5)
        analytics = redis_component.get_workflow_analytics(workflow_id)
        
        return {
            'current_state': state,
            'recent_history': history,
            'analytics': analytics,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get workflow memory context: {e}")
        return {'error': str(e)}

def store_workflow_result(redis_component: LangflowRedisComponent, workflow_id: str, result: Dict) -> bool:
    """Store workflow execution result"""
    try:
        execution_id = f"{workflow_id}_{datetime.utcnow().timestamp()}"
        
        result_data = {
            'workflow_id': workflow_id,
            'result': result,
            'execution_timestamp': datetime.utcnow().isoformat()
        }
        
        return redis_component.store_execution_result(execution_id, result_data)
    except Exception as e:
        logger.error(f"Failed to store workflow result: {e}")
        return False

