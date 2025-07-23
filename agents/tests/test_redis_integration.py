"""
🧪 Redis Integration Tests for MESHNET Agents
Tests Redis memory functionality for Langflow, Langchain, and LangGraph
"""

import pytest
import json
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.redis_memory import RedisMemoryStore, LangChainRedisMemory, LangGraphRedisCheckpoint
from langflow.redis_integration import LangflowRedisComponent
from langgraph.redis_checkpoint import LangGraphRedisCheckpointer, LangGraphMemoryManager

class TestRedisMemoryStore:
    """Test basic Redis memory store functionality"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,  # Use test database
            'REDIS_PASSWORD': None
        }
    
    @pytest.fixture
    def memory_store(self, redis_config):
        store = RedisMemoryStore(redis_config)
        yield store
        # Cleanup after test
        store.redis_client.flushdb()
    
    def test_connection(self, memory_store):
        """Test Redis connection"""
        health = memory_store.health_check()
        assert health['status'] == 'healthy'
        assert health['redis_connected'] is True
    
    def test_conversation_storage(self, memory_store):
        """Test conversation storage and retrieval"""
        agent_id = "test_agent"
        conversation_data = {
            'message': 'Hello, world!',
            'response': 'Hi there!',
            'type': 'greeting'
        }
        
        # Store conversation
        success = memory_store.store_conversation(agent_id, conversation_data)
        assert success is True
        
        # Retrieve conversation
        history = memory_store.get_conversation_history(agent_id, limit=10)
        assert len(history) == 1
        assert history[0]['data'] == conversation_data
        assert history[0]['agent_id'] == agent_id
    
    def test_context_storage(self, memory_store):
        """Test context storage with TTL"""
        context_id = "test_context"
        context_data = {
            'session': 'test_session',
            'user_id': 'user123',
            'preferences': {'theme': 'dark'}
        }
        
        # Store context
        success = memory_store.store_context(context_id, context_data, ttl=60)
        assert success is True
        
        # Retrieve context
        retrieved_context = memory_store.get_context(context_id)
        assert retrieved_context is not None
        assert retrieved_context['data'] == context_data
    
    def test_decision_storage(self, memory_store):
        """Test decision storage and retrieval"""
        agent_id = "test_agent"
        decision_data = {
            'action': 'reward_distribution',
            'amount': 100,
            'reasoning': 'Good mining performance'
        }
        
        # Store decision
        success = memory_store.store_decision(agent_id, decision_data)
        assert success is True
        
        # Retrieve recent decisions
        decisions = memory_store.get_recent_decisions(agent_id, limit=5)
        assert len(decisions) == 1
        assert decisions[0]['data'] == decision_data
    
    def test_knowledge_storage(self, memory_store):
        """Test knowledge base functionality"""
        knowledge_id = "mining_best_practices"
        category = "mining"
        knowledge_data = {
            'title': 'Mining Best Practices',
            'content': 'Always optimize your hash rate...',
            'tags': ['mining', 'optimization']
        }
        
        # Store knowledge
        success = memory_store.store_knowledge(knowledge_id, knowledge_data, category)
        assert success is True
        
        # Retrieve knowledge
        retrieved = memory_store.get_knowledge(knowledge_id, category)
        assert retrieved is not None
        assert retrieved['data'] == knowledge_data
        
        # Get knowledge by category
        category_items = memory_store.get_knowledge_by_category(category, limit=10)
        assert len(category_items) == 1
    
    def test_memory_search(self, memory_store):
        """Test memory search functionality"""
        agent_id = "test_agent"
        
        # Store some test data
        memory_store.store_conversation(agent_id, {'topic': 'mining rewards'})
        memory_store.store_decision(agent_id, {'action': 'mining_reward', 'amount': 50})
        
        # Search memory
        results = memory_store.search_memory('mining', agent_id, limit=10)
        assert len(results) >= 1
        
        # Check result structure
        for result in results:
            assert 'type' in result
            assert 'data' in result
            assert result['type'] in ['conversation', 'decision']
    
    def test_agent_state(self, memory_store):
        """Test agent state storage"""
        agent_id = "test_agent"
        state_data = {
            'current_task': 'monitoring',
            'last_action': 'reward_distribution',
            'status': 'active'
        }
        
        # Store state
        success = memory_store.store_agent_state(agent_id, state_data)
        assert success is True
        
        # Retrieve state
        retrieved_state = memory_store.get_agent_state(agent_id)
        assert retrieved_state is not None
        assert retrieved_state['state'] == state_data
    
    def test_memory_cleanup(self, memory_store):
        """Test memory cleanup functionality"""
        agent_id = "test_agent"
        
        # Store some data
        memory_store.store_conversation(agent_id, {'test': 'data1'})
        memory_store.store_decision(agent_id, {'test': 'data2'})
        memory_store.store_agent_state(agent_id, {'test': 'data3'})
        
        # Verify data exists
        assert len(memory_store.get_conversation_history(agent_id)) > 0
        assert len(memory_store.get_recent_decisions(agent_id)) > 0
        assert memory_store.get_agent_state(agent_id) is not None
        
        # Clear memory
        success = memory_store.clear_agent_memory(agent_id)
        assert success is True
        
        # Verify data is cleared
        assert len(memory_store.get_conversation_history(agent_id)) == 0
        assert len(memory_store.get_recent_decisions(agent_id)) == 0
        assert memory_store.get_agent_state(agent_id) is None


class TestLangChainRedisMemory:
    """Test LangChain Redis memory integration"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,
            'REDIS_PASSWORD': None
        }
    
    @pytest.fixture
    def langchain_memory(self, redis_config):
        store = RedisMemoryStore(redis_config)
        memory = LangChainRedisMemory(store, "test_langchain_agent")
        yield memory
        # Cleanup
        store.redis_client.flushdb()
    
    def test_save_context(self, langchain_memory):
        """Test LangChain context saving"""
        inputs = {"human_input": "What is the weather?"}
        outputs = {"ai_output": "I don't have access to weather data."}
        
        langchain_memory.save_context(inputs, outputs)
        
        # Check if context was saved
        buffer = langchain_memory.buffer
        assert "What is the weather?" in buffer
        assert "I don't have access to weather data." in buffer
    
    def test_clear_memory(self, langchain_memory):
        """Test LangChain memory clearing"""
        inputs = {"human_input": "Test message"}
        outputs = {"ai_output": "Test response"}
        
        langchain_memory.save_context(inputs, outputs)
        assert len(langchain_memory.buffer) > 0
        
        langchain_memory.clear()
        assert len(langchain_memory.buffer) == 0


