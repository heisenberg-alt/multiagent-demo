# Multiagent Demo - Orchestrated AI Agents

A comprehensive multiagent system demonstration featuring orchestrated AI agents from Copilot Studio and Azure AI Foundry, all coordinated through LangChain with Microsoft 365 integration and Azure authentication.

## 🌟 Features

### Core Capabilities
- **Multi-Agent Orchestration**: LangChain-powered coordination of specialized AI agents
- **Four Specialized Agent Types**:
  - **Copilot Studio Agent 1**: General conversation and Q&A
  - **Copilot Studio Agent 2**: Business process automation and workflows
  - **AI Foundry Agent 1**: Document processing and content extraction
  - **AI Foundry Agent 2**: Data analysis and statistical modeling
- **Microsoft 365 Integration**: Access to Teams, OneDrive, SharePoint, and Outlook
- **Azure Authentication**: Entra ID (Azure AD) with RBAC support
- **Real-time Chat**: Interactive conversations with multiple specialized agents
- **Beautiful UI**: Modern React interface with Material-UI components

### Technical Architecture
- **Backend**: FastAPI with Python, async/await patterns
- **Frontend**: React with TypeScript, Redux for state management
- **Authentication**: Azure AD (Entra ID) with MSAL integration
- **Authorization**: Role-based access control (RBAC)
- **Deployment**: Azure Container Apps and Static Web Apps
- **Infrastructure**: Bicep templates for Azure resources

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure subscription
- Azure CLI (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multiagent-demo
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create `.env` file in the backend directory:
   ```env
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
   AZURE_OPENAI_ENDPOINT=your-openai-endpoint
   AZURE_AI_FOUNDRY_ENDPOINT=your-ai-foundry-endpoint
   COPILOT_STUDIO_ENDPOINT=your-copilot-studio-endpoint
   MICROSOFT_GRAPH_ENDPOINT=https://graph.microsoft.com/v1.0
   ```

   Create `.env.local` file in the frontend directory:
   ```env
   REACT_APP_AZURE_CLIENT_ID=your-client-id
   REACT_APP_AZURE_TENANT_ID=your-tenant-id
   REACT_APP_BACKEND_URL=http://localhost:8000
   REACT_APP_REDIRECT_URI=http://localhost:3000
   ```

5. **Run the Application**
   
   Backend:
   ```bash
   cd backend
   python main.py
   ```
   
   Frontend:
   ```bash
   cd frontend
   npm start
   ```

### Azure Deployment

1. **Install Azure Developer CLI**
   ```bash
   # Windows
   winget install Microsoft.Azd
   
   # macOS
   brew install azure-cli
   ```

2. **Login to Azure**
   ```bash
   azd auth login
   ```

3. **Deploy to Azure**
   ```bash
   azd up
   ```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  Azure Services │
│                 │    │                 │    │                 │
│ • Authentication│◄──►│ • Orchestrator  │◄──►│ • Azure OpenAI  │
│ • Chat Interface│    │ • Agent Manager │    │ • AI Foundry    │
│ • Agent Control │    │ • RBAC Handler  │    │ • Copilot Studio│
│ • M365 Data     │    │ • M365 Client   │    │ • Microsoft 365 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agent Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Orchestrator                    │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Copilot Studio  │ Copilot Studio  │      AI Foundry         │
│ Agent 1         │ Agent 2         │      Agents             │
│                 │                 │                         │
│ • General Conv  │ • Business Proc │ Agent 1: Document Proc  │
│ • Q&A Support   │ • Workflows     │ • Text Extraction       │
│ • Information   │ • Task Coord    │ • Classification        │
│   Retrieval     │ • Process Opt   │ • Summarization         │
│                 │                 │                         │
│                 │                 │ Agent 2: Data Analysis  │
│                 │                 │ • Statistical Modeling  │
│                 │                 │ • Predictive Analytics  │
│                 │                 │ • Data Visualization    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 🔧 Configuration

### Agent Configuration
Each agent can be configured through the application settings:

#### Copilot Studio Agents
- **Agent 1 (General)**: Configure for general conversation, Q&A, and information retrieval
- **Agent 2 (Business)**: Configure for workflow automation and business process management

#### AI Foundry Agents  
- **Agent 1 (Document)**: Configure for document processing, text extraction, and content analysis
- **Agent 2 (Data)**: Configure for data analysis, statistical modeling, and predictive analytics

### Agent Specializations

#### COPILOT_STUDIO_1 (`copilot_1`)
- **Focus**: General conversation and assistance
- **Capabilities**: Q&A, information retrieval, basic assistance, greeting handling

#### COPILOT_STUDIO_2 (`copilot_2`) 
- **Focus**: Business process automation
- **Capabilities**: Workflow automation, process management, task coordination, approval workflows

#### AI_FOUNDRY_1 (`ai_foundry_1`)
- **Focus**: Document processing
- **Capabilities**: Document extraction, text classification, content summarization, document comparison

#### AI_FOUNDRY_2 (`ai_foundry_2`)
- **Focus**: Data analysis  
- **Capabilities**: Data analysis, predictive modeling, statistical analysis, data visualization

### RBAC Configuration
Role-based access control is implemented with the following roles:
- **Admin**: Full access to all agents and system settings
- **Agent User**: Access to specific agents based on permissions
- **Viewer**: Read-only access to agent responses and metrics

### M365 Integration
Required permissions for Microsoft 365 integration:
- `User.Read`: User profile information
- `Mail.Read`: Email access
- `Files.ReadWrite`: OneDrive file access
- `Sites.ReadWrite.All`: SharePoint access
- `Team.ReadBasic.All`: Teams information
- `Channel.ReadBasic.All`: Teams channels

## 📊 Monitoring & Analytics

### Built-in Metrics
- Agent response times
- Success rates
- Usage statistics
- Error tracking
- Performance analytics

### Azure Application Insights
Comprehensive telemetry and monitoring:
- Request tracking
- Dependency monitoring
- Custom events
- Performance counters
- Error logging

## 🔒 Security

### Authentication
- Azure AD (Entra ID) integration
- JWT token validation
- Multi-factor authentication support
- Token refresh handling

### Authorization
- Role-based access control (RBAC)
- Agent-specific permissions
- Resource-level security
- Audit logging

### Data Protection
- Encryption at rest and in transit
- Secure communication with Azure services
- PII data handling
- Compliance with security standards

## 🛠️ Development

### Project Structure
```
multiagent-demo/
├── backend/
│   ├── agents/           # Agent implementations
│   ├── auth/            # Authentication & RBAC
│   ├── models/          # Data models
│   ├── utils/           # Utilities & config
│   └── main.py          # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Redux store
│   │   └── utils/       # Utilities
│   └── public/          # Static files
└── infra/               # Azure infrastructure
    ├── main.bicep       # Infrastructure as Code
    └── main.parameters.json
```

### Adding New Agents
1. Create agent class in `backend/agents/`
2. Implement required interfaces
3. Register in orchestrator
4. Add frontend components
5. Update RBAC permissions

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📚 Documentation

### API Documentation
- OpenAPI/Swagger documentation available at `/docs`
- Interactive API explorer at `/redoc`

### Component Documentation
- React components documented with JSDoc
- TypeScript interfaces for all data models
- Redux actions and reducers documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions and support:
- Create an issue in the repository
- Check the documentation
- Review the example configurations

## 🚀 Future Enhancements

- [ ] Voice interaction support for agents
- [ ] Advanced analytics dashboard with agent-specific metrics
- [ ] Plugin system for custom agent extensions
- [ ] Multi-language support for international deployments
- [ ] Advanced workflow orchestration with conditional agent selection
- [ ] Integration with additional Microsoft services (Power Platform, Dynamics)
- [ ] Real-time collaboration features
- [ ] Agent performance optimization and caching
- [ ] Enhanced document processing with OCR capabilities
- [ ] Advanced data visualization and reporting features

---

Built with ❤️ using Azure AI services, LangChain, and modern web technologies.
