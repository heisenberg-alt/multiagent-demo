# Agent Documentation

## Overview

The Multiagent System features four specialized AI agents, each designed for specific use cases and capabilities. This document provides detailed information about each agent, their specializations, capabilities, and usage patterns.

## Agent Architecture

```
Multiagent Orchestrator System
├── Copilot Studio Agents
│   ├── Agent 1: General Conversation (copilot_1)
│   └── Agent 2: Business Process (copilot_2)
└── AI Foundry Agents
    ├── Agent 1: Document Processing (ai_foundry_1)
    └── Agent 2: Data Analysis (ai_foundry_2)
```

## Copilot Studio Agents

### Agent 1: General Conversation (`copilot_studio_1`)

**Agent ID**: `copilot_1`  
**Specialization**: `general`  
**Purpose**: General conversation, Q&A, and basic assistance

#### Capabilities
- **General Conversation**: Natural language conversation and dialogue
- **Question Answering**: Answering questions across various domains
- **Information Retrieval**: Finding and presenting relevant information
- **Basic Assistance**: Helping users with general tasks and inquiries
- **Greeting Handling**: Managing initial user interactions and welcomes

#### Best Use Cases
- Customer support interactions
- General knowledge queries
- Greeting and onboarding new users
- Basic information lookup
- Conversational AI interactions

#### Configuration
```json
{
  "agent_type": "copilot_studio_1",
  "agent_id": "copilot_1",
  "specialization": "general",
  "endpoint": "https://your-copilot-studio.com/api/v1/bots/general",
  "authentication": {
    "type": "azure_ad",
    "scope": "https://api.botframework.com/.default"
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500,
    "response_format": "conversational"
  }
}
```

#### Example Usage
```python
# Direct API call
response = await client.agents.copilot_studio_1.query({
    "query": "Hello, can you help me understand how this system works?",
    "context": {
        "conversation_type": "general",
        "user_level": "beginner"
    }
})

# Expected response
{
    "success": True,
    "response": "Hello! I'm here to help you understand our multiagent system...",
    "agent_type": "copilot_studio_1",
    "agent_id": "copilot_1",
    "confidence": 0.85
}
```

### Agent 2: Business Process (`copilot_studio_2`)

**Agent ID**: `copilot_2`  
**Specialization**: `business_process`  
**Purpose**: Business process automation and workflow management

#### Capabilities
- **Workflow Automation**: Creating and managing automated workflows
- **Business Process Management**: Optimizing and streamlining business processes
- **Task Coordination**: Coordinating tasks across teams and systems
- **Process Optimization**: Identifying and implementing process improvements
- **Approval Workflows**: Managing approval processes and routing

#### Best Use Cases
- Setting up approval workflows
- Process automation requests
- Task delegation and coordination
- Business process optimization
- Workflow troubleshooting

#### Configuration
```json
{
  "agent_type": "copilot_studio_2",
  "agent_id": "copilot_2",
  "specialization": "business_process",
  "endpoint": "https://your-copilot-studio.com/api/v1/bots/business",
  "parameters": {
    "temperature": 0.5,
    "max_tokens": 1000,
    "workflow_integration": true,
    "process_templates": ["approval", "escalation", "routing"]
  }
}
```

#### Example Usage
```python
# Workflow automation request
response = await client.agents.copilot_studio_2.query({
    "query": "Help me set up an expense report approval workflow",
    "context": {
        "workflow_type": "approval",
        "department": "finance",
        "approval_levels": 2
    }
})

# Expected response
{
    "success": True,
    "response": "I'll help you create an expense report approval workflow...",
    "agent_type": "copilot_studio_2",
    "agent_id": "copilot_2",
    "metadata": {
        "workflow_template": "expense_approval",
        "estimated_setup_time": "15_minutes"
    }
}
```

## AI Foundry Agents

### Agent 1: Document Processing (`ai_foundry_1`)

**Agent ID**: `ai_foundry_1`  
**Specialization**: `document_processing`  
**Purpose**: Document analysis, extraction, and processing

#### Capabilities
- **Document Extraction**: Extract structured data from unstructured documents
- **Text Classification**: Classify documents into categories
- **Content Summarization**: Generate summaries of long documents
- **Document Comparison**: Compare documents for similarity and differences

#### Supported Document Types
- PDF documents
- Microsoft Word documents (DOCX)
- Plain text files
- HTML content
- Emails and messaging formats

