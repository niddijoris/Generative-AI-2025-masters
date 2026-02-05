"""
AI Agent - OpenAI-powered assistant with function calling
"""
import json
from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from agent.tools import AgentTools


class AIAgent:
    """AI Agent powered by OpenAI with function calling capabilities"""
    
    SYSTEM_PROMPT = """You are a helpful data analyst assistant for a car auction/pricing database. 
Your role is to help users understand and query car pricing data.

IMPORTANT GUIDELINES:
1. **Data Privacy**: Never pass the entire dataset to your responses. Only use the tools to query specific data.
2. **Safety**: You can only execute SELECT queries. Any attempt to modify data (DELETE, UPDATE, INSERT, DROP) will be blocked.
3. **Tool Usage**: 
   - Use `query_database` for specific data queries
   - Use `get_database_statistics` for general overviews and statistics
   - Use `generate_chart` when the user asks for a chart, visualization, or trend analysis. Choose the most appropriate chart type (bar, column, line, pie, scatter).
   - Use `create_support_ticket` when you cannot help or user requests human assistance
4. **Support Escalation**: If you cannot answer a question or the user seems frustrated, proactively suggest creating a support ticket.
5. **Clear Communication**: Explain your findings clearly with relevant numbers and insights.

DATABASE SCHEMA:
- Table: cars
- Columns: year, make, model, trim, body, transmission, vin, state, condition, odometer, color, interior, seller, mmr, sellingprice, saledate

Be concise, helpful, and data-driven in your responses."""
    
    def __init__(self, tools: AgentTools):
        self.tools = tools
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.logger = logging.getLogger(__name__)
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize with system prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.SYSTEM_PROMPT
        })
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and return AI response with metadata
        
        Args:
            user_message: User's question or request
            
        Returns:
            Dictionary with 'content' (str) and optional 'chart' (dict)
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get AI response with function calling
            return self._get_ai_response()
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.logger.error(error_msg)
            return {
                "content": f"❌ {error_msg}",
                "chart": None
            }
    
    def _get_ai_response(self, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Get AI response with function calling loop
        
        Args:
            max_iterations: Maximum number of function calling iterations
            
        Returns:
            Dictionary with 'content' and optional 'chart'
        """
        iteration = 0
        last_chart = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=AgentTools.get_tool_definitions(),
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Check if AI wants to call a function
            if message.tool_calls:
                # Add assistant message to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    self.logger.info(f"AI calling function: {function_name}")
                    
                    # Execute the tool
                    result = self.tools.execute_tool(function_name, function_args)
                    
                    # Capture chart result if it's a chart
                    if result.get('is_chart'):
                        last_chart = result.get('chart_config')
                    
                    # Add function result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                # Continue loop to get final response
                continue
            
            else:
                # No more function calls, return final response
                final_response = message.content or "I apologize, but I couldn't generate a response."
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                
                return {
                    "content": final_response,
                    "chart": last_chart
                }
        
        # Max iterations reached
        return {
            "content": "I apologize, but I'm having trouble processing your request. Would you like me to create a support ticket for human assistance?",
            "chart": None
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [{
            "role": "system",
            "content": self.SYSTEM_PROMPT
        }]
        self.logger.info("Conversation history reset")
    
    def get_conversation_context(self) -> str:
        """Get conversation history as formatted string for support tickets"""
        context = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                context.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant" and msg.get("content"):
                context.append(f"Assistant: {msg['content']}")
        
        return "\n\n".join(context)
