#!/usr/bin/env python3
# Dre Proprietary Copyright 2023. All rights reserved.

"""
app.py

This module serves as the entry point for the Self-Healing API Monitoring tool.
It initializes the Flask application and sets up routes, error handlers, and other configurations.
"""

from flask import Flask, request, jsonify
import logging
from werkzeug.exceptions import HTTPException
from dre_optimized_1787.api_monitoring.service_layer import ApiHealthChecker

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def check_api_health():
    """
    Endpoint to check the health of the API.
    
    Returns:
        JSON: A dictionary containing the status of the API and its components.
    """
    try:
        checker = ApiHealthChecker()
        result = checker.check_health()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error checking API health: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/monitor', methods=['POST'])
def monitor_api():
    """
    Endpoint to start monitoring the API.
    
    Returns:
        JSON: A confirmation message indicating whether monitoring was started successfully.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing URL parameter"}), 400
        
        url = data['url']
        checker = ApiHealthChecker(url)
        result = checker.start_monitoring()
        return jsonify(result), 201
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e}")
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logger.error(f"Error monitoring API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop_monitor', methods=['POST'])
def stop_api_monitor():
    """
    Endpoint to stop the ongoing API monitoring.
    
    Returns:
        JSON: A confirmation message indicating whether monitoring was stopped successfully.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing URL parameter"}), 400
        
        url = data['url']
        checker = ApiHealthChecker(url)
        result = checker.stop_monitoring()
        return jsonify(result), 200
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e}")
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        logger.error(f"Error stopping API monitoring: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """
    Global error handler for the application.
    
    Args:
        error (Exception): The exception that was raised.
        
    Returns:
        JSON: A dictionary containing an error message and status code.
    """
    logger.exception(f"Uncaught exception: {error}")
    return jsonify({"error": str(error)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)