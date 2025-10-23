"""
Adaptador Redis para persistência de dados.
"""
import json
from typing import Optional, List
import redis.asyncio as redis
from loguru import logger
from ....core.application.ports.outbound.persistence_port import PersistencePort
from ....core.domain.models import Message, Task, ConversationContext
from ....config.settings import settings


class RedisAdapter(PersistencePort):
    """Adaptador Redis para persistência."""
    
    def __init__(self):
        self.redis_client = None
        
    async def _get_client(self) -> redis.Redis:
        """Obtém cliente Redis."""
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
        return self.redis_client
    
    async def save_conversation(self, conversation: ConversationContext) -> None:
        """Salva uma conversação no Redis."""
        try:
            client = await self._get_client()
            key = f"conversation:{conversation.id}"
            data = conversation.model_dump_json()
            
            # Salva com TTL de 24 horas
            await client.setex(key, 86400, data)
            logger.debug(f"Conversation saved: {conversation.id}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Recupera uma conversação do Redis."""
        try:
            client = await self._get_client()
            key = f"conversation:{conversation_id}"
            data = await client.get(key)
            
            if data:
                return ConversationContext.model_validate_json(data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    async def save_message(self, message: Message) -> None:
        """Salva uma mensagem no Redis."""
        try:
            client = await self._get_client()
            
            # Salva mensagem individual
            message_key = f"message:{message.id}"
            await client.setex(message_key, 86400, message.model_dump_json())
            
            # Adiciona à lista de mensagens da conversação (se especificada nos metadados)
            if "conversation_id" in message.metadata:
                conversation_id = message.metadata["conversation_id"]
                conversation_messages_key = f"conversation_messages:{conversation_id}"
                await client.lpush(conversation_messages_key, message.id)
                await client.expire(conversation_messages_key, 86400)
            
            logger.debug(f"Message saved: {message.id}")
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    async def get_messages(self, conversation_id: str) -> List[Message]:
        """Recupera mensagens de uma conversação."""
        try:
            client = await self._get_client()
            messages_key = f"conversation_messages:{conversation_id}"
            
            # Obtém IDs das mensagens
            message_ids = await client.lrange(messages_key, 0, -1)
            
            messages = []
            for message_id in message_ids:
                message_key = f"message:{message_id}"
                message_data = await client.get(message_key)
                if message_data:
                    message = Message.model_validate_json(message_data)
                    messages.append(message)
            
            # Retorna em ordem cronológica
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def save_task(self, task: Task) -> None:
        """Salva uma tarefa no Redis."""
        try:
            client = await self._get_client()
            key = f"task:{task.id}"
            data = task.model_dump_json()
            
            # Salva tarefa
            await client.setex(key, 3600, data)  # TTL de 1 hora
            
            # Adiciona à lista de tarefas por status
            status_key = f"tasks:{task.status}"
            await client.sadd(status_key, task.id)
            await client.expire(status_key, 3600)
            
            logger.debug(f"Task saved: {task.id}")
            
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera uma tarefa do Redis."""
        try:
            client = await self._get_client()
            key = f"task:{task_id}"
            data = await client.get(key)
            
            if data:
                return Task.model_validate_json(data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None
    
    async def update_task(self, task: Task) -> None:
        """Atualiza uma tarefa no Redis."""
        try:
            client = await self._get_client()
            
            # Remove da lista do status anterior se existir
            old_task = await self.get_task(task.id)
            if old_task and old_task.status != task.status:
                old_status_key = f"tasks:{old_task.status}"
                await client.srem(old_status_key, task.id)
            
            # Salva tarefa atualizada
            await self.save_task(task)
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise
    
    async def close(self) -> None:
        """Fecha conexão Redis."""
        if self.redis_client:
            await self.redis_client.aclose()