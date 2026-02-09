import os
import sqlite3
import subprocess
import psutil
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("GoldenCastleAdmin")

DB_PATH = os.path.join(os.path.dirname(__file__), "bot_data.db")
DASHBOARD_SCRIPT = "dashboard.py"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
async def sql_read_query(query: str) -> str:
    """
    Execute a readonly SQL query (SELECT) on the bot database.
    Use this to inspect signals, trades, or market status.
    """
    if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper() or "INSERT" in query.upper():
        return "❌ Error: This tool only supports read-only queries (SELECT)."
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "📭 No results found."
            
        # Format as a simple text table
        columns = rows[0].keys()
        result = f"| {' | '.join(columns)} |\n| {'-' * len(' | '.join(columns))} |\n"
        
        for row in rows:
            values = [str(x) for x in row]
            result += f"| {' | '.join(values)} |\n"
            
        return result
    except Exception as e:
        return f"❌ Database Error: {str(e)}"

@mcp.tool()
async def sql_execute_command(query: str) -> str:
    """
    Execute a modification SQL command (INSERT, UPDATE, DELETE).
    ⚠️ CAUTION: This modifies the database permanently.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        changes = conn.total_changes
        conn.close()
        return f"✅ Command Executed. Rows affected: {changes}"
    except Exception as e:
        return f"❌ Database Error: {str(e)}"

@mcp.tool()
async def get_system_health() -> str:
    """Check the status of the Dashboard and Bot processes."""
    dashboard_status = "🔴 Stopped"
    bot_status = "🔴 Stopped"
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                if 'streamlit' in cmdline and DASHBOARD_SCRIPT in ' '.join(cmdline):
                    dashboard_status = f"🟢 Running (PID: {proc.info['pid']})"
                # Assuming bot is run via python directly or bat
                if 'python' in proc.info['name'] and 'bot_main.py' in ' '.join(cmdline):
                    bot_status = f"🟢 Running (PID: {proc.info['pid']})"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return f"🏰 **Golden Castle System Health**:\n- Dashboard: {dashboard_status}\n- Trading Bot: {bot_status}"

@mcp.tool()
async def restart_dashboard() -> str:
    """Restarts the Streamlit Dashboard process."""
    # Kill existing streamlit processes
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'streamlit' in cmdline and DASHBOARD_SCRIPT in ' '.join(cmdline):
                proc.kill()
                killed = True
        except:
            pass
            
    # Start new process
    try:
        subprocess.Popen(["streamlit", "run", DASHBOARD_SCRIPT], cwd=os.path.dirname(__file__), shell=True)
        return f"🔄 Dashboard Restarted. {'(Previous instance killed)' if killed else '(No active instance found)'}"
    except Exception as e:
        return f"❌ Failed to start dashboard: {str(e)}"

if __name__ == "__main__":
    mcp.run()