#### Best Use Cases
- Contract analysis and data extraction
- Invoice processing and validation
- Document classification and organization
- Content summarization for reports
- Legal document review

#### Configuration
```json
{
  "agent_type": "ai_foundry_1",
  "agent_id": "ai_foundry_1",
  "specialization": "document_processing",
  "endpoint": "https://your-ai-foundry.com/api/v1/document",
  "parameters": {
    "max_file_size": "50MB",
    "supported_formats": ["pdf", "docx", "txt", "html"],
    "extraction_models": ["contract", "invoice", "general"],
    "language_support": ["en", "es", "fr", "de"]
  }
}
```

#### Example Usage
```python
# Document processing request
response = await client.agents.ai_foundry_1.process({
    "query": "Extract key information from this contract document",
    "context": {
        "document_type": "contract",
        "extraction_fields": ["parties", "dates", "amounts", "terms"]
    },
    "file_data": {
        "content": "base64_encoded_pdf_content",
        "filename": "service_contract.pdf",
        "mime_type": "application/pdf"
    }
})

# Expected response
{
    "success": True,
    "response": {
        "extracted_data": {
            "parties": ["Acme Corp", "Beta Solutions"],
            "dates": {
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "signature_date": "2024-12-15"
            },
            "amounts": ["$120,000", "$10,000/month"],
            "key_terms": ["confidentiality", "termination_clause"]
        },
        "summary": "Service contract between Acme Corp and Beta Solutions...",
        "confidence": 0.92
    },
    "agent_type": "ai_foundry_1",
    "agent_id": "ai_foundry_1"
}
```

### Agent 2: Data Analysis (`ai_foundry_2`)

**Agent ID**: `ai_foundry_2`  
**Specialization**: `data_analysis`  
**Purpose**: Statistical analysis, data modeling, and insights generation

#### Capabilities
- **Data Analysis**: Advanced data analysis and statistical modeling
- **Predictive Modeling**: Create predictive models using machine learning
- **Data Visualization**: Create interactive data visualizations and dashboards
- **Statistical Analysis**: Perform statistical analysis and hypothesis testing

#### Supported Data Formats
- CSV files
- JSON datasets
- Excel spreadsheets (XLSX)
- Database query results
- Time series data

#### Best Use Cases
- Sales data analysis and forecasting
- Customer behavior analysis
- Financial performance modeling
- Market trend analysis
- Statistical hypothesis testing

#### Configuration
```json
{
  "agent_type": "ai_foundry_2",
  "agent_id": "ai_foundry_2",
  "specialization": "data_analysis",
  "endpoint": "https://your-ai-foundry.com/api/v1/analytics",
  "parameters": {
    "max_dataset_size": "100MB",
    "supported_formats": ["csv", "json", "xlsx"],
    "analysis_types": ["descriptive", "predictive", "prescriptive"],
    "visualization_types": ["charts", "graphs", "dashboards"]
  }
}
```

#### Example Usage
```python
# Data analysis request
response = await client.agents.ai_foundry_2.process({
    "query": "Analyze this sales data for trends and create forecasts",
    "context": {
        "analysis_type": "trend_analysis",
        "time_period": "quarterly",
        "forecast_horizon": "next_quarter"
    },
    "data": {
        "format": "csv",
        "content": "date,sales,region,product\n2025-01-01,15000,North,Widget A\n..."
    }
})

# Expected response
{
    "success": True,
    "response": {
        "analysis_result": {
            "trends": {
                "overall_growth": "12.5%",
                "seasonal_patterns": "Q4_peak",
                "regional_performance": {
                    "North": "+15%",
                    "South": "+8%",
                    "East": "+10%",
                    "West": "+5%"
                }
            },
            "forecast": {
                "next_quarter_projection": "$450,000",
                "confidence_interval": "±$25,000"
            },
            "insights": [
                "Strong growth in North region",
                "Seasonal patterns indicate Q4 strength",
                "Widget A showing consistent performance"
            ]
        },
        "visualizations": ["trend_chart.png", "regional_map.png"],
        "confidence": 0.88
    },
    "agent_type": "ai_foundry_2",
    "agent_id": "ai_foundry_2"
}
```

## Orchestration Patterns

### Agent Selection Logic

The orchestrator uses the following logic to select appropriate agents:

1. **Query Analysis**: Analyze the user query for keywords and intent
2. **Context Evaluation**: Consider provided context and metadata
3. **Capability Matching**: Match query requirements to agent capabilities
4. **Preference Handling**: Consider any specified preferred agents
5. **Load Balancing**: Distribute requests across available agents

