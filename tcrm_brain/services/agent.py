import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from services.data_loader import get_dataframe
from services.tools import trend_plot_tool, prediction_tool, report_tool
import pandas as pd

# 1. Initialize Gemini
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0)

# 2. Define Wrapper Tools
def data_analysis_tool(input_str: str) -> str:
    """
    Complex tool that can handle fetch + plot/predict.
    Expected input format: "ACTION|SQL_QUERY|ARGS..."
    """
    parts = input_str.split("|")
    action = parts[0].strip().upper()
    
    try:
        if action == "QUERY":
            query = parts[1]
            df = get_dataframe(query)
            if df.empty: return "No data found."
            return df.to_string()

        elif action == "PLOT":
            # PLOT|QUERY|X_COL|Y_COL|TYPE
            if len(parts) < 4: return "Invalid arguments for PLOT."
            query = parts[1]
            x_col = parts[2]
            y_col = parts[3]
            plot_type = parts[4] if len(parts) > 4 else "line"
            
            df = get_dataframe(query)
            if df.empty: return "No data found for plotting."
            return trend_plot_tool(df, x_col, y_col, plot_type)

        elif action == "PREDICT":
            # PREDICT|QUERY|FEATURE|TARGET
            if len(parts) < 4: return "Invalid arguments for PREDICT."
            query = parts[1]
            feat = parts[2]
            target = parts[3]
            
            df = get_dataframe(query)
            if df.empty: return "No data found for prediction."
            return prediction_tool(df, feat, target)
        
        else:
            return f"Unknown action: {action}"
            
    except Exception as e:
        return f"Error processing request: {str(e)}"

tools = [
    Tool(
        name="DataAnalysis",
        func=data_analysis_tool,
        description="""
        Main tool for TCRM Brain. Use this to query data, plot charts, or make predictions.
        Input format is a pipe-separated string: "ACTION|QUERY|ARGS...".
        
        Actions:
        1. QUERY: Get raw data. Format: "QUERY|select_statement"
        2. PLOT: Generate a chart. Format: "PLOT|select_statement|x_column|y_column|chart_type"
        3. PREDICT: Predict next value. Format: "PREDICT|select_statement|feature_column|target_column"
        """
    )
]

# 3. Create the Agent using LangGraph
# Note: create_react_agent in langgraph returns a graph that can be invoked
agent_graph = create_react_agent(llm, tools)

def run_agent(query: str):
    # LangGraph expects messages
    inputs = {"messages": [("human", query)]}
    result = agent_graph.invoke(inputs)
    
    # Extract the last message content (the AI answer)
    messages = result.get("messages", [])
    if messages:
        return {"output": messages[-1].content}
    return {"output": "No response generated."}
