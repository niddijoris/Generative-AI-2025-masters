"""
AI Agent Tools - Function definitions for OpenAI function calling
"""
import json
from typing import Dict, Any, Optional
import logging

from database.db_manager import DatabaseManager
from support.github_integration import GitHubSupport


class AgentTools:
    """Tools available to the AI agent via function calling"""
    
    def __init__(self, db_manager: DatabaseManager, github_support: Optional[GitHubSupport] = None):
        self.db_manager = db_manager
        self.github_support = github_support
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def get_tool_definitions() -> list:
        """
        Get OpenAI function definitions for all available tools
        
        Returns:
            List of tool definitions in OpenAI format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_database",
                    "description": "Execute a SQL SELECT query on the car prices database. Use this to retrieve specific data based on user questions. Only SELECT queries are allowed for safety. The database contains car auction data with columns: year, make, model, trim, body, transmission, vin, state, condition, odometer, color, interior, seller, mmr, sellingprice, saledate.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                                "description": "The SQL SELECT query to execute. Must be a valid SELECT statement. Example: 'SELECT AVG(sellingprice) FROM cars WHERE make = \"BMW\"'"
                            }
                        },
                        "required": ["sql_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_database_statistics",
                    "description": "Get comprehensive statistics and aggregated information about the car prices database. Use this when user asks for general information, overview, or statistics about the data. Returns total records, price statistics, top makes/models, condition distribution, and year range.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_support_ticket",
                    "description": "Create a support ticket to reach a human for help. Use this when the user explicitly asks for human support, or when you cannot answer their question adequately. The ticket will be created as a GitHub issue.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Brief title summarizing the support request"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue or question, including conversation context"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Priority level of the support request"
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_chart",
                    "description": "Generate a dynamic chart based on a SQL query. Use this when the user asks for a chart, visualization, or comparison that would look better as a graph. You must provide a valid SQL SELECT query and chart configurations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                                "description": "SQL SELECT query to get data for the chart. Example: 'SELECT make, AVG(sellingprice) FROM cars GROUP BY make'"
                            },
                            "chart_type": {
                                "type": "string",
                                "enum": ["bar", "column", "line", "pie", "scatter"],
                                "description": "Type of chart to generate"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the chart"
                            },
                            "x_label": {
                                "type": "string",
                                "description": "Label for the X-axis (column name from query)"
                            },
                            "y_label": {
                                "type": "string",
                                "description": "Label for the Y-axis (column name from query)"
                            }
                        },
                        "required": ["sql_query", "chart_type", "title"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on function call from OpenAI
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Result dictionary from the tool execution
        """
        self.logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name == "query_database":
            return self._query_database(arguments.get("sql_query", ""))
        
        elif tool_name == "get_database_statistics":
            return self._get_database_statistics()
        
        elif tool_name == "create_support_ticket":
            return self._create_support_ticket(
                title=arguments.get("title", ""),
                description=arguments.get("description", ""),
                priority=arguments.get("priority", "medium")
            )
        
        elif tool_name == "generate_chart":
            return self._generate_chart(
                sql_query=arguments.get("sql_query", ""),
                chart_type=arguments.get("chart_type", "bar"),
                title=arguments.get("title", ""),
                x_label=arguments.get("x_label"),
                y_label=arguments.get("y_label")
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    def _query_database(self, sql_query: str) -> Dict[str, Any]:
        """Execute a database query"""
        self.logger.info(f"Executing query: {sql_query}")
        result = self.db_manager.execute_query(sql_query)
        
        # Format result for AI consumption
        if result['success']:
            # Limit data sent to AI to avoid token limits
            data = result['data']
            if len(data) > 100:
                return {
                    "success": True,
                    "message": f"Query returned {len(data)} rows (showing first 100)",
                    "data": data[:100],
                    "row_count": len(data),
                    "truncated": True
                }
            else:
                return {
                    "success": True,
                    "message": f"Query returned {len(data)} rows",
                    "data": data,
                    "row_count": len(data),
                    "truncated": False
                }
        else:
            return {
                "success": False,
                "error": result['error']
            }
    
    def _get_database_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        self.logger.info("Retrieving database statistics")
        stats = self.db_manager.get_statistics()
        
        if stats:
            return {
                "success": True,
                "statistics": stats
            }
        else:
            return {
                "success": False,
                "error": "Failed to retrieve statistics"
            }
    
    def _create_support_ticket(self, title: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a support ticket"""
        self.logger.info(f"Creating support ticket: {title}")
        
        if self.github_support:
            result = self.github_support.create_issue(
                title=title,
                body=description,
                labels=["support", f"priority-{priority}"]
            )
            return result
        else:
            # Mock support ticket if GitHub not configured
            return {
                "success": True,
                "message": "Support ticket created (mock mode - GitHub not configured)",
                "ticket_id": "MOCK-001",
                "title": title,
                "priority": priority
            }

    def _generate_chart(
        self, 
        sql_query: str, 
        chart_type: str, 
        title: str, 
        x_label: Optional[str] = None, 
        y_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute query and return chart configuration"""
        self.logger.info(f"Generating chart: {chart_type} - {title}")
        
        # Execute query first
        query_result = self._query_database(sql_query)
        
        if query_result['success']:
            data = query_result['data']
            if not data:
                return {
                    "success": False,
                    "error": "Query returned no data for the chart."
                }
            
            # Use provided labels or infer from data
            cols = list(data[0].keys())
            x_axis = x_label if x_label in cols else cols[0]
            y_axis = y_label if y_label in cols else (cols[1] if len(cols) > 1 else cols[0])
            
            return {
                "success": True,
                "is_chart": True,
                "chart_config": {
                    "type": chart_type,
                    "title": title,
                    "x_label": x_axis,
                    "y_label": y_axis,
                    "data": data
                },
                "message": f"Successfully generated {chart_type} chart: {title}"
            }
        else:
            return query_result