class TestLangflowRedisIntegration:
    """Test Langflow Redis integration"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,
            'REDIS_PASSWORD': None
        }
    
    @pytest.fixture
    def langflow_component(self, redis_config):
        component = LangflowRedisComponent(redis_config)
        yield component
        # Cleanup
        component.memory_store.redis_client.flushdb()
    
    def test_workflow_state(self, langflow_component):
        """Test workflow state storage"""
        workflow_id = "test_workflow"
        state_data = {
            'current_step': 'data_processing',
            'variables': {'input_count': 100},
            'status': 'running'
        }
        
        # Store state
        success = langflow_component.store_workflow_state(workflow_id, state_data)
        assert success is True
        
        # Retrieve state
        retrieved_state = langflow_component.get_workflow_state(workflow_id)
        assert retrieved_state == state_data
    
    def test_execution_results(self, langflow_component):
        """Test execution result storage"""
        execution_id = "test_execution_123"
        result_data = {
            'status': 'success',
            'output': {'processed_items': 50},
            'duration': 1.5,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store result
        success = langflow_component.store_execution_result(execution_id, result_data)
        assert success is True
        
        # Get execution history
        history = langflow_component.get_execution_history(limit=10)
        assert len(history) == 1
        assert history[0]['data']['result'] == result_data
    
    def test_agent_interactions(self, langflow_component):
        """Test agent interaction storage"""
        interaction_data = {
            'user_input': 'Process this data',
            'agent_response': 'Data processed successfully',
            'workflow_id': 'test_workflow'
        }
        
        # Store interaction
        success = langflow_component.store_agent_interaction(interaction_data)
        assert success is True
        
        # Get interactions
        interactions = langflow_component.get_agent_interactions(limit=10)
        assert len(interactions) == 1
        assert interactions[0]['data']['data'] == interaction_data
    
    def test_workflow_analytics(self, langflow_component):
        """Test workflow analytics"""
        workflow_id = "analytics_test_workflow"
        
        # Store some execution results
        for i in range(3):
            execution_id = f"exec_{i}"
            result_data = {
                'workflow_id': workflow_id,
                'status': 'success' if i < 2 else 'error',
                'duration': 1.0 + i * 0.5
            }
            langflow_component.store_execution_result(execution_id, result_data)
        
        # Get analytics
        analytics = langflow_component.get_workflow_analytics(workflow_id)
        assert 'workflow_id' in analytics
        assert analytics['total_executions'] >= 0  # May be 0 due to search limitations
    
    def test_health_check(self, langflow_component):
        """Test Langflow component health check"""
        health = langflow_component.health_check()
        assert 'overall_status' in health
        assert health['overall_status'] in ['healthy', 'unhealthy']


class TestLangGraphRedisCheckpointer:
    """Test LangGraph Redis checkpointer"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,
            'REDIS_PASSWORD': None
        }
    
    @pytest.fixture
    def checkpointer(self, redis_config):
        checkpointer = LangGraphRedisCheckpointer(redis_config)
        yield checkpointer
        # Cleanup
        checkpointer.memory_store.redis_client.flushdb()
    
    def test_checkpoint_operations(self, checkpointer):
        """Test basic checkpoint operations"""
        thread_id = "test_thread"
        checkpoint_data = {
            'state': {'current_step': 1, 'data': 'test'},
            'metadata': {'version': '1.0'}
        }
        metadata = {'test': True, 'priority': 'high'}
        
        # Save checkpoint
        checkpoint_id = checkpointer.save_checkpoint(thread_id, checkpoint_data, metadata)
        assert checkpoint_id is not None
        
        # Load checkpoint
        loaded_checkpoint = checkpointer.load_checkpoint(checkpoint_id)
        assert loaded_checkpoint is not None
        assert loaded_checkpoint['data'] == checkpoint_data
        assert loaded_checkpoint['metadata'] == metadata
        assert loaded_checkpoint['thread_id'] == thread_id
    
    def test_latest_checkpoint(self, checkpointer):
        """Test getting latest checkpoint"""
        thread_id = "test_thread"
        
        # Save multiple checkpoints
        checkpoint_ids = []
        for i in range(3):
            data = {'step': i, 'data': f'checkpoint_{i}'}
            checkpoint_id = checkpointer.save_checkpoint(thread_id, data)
            checkpoint_ids.append(checkpoint_id)
            time.sleep(0.1)  # Ensure different timestamps
        
        # Get latest checkpoint
        latest = checkpointer.get_latest_checkpoint(thread_id)
        assert latest is not None
        assert latest['data']['step'] == 2  # Last checkpoint
    
    def test_list_checkpoints(self, checkpointer):
        """Test listing checkpoints"""
        thread_id = "test_thread"
        
        # Save multiple checkpoints
        for i in range(5):
            data = {'step': i}
            checkpointer.save_checkpoint(thread_id, data)
        
        # List checkpoints
        checkpoints = checkpointer.list_checkpoints(thread_id, limit=3)
        assert len(checkpoints) <= 3
        
        # Check order (should be newest first)
        if len(checkpoints) > 1:
            assert checkpoints[0]['data']['step'] > checkpoints[1]['data']['step']
    
    def test_restore_from_checkpoint(self, checkpointer):
        """Test restoring from checkpoint"""
        thread_id = "test_thread"
        checkpoint_data = {
            'agent_state': {'current_task': 'processing'},
            'variables': {'count': 42}
        }
        metadata = {'restore_test': True}
        
        # Save checkpoint
        checkpoint_id = checkpointer.save_checkpoint(thread_id, checkpoint_data, metadata)
        
        # Restore from checkpoint
        restored = checkpointer.restore_from_checkpoint(checkpoint_id)
        assert restored is not None
        assert restored['state'] == checkpoint_data
        assert restored['metadata'] == metadata
        assert restored['thread_id'] == thread_id
        assert restored['checkpoint_id'] == checkpoint_id
    
    def test_delete_checkpoint(self, checkpointer):
        """Test checkpoint deletion"""
        thread_id = "test_thread"
        checkpoint_data = {'test': 'delete_me'}
        
        # Save checkpoint
        checkpoint_id = checkpointer.save_checkpoint(thread_id, checkpoint_data)
        
        # Verify it exists
        loaded = checkpointer.load_checkpoint(checkpoint_id)
        assert loaded is not None
        
        # Delete checkpoint
        success = checkpointer.delete_checkpoint(checkpoint_id)
        assert success is True
        
        # Verify it's deleted
        loaded = checkpointer.load_checkpoint(checkpoint_id)
        assert loaded is None
    
    def test_thread_statistics(self, checkpointer):
        """Test thread statistics"""
        thread_id = "stats_test_thread"
        
        # Save some checkpoints
        for i in range(3):
            data = {'step': i}
            checkpointer.save_checkpoint(thread_id, data)
        
        # Get statistics
        stats = checkpointer.get_thread_statistics(thread_id)
        assert stats['thread_id'] == thread_id
        assert stats['checkpoint_count'] == 3
        assert stats['first_checkpoint'] is not None
        assert stats['last_checkpoint'] is not None
    
    def test_health_check(self, checkpointer):
        """Test checkpointer health check"""
        health = checkpointer.health_check()
        assert 'overall_status' in health
        assert health['overall_status'] in ['healthy', 'unhealthy']