### Common Orchestration Scenarios

#### Scenario 1: Document Analysis with Insights
```
User Query: "Analyze this contract and provide business insights"
→ AI Foundry Agent 1 (Document Processing): Extract contract data
→ AI Foundry Agent 2 (Data Analysis): Analyze extracted data for insights
→ Orchestrator: Combine results into comprehensive response
```

#### Scenario 2: Process Automation Setup
```
User Query: "Help me automate our invoice approval process"
→ Copilot Studio Agent 2 (Business Process): Design workflow
→ AI Foundry Agent 1 (Document Processing): Configure invoice processing
→ Orchestrator: Provide complete automation solution
```

#### Scenario 3: General Support with Escalation
```
User Query: "I need help with complex data analysis"
→ Copilot Studio Agent 1 (General): Initial assessment
→ AI Foundry Agent 2 (Data Analysis): Detailed analysis capabilities
→ Orchestrator: Route to appropriate specialist
```

## Performance Characteristics

### Response Times (Typical)

| Agent Type | Simple Query | Complex Request | File Processing |
|------------|-------------|-----------------|----------------|
| Copilot Studio 1 | 1-2 seconds | 3-5 seconds | N/A |
| Copilot Studio 2 | 2-3 seconds | 5-8 seconds | N/A |
| AI Foundry 1 | 3-5 seconds | 8-15 seconds | 10-30 seconds |
| AI Foundry 2 | 5-10 seconds | 15-30 seconds | 20-60 seconds |

### Throughput Limits

- **Copilot Studio Agents**: 100 requests/minute per agent
- **AI Foundry Agents**: 50 requests/minute per agent
- **Orchestration**: 200 requests/minute total

### Error Handling

Each agent implements robust error handling:

1. **Connection Errors**: Automatic retry with exponential backoff
2. **Processing Errors**: Graceful degradation with meaningful error messages
3. **Timeout Handling**: Configurable timeouts with fallback responses
4. **Mock Mode**: Fallback to mock responses when services unavailable

## Monitoring and Analytics

### Health Checks

Each agent provides health endpoints:
- `/health`: Basic connectivity test
- `/health/detailed`: Comprehensive status including dependencies
- `/metrics`: Performance and usage metrics

### Key Metrics

- **Request Volume**: Total requests per agent per time period
- **Success Rate**: Percentage of successful requests
- **Response Time**: Average and percentile response times
- **Error Rate**: Percentage of failed requests
- **Availability**: Uptime percentage

### Alerting

Configure alerts for:
- Agent unavailability (> 5 minutes)
- High error rates (> 10%)
- Slow response times (> 95th percentile)
- Quota exhaustion

## Best Practices

### Agent Selection
1. Use the orchestrator for complex, multi-step tasks
2. Call agents directly for simple, single-purpose requests
3. Specify preferred agents when you know the optimal choice
4. Provide rich context to improve agent selection

### Error Handling
1. Implement retry logic for transient failures
2. Handle agent unavailability gracefully
3. Provide meaningful fallback responses
4. Log errors for monitoring and debugging

### Performance Optimization
1. Cache frequently accessed data
2. Use appropriate timeout values
3. Batch related requests when possible
4. Monitor and optimize based on usage patterns

### Security
1. Always use authenticated requests
2. Validate user permissions before agent access
3. Sanitize inputs, especially for file uploads
4. Monitor for unusual usage patterns

## Troubleshooting

### Common Issues

#### Agent Unavailable
- **Symptoms**: 503 errors, timeout responses
- **Solutions**: Check agent health, verify configuration, restart if needed

#### Slow Response Times
- **Symptoms**: High latency, timeout errors
- **Solutions**: Check network connectivity, review request complexity, optimize queries

#### Authentication Failures
- **Symptoms**: 401/403 errors
- **Solutions**: Verify JWT tokens, check user permissions, refresh credentials

#### Invalid Responses
- **Symptoms**: Malformed or unexpected responses
- **Solutions**: Check input format, review agent configuration, update request structure

### Debugging Tools

1. **Health Check Endpoints**: Verify agent status
2. **Request Tracing**: Track request flow through system
3. **Log Analysis**: Review detailed logs for errors
4. **Performance Metrics**: Monitor response times and throughput

---

For additional support and examples, see the [API Documentation](./API_DOCUMENTATION.md) or contact the development team.
