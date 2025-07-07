"""
Telemetry and monitoring for the multiagent system.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

try:
    from applicationinsights import TelemetryClient
    from applicationinsights.logging import LoggingHandler
except ImportError:
    TelemetryClient = None
    LoggingHandler = None

logger = logging.getLogger(__name__)

class TelemetryManager:
    """Manages telemetry and monitoring for the application."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize telemetry manager."""
        self.connection_string = connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        self.client = None
        
        if self.connection_string and TelemetryClient:
            try:
                self.client = TelemetryClient(self.connection_string)
                logger.info("Application Insights telemetry initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Application Insights: {str(e)}")
        else:
            logger.warning("Application Insights not available - telemetry will be logged locally")
    
    def track_event(self, name: str, properties: Optional[Dict[str, Any]] = None, measurements: Optional[Dict[str, float]] = None):
        """Track a custom event."""
        if self.client:
            try:
                self.client.track_event(name, properties, measurements)
            except Exception as e:
                logger.error(f"Failed to track event {name}: {str(e)}")
        else:
            # Fallback to logging
            event_data = {
                "event": name,
                "properties": properties or {},
                "measurements": measurements or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Event: {json.dumps(event_data)}")
    
    def track_request(self, name: str, url: str, success: bool, duration: float, response_code: int = 200, properties: Optional[Dict[str, Any]] = None):
        """Track an HTTP request."""
        if self.client:
            try:
                self.client.track_request(name, url, success, duration, response_code, properties)
            except Exception as e:
                logger.error(f"Failed to track request {name}: {str(e)}")
        else:
            # Fallback to logging
            request_data = {
                "request": name,
                "url": url,
                "success": success,
                "duration": duration,
                "response_code": response_code,
                "properties": properties or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Request: {json.dumps(request_data)}")
    
    def track_dependency(self, name: str, data: str, type_name: str, target: str, success: bool, duration: float, properties: Optional[Dict[str, Any]] = None):
        """Track a dependency call."""
        if self.client:
            try:
                self.client.track_dependency(name, data, type_name, target, success, duration, properties)
            except Exception as e:
                logger.error(f"Failed to track dependency {name}: {str(e)}")
        else:
            # Fallback to logging
            dependency_data = {
                "dependency": name,
                "data": data,
                "type": type_name,
                "target": target,
                "success": success,
                "duration": duration,
                "properties": properties or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Dependency: {json.dumps(dependency_data)}")
    
    def track_exception(self, exception: Exception, properties: Optional[Dict[str, Any]] = None):
        """Track an exception."""
        if self.client:
            try:
                self.client.track_exception(type(exception), exception, properties=properties)
            except Exception as e:
                logger.error(f"Failed to track exception: {str(e)}")
        else:
            # Fallback to logging
            exception_data = {
                "exception": str(exception),
                "type": type(exception).__name__,
                "properties": properties or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.error(f"Exception: {json.dumps(exception_data)}")
    
    def track_metric(self, name: str, value: float, properties: Optional[Dict[str, Any]] = None):
        """Track a custom metric."""
        if self.client:
            try:
                self.client.track_metric(name, value, properties)
            except Exception as e:
                logger.error(f"Failed to track metric {name}: {str(e)}")
        else:
            # Fallback to logging
            metric_data = {
                "metric": name,
                "value": value,
                "properties": properties or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Metric: {json.dumps(metric_data)}")
    
    def track_trace(self, message: str, severity: str = "Information", properties: Optional[Dict[str, Any]] = None):
        """Track a trace message."""
        if self.client:
            try:
                self.client.track_trace(message, severity, properties)
            except Exception as e:
                logger.error(f"Failed to track trace: {str(e)}")
        else:
            # Fallback to logging
            trace_data = {
                "trace": message,
                "severity": severity,
                "properties": properties or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Trace: {json.dumps(trace_data)}")
    
    def track_agent_interaction(self, user_id: str, agent_type: str, query: str, success: bool, duration: Optional[float] = None):
        """Track an agent interaction."""
        properties = {
            "user_id": user_id,
            "agent_type": agent_type,
            "query_length": len(query),
            "success": success
        }
        
        measurements = {}
        if duration is not None:
            measurements["duration"] = duration
        
        self.track_event("agent_interaction", properties, measurements)
    
    def track_orchestration(self, user_id: str, query: str, agents_used: List[str], success: bool, duration: Optional[float] = None):
        """Track a multiagent orchestration."""
        properties = {
            "user_id": user_id,
            "query_length": len(query),
            "agents_used": ",".join(agents_used),
            "num_agents": len(agents_used),
            "success": success
        }
        
        measurements = {}
        if duration is not None:
            measurements["duration"] = duration
        
        self.track_event("orchestration", properties, measurements)
    
    def track_chat_message(self, user_id: str, session_id: str, message: str, success: bool):
        """Track a chat message."""
        properties = {
            "user_id": user_id,
            "session_id": session_id,
            "message_length": len(message),
            "success": success
        }
        
        self.track_event("chat_message", properties)
    
    def track_permission_change(self, admin_user_id: str, target_user_id: str, permissions: Dict[str, Any]):
        """Track a permission change."""
        properties = {
            "admin_user_id": admin_user_id,
            "target_user_id": target_user_id,
            "permissions_changed": json.dumps(permissions)
        }
        
        self.track_event("permission_change", properties)
    
    def track_authentication(self, user_id: str, success: bool, method: str = "unknown"):
        """Track an authentication attempt."""
        properties = {
            "user_id": user_id,
            "success": success,
            "method": method
        }
        
        self.track_event("authentication", properties)
    
    def track_rate_limit(self, user_id: str, endpoint: str, limit_type: str):
        """Track a rate limit event."""
        properties = {
            "user_id": user_id,
            "endpoint": endpoint,
            "limit_type": limit_type
        }
        
        self.track_event("rate_limit", properties)
    
    def track_system_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Track a system metric."""
        self.track_metric(f"system.{metric_name}", value, tags)
    
    def flush(self):
        """Flush all telemetry data."""
        if self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to flush telemetry: {str(e)}")
    
    def shutdown(self):
        """Shutdown telemetry client."""
        if self.client:
            try:
                self.client.flush()
                # Note: Application Insights client doesn't have an explicit shutdown method
            except Exception as e:
                logger.error(f"Failed to shutdown telemetry: {str(e)}")

class TelemetryContext:
    """Context manager for adding telemetry context."""
    
    def __init__(self, telemetry: TelemetryManager, **context):
        self.telemetry = telemetry
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type is not None:
            # An exception occurred
            self.telemetry.track_exception(exc_val, self.context)
        
        # Track the operation
        self.context["duration"] = duration
        self.context["success"] = exc_type is None
        
        operation_name = self.context.get("operation", "unknown")
        self.telemetry.track_event(f"operation_{operation_name}", self.context)

def track_operation(operation_name: str, telemetry: TelemetryManager):
    """Decorator to track operation execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                telemetry.track_exception(e, {"operation": operation_name})
                raise
            finally:
                duration = (datetime.utcnow() - start_time).total_seconds()
                telemetry.track_event(
                    f"operation_{operation_name}",
                    {"success": success, "duration": duration}
                )
        
        return wrapper
    return decorator

def track_async_operation(operation_name: str, telemetry: TelemetryManager):
    """Decorator to track async operation execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                telemetry.track_exception(e, {"operation": operation_name})
                raise
            finally:
                duration = (datetime.utcnow() - start_time).total_seconds()
                telemetry.track_event(
                    f"operation_{operation_name}",
                    {"success": success, "duration": duration}
                )
        
        return wrapper
    return decorator

# Global telemetry client instance
telemetry_client = TelemetryManager()