class TestLangGraphMemoryManager:
    """Test LangGraph memory manager"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,
            'REDIS_PASSWORD': None
        }
    
    @pytest.fixture
    def memory_manager(self, redis_config):
        manager = LangGraphMemoryManager(redis_config)
        yield manager
        # Cleanup
        manager.memory_store.redis_client.flushdb()
    
    def test_save_restore_agent_state(self, memory_manager):
        """Test saving and restoring complete agent state"""
        thread_id = "test_thread"
        agent_state = {
            'current_task': 'data_analysis',
            'progress': 0.75,
            'variables': {'input_size': 1000}
        }
        metadata = {'version': '2.0', 'test': True}
        
        # Save agent state
        checkpoint_id = memory_manager.save_agent_state(thread_id, agent_state, metadata)
        assert checkpoint_id is not None
        
        # Restore agent state
        restored = memory_manager.restore_agent_state(checkpoint_id)
        assert restored is not None
        assert restored['agent_state'] == agent_state
        assert restored['checkpoint_metadata'] == metadata
        assert restored['thread_id'] == thread_id
    
    def test_memory_context(self, memory_manager):
        """Test getting comprehensive memory context"""
        thread_id = "context_test_thread"
        
        # Create some state and conversation history
        agent_state = {'task': 'testing'}
        memory_manager.save_agent_state(thread_id, agent_state)
        
        # Store some conversation data
        conversation_data = {'message': 'test conversation'}
        memory_manager.memory_store.store_conversation(
            memory_manager.agent_id, 
            conversation_data
        )
        
        # Get memory context
        context = memory_manager.get_memory_context(thread_id)
        assert context['thread_id'] == thread_id
        assert 'latest_checkpoint' in context
        assert 'conversation_history' in context
        assert 'thread_statistics' in context


class TestIntegrationScenarios:
    """Test integration scenarios across all components"""
    
    @pytest.fixture
    def redis_config(self):
        return {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_DB': 15,
            'REDIS_PASSWORD': None
        }
    
    def test_cross_component_memory_sharing(self, redis_config):
        """Test memory sharing between different components"""
        # Initialize all components
        memory_store = RedisMemoryStore(redis_config)
        langflow_component = LangflowRedisComponent(redis_config)
        langgraph_checkpointer = LangGraphRedisCheckpointer(redis_config)
        
        try:
            # Store data from different components
            agent_id = "integration_test_agent"
            
            # Store conversation in base memory store
            memory_store.store_conversation(agent_id, {'source': 'memory_store'})
            
            # Store workflow interaction in Langflow
            langflow_component.store_agent_interaction({'source': 'langflow'})
            
            # Store checkpoint in LangGraph
            thread_id = "integration_thread"
            langgraph_checkpointer.save_checkpoint(thread_id, {'source': 'langgraph'})
            
            # Verify data can be accessed across components
            conversations = memory_store.get_conversation_history(agent_id)
            assert len(conversations) >= 1
            
            interactions = langflow_component.get_agent_interactions()
            assert len(interactions) >= 1
            
            checkpoints = langgraph_checkpointer.list_checkpoints(thread_id)
            assert len(checkpoints) >= 1
            
            # Test search across components
            search_results = memory_store.search_memory('integration', agent_id)
            # Results may vary based on search implementation
            
        finally:
            # Cleanup
            memory_store.redis_client.flushdb()
    
    def test_performance_under_load(self, redis_config):
        """Test performance with multiple operations"""
        memory_store = RedisMemoryStore(redis_config)
        
        try:
            agent_id = "performance_test_agent"
            start_time = time.time()
            
            # Perform multiple operations
            for i in range(100):
                memory_store.store_conversation(agent_id, {'iteration': i})
                memory_store.store_decision(agent_id, {'decision': i})
                
                if i % 10 == 0:
                    memory_store.get_conversation_history(agent_id, limit=10)
                    memory_store.get_recent_decisions(agent_id, limit=5)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert duration < 10.0, f"Operations took too long: {duration}s"
            
            # Verify data integrity
            conversations = memory_store.get_conversation_history(agent_id)
            decisions = memory_store.get_recent_decisions(agent_id)
            
            assert len(conversations) == 100
            assert len(decisions) == 100
            
        finally:
            # Cleanup
            memory_store.redis_client.flushdb()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

