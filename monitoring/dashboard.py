"""
Monitoring dashboard for SubFluxGPT.
Provides web interface for monitoring system status and metrics.
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import yaml
from datetime import datetime

from data_collector.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SubFluxGPT Monitoring Dashboard")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SubFluxGPT Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .card {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .metric {
                display: inline-block;
                margin: 10px;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                min-width: 150px;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
            }
            .metric-label {
                font-size: 14px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            .status-healthy {
                color: green;
            }
            .status-error {
                color: red;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SubFluxGPT Monitoring Dashboard</h1>
                <p>Continuous Bug Bounty Data Collection & AI Training System</p>
            </div>
            
            <div class="card">
                <h2>System Metrics</h2>
                <div class="metric">
                    <div class="metric-value" id="total-reports">-</div>
                    <div class="metric-label">Total Reports</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="total-domains">-</div>
                    <div class="metric-label">Total Domains</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="hackerone-reports">-</div>
                    <div class="metric-label">HackerOne Reports</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="bugcrowd-reports">-</div>
                    <div class="metric-label">Bugcrowd Reports</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="yeswehack-reports">-</div>
                    <div class="metric-label">YesWeHack Reports</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Collection Runs</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Status</th>
                            <th>Reports Collected</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="collection-runs">
                        <tr>
                            <td colspan="4">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>Training Runs</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Model Type</th>
                            <th>Model Size</th>
                            <th>Status</th>
                            <th>Train Loss</th>
                            <th>Val Loss</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="training-runs">
                        <tr>
                            <td colspan="6">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            // Fetch metrics from API
            async function fetchMetrics() {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    
                    document.getElementById('total-reports').textContent = data.total_reports;
                    document.getElementById('total-domains').textContent = data.total_domains;
                    document.getElementById('hackerone-reports').textContent = data.reports_by_platform.hackerone;
                    document.getElementById('bugcrowd-reports').textContent = data.reports_by_platform.bugcrowd;
                    document.getElementById('yeswehack-reports').textContent = data.reports_by_platform.yeswehack;
                } catch (error) {
                    console.error('Failed to fetch metrics:', error);
                }
            }
            
            // Initial load
            fetchMetrics();
            
            // Refresh every 30 seconds
            setInterval(fetchMetrics, 30000);
        </script>
    </body>
    </html>
    """
    return html


@app.get("/api/metrics")
async def get_metrics():
    """Get current system metrics."""
    try:
        # Load configuration
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize database
        db_url = config['database']['url']
        db_manager = DatabaseManager(db_url)
        
        # Get statistics
        stats = db_manager.get_statistics()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_reports': stats['total_reports'],
            'total_domains': stats['total_domains'],
            'reports_by_platform': stats['reports_by_platform']
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch metrics: {e}")
        return {'error': str(e)}


def main():
    """Main entry point for the monitoring dashboard."""
    import yaml
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    monitoring_config = config.get('monitoring', {})
    host = monitoring_config.get('host', '0.0.0.0')
    port = monitoring_config.get('port', 8080)
    
    logger.info(f"Starting monitoring dashboard on {host}:{port}")
    
    uvicorn.run(
        "monitoring.dashboard:app",
        host=host,
        port=port,
        reload=False
    )


if __name__ == '__main__':
    main()
