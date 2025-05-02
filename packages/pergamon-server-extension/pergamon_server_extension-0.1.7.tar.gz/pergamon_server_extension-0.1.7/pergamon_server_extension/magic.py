import json
import requests
import shlex
import os
from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.display import display, HTML, Markdown
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


# Global flag to track if the magic has been loaded
__MAGIC_LOADED__ = False

# Get API host from environment variable with default fallback
API_HOST = os.environ.get("CALLIOPE_API_HOST")

@magics_class
class CalliopeMagics(Magics):
    @line_cell_magic
    def calliope(self, line, cell):
        if not cell.strip():
            return {"warning": "Empty content provided"}
        
        args = shlex.split(line) if line else []
        action = "chat"
        datasource_id = ""
        # session_id = ""
        to_ai = False
        ai_model = "gpto"

        endpoint_map = {
            # "chat": "/api/chat",
            "sql_ask": "/api/sql/ask",
            "generate_sql": "/api/sql/generate_sql",
            "run_sql": "/api/sql/run_sql",
            "followup_questions": "/api/sql/generate_followup_questions",
            "generate_summary": "/api/sql/generate_summary",
            "rag_train": "/api/rag/train",
            "update_schema": "/api/rag/update_schema/{}",
            "clear_rag": "/api/rag/clear",
        }

        i = 0
        while i < len(args):
            if i == 0 and args[i] not in ["--to-ai", "--model"]:
                action = args[i].lower()
            elif i == 1 and args[i] not in ["--to-ai", "--model"]:
                # if action in ["chat"]:
                #     session_id = args[i]
                # else:
                datasource_id = args[i]
            elif args[i] == "--to-ai":
                to_ai = True
            elif args[i] == "--model" and i + 1 < len(args):
                ai_model = args[i + 1]
                i += 1
            i += 1

        if action not in endpoint_map:
            valid_actions = ", ".join(f"'{a}'" for a in endpoint_map.keys())
            return {"error": f"Invalid action: {action}. Must be one of: {valid_actions}"}

        # if action in ["chat"] and not session_id:
        #     return {"error": f"Missing session_id. Usage: %%calliope {action} [session_id]"}
        
        if action in ["sql_ask", "generate_sql", "run_sql", "generate_summary", "rag_train", "update_schema"] and not datasource_id:
            return {"error": f"Missing datasource_id. Usage: %%calliope {action} [datasource_id]"}

        if action == "update_schema":
            endpoint = f"{API_HOST}{endpoint_map[action].format(datasource_id)}"
        else:
            endpoint = f"{API_HOST}{endpoint_map[action]}"

        payload = {}
        
        match action:
            # case "chat":
            #     payload = {
            #         "message": cell.strip(),
            #         "session_id": session_id
            #     }
            case "sql_ask":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id,
                    "generate_summary": True,
                    "generate_chart": not to_ai,
                    "generate_followups": True
                }
            case "generate_sql":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "run_sql":
                payload = {
                    "sql_query": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "followup_questions":
                try:
                    data = json.loads(cell.strip())
                    question = data.get("question")
                    sql_query = data.get("sql_query") 
                    results = data.get("results")
                    
                    if not all([question, sql_query, results]):
                        return {"error": "Cell must contain JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"}
                        
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"} 
                payload = {
                    "question": question,
                    "sql_query": sql_query,
                    "results": results
                }
            case "generate_summary":
                payload = {
                    "query_results": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "rag_train":
                try:
                    data = json.loads(cell.strip())
                    
                    if "ddl" in data and isinstance(data["ddl"], list) and all(isinstance(x, str) for x in data["ddl"]):
                        payload = {
                            "ddl": data["ddl"],
                            "datasource_id": datasource_id
                        }
                    elif "documentation" in data and isinstance(data["documentation"], list) and all(isinstance(x, str) for x in data["documentation"]):
                        payload = {
                            "documentation": data["documentation"],
                            "datasource_id": datasource_id
                        }
                    elif ("question" in data and isinstance(data["question"], list) and all(isinstance(x, str) for x in data["question"]) and
                        "sql" in data and isinstance(data["sql"], list) and all(isinstance(x, str) for x in data["sql"])):
                        payload = {
                            "question": data["question"],
                            "sql": data["sql"],
                            "datasource_id": datasource_id
                        }
                    else:
                        return {"error": "Payload must contain either ddl: string[], documentation: string[], or both question: string[] and sql: string[]"}
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON"}
            case "update_schema":
                pass
            case "clear_rag":
                pass
        
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=100
            )
            
            response.raise_for_status()
            
            try:
                result = response.json()    
                
                if to_ai:
                    ai_prompt = f"""\
                    Please interpret this response in the context of the question: {cell.strip()}. 
                    Format the response strictly as a Jupyter notebook response with the appropriate markdown.

                    ---BEGIN DATA---
                    Summary: {result.get("summary")}
                    Response: {result.get("response")}
                    Followup Questions: {", ".join(result.get("followup_questions"))}
                    SQL Query: {result.get("sql_query")}
                    ---END DATA---
                    """

                    ai_magic = f"%%ai {ai_model} --format code\n{ai_prompt}"
                    self.shell.run_cell(ai_magic)
                    return None
                else:
                    self._display_formatted_result(result, action)
                    return None
                
            except json.JSONDecodeError:
                return {"error": "API response was not valid JSON", "response_text": response.text[:200]}
                
        except requests.RequestException as e:
            error_msg = str(e)
            return {
                "error": "Failed to connect to API endpoint",
                "details": error_msg,
                "endpoint": endpoint
            }
    
    def _display_formatted_result(self, result, action):
        """Format and display the result with proper markdown and visualizations"""
        if "error" in result:
            display(HTML(f"<div style='color: red; font-weight: bold;'>Error: {result['error']}</div>"))
            if "details" in result:
                display(HTML(f"<div style='color: red;'>Details: {result['details']}</div>"))
            return
        
        markdown_output = ""
        
        if "datasource_id" in result and result["datasource_id"]:
            markdown_output += f"## Query Results: {result.get('datasource_id', '')}\n\n"
        
        if "summary" in result and result["summary"]:
            markdown_output += f"### Summary\n{result['summary']}\n\n"
        
        if "response" in result and result["response"]:
            markdown_output += f"{result['response']}\n\n"
        
        if "visualization" in result and result["visualization"]:
            display(Markdown(markdown_output))
            
            try:
                visualization = result["visualization"]
                fig = go.Figure(
                    data=visualization.get("data", []),
                    layout=visualization.get("layout", {})
                )
                
                fig.show()
                
                markdown_output = ""
            except Exception as e:
                markdown_output += f"**Error displaying visualization:** {str(e)}\n\n"
        
        if "sql_query" in result and result["sql_query"]:
            markdown_output += f"### Executed SQL\n```sql\n{result['sql_query']}\n```\n\n"
        
        if "followup_questions" in result and result["followup_questions"]:
            markdown_output += "### Suggested Follow-up Questions\n"
            for question in result["followup_questions"]:
                markdown_output += f"- {question}\n"
            markdown_output += "\n"
        
        if markdown_output:
            display(Markdown(markdown_output))

def load_ipython_extension(ipython):
    """
    Register the magic with IPython.
    This function is called when the extension is loaded.
    
    Can be manually loaded in a notebook with:
    %load_ext pergamon_server_extension
    """
    global __MAGIC_LOADED__
    
    if not __MAGIC_LOADED__:
        ipython.register_magics(CalliopeMagics)
        __MAGIC_LOADED__ = True
    else:
        pass

load_ext = load_ipython_extension 

