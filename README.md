# EVIDEX

**Advanced Legal Document Analysis Platform**

A sleek, dark‑theme web app for legal professionals that extracts text from PDFs/images (Google Cloud Vision) and generates structured legal insights (DeepSeek LLM).

## ✨ Highlights
- **Multi‑format upload** – PDFs, PNG, JPG, JPEG
- **Accurate OCR** – Google Cloud Vision
- **AI‑driven analysis** – Summaries, issue spotting, clause extraction, drafting, checklists
- **Precision Legal UI** – glass‑panel cards, smooth animations, dark palette
- **History & Templates** – view past analyses, ready‑made contract templates
- **Client Profiles** – manage client data

## 🚀 Tech Stack
- **Backend**: FastAPI, SQLModel, SQLite
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **AI services**: Google Cloud Vision (OCR), DeepSeek (LLM)

## 📦 Setup

### Prerequisites
- Python 3.9+
- Node 18+
- Google Cloud Vision API key
- DeepSeek API key

### Backend
```bash
cd EVIDEX
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
cp .env.example .env   # add your API keys
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## ▶️ Run locally
```bash
# backend
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000   # http://localhost:8000

# frontend (in another terminal)
cd frontend
npm run dev
```

## 📚 Usage
1. Choose a document type (Contract, Pleading, Evidence, etc.).
2. Upload a file.
3. Select an analysis task (summary, issue spotting, clause extraction, drafting, checklist).
4. Click **Analyze** – results appear as styled cards with key points, clauses, or action items.

## 🔧 API
- `POST /api/upload` – upload document
- `GET /api/docs` – list documents
- `POST /api/run_task` – start analysis
- `GET /api/tasks/{id}` – get result
- `GET /api/tasks` – list all tasks

## 📁 Project layout
```
EVIDEX/
├─ backend/
│  ├─ api/routes.py
│  ├─ services/ocr.py
│  ├─ services/llm.py
│  └─ …
├─ frontend/
│  └─ src/app/   # pages
│  └─ src/components/
└─ README.md
```

## 🔐 Security
- API keys are read from `.env` (ignored by Git).
- Input validation on all endpoints.
- No authentication in MVP – add before production.

## 🚧 Roadmap
- User auth & authorization
- Multi‑user support
- Export reports (PDF/DOCX)
- Real‑time collaboration
- Cloud storage integration

## 📄 License
MIT – see `LICENSE`.

## 👤 Author
**Affan Khan** – [GitHub @kaffan](https://github.com/kaffan)

## 🙏 Acknowledgments
- Google Cloud Vision
- DeepSeek
- Next.js team
- FastAPI community

---

Built for legal professionals.

**Advanced Legal Document Analysis Platform**

A cutting-edge web application designed for legal professionals to analyze documents using OCR and natural language processing.

---

## 🌟 Features

### Document Processing
- **Multi-Format Support**: Upload PDFs, images (PNG, JPG, JPEG)
- **OCR Integration**: Google Cloud Vision API for accurate text extraction
- **Intelligent Analysis**: Powered by DeepSeek LLM

### Legal Analysis Tools
- **Legal Summary**: Generate concise overviews of legal documents
- **Issue Spotting**: Identify potential legal concerns and risks
- **Clause Extraction**: Extract and analyze key contractual clauses
- **Document Drafting**: Assisted legal document creation
- **Compliance Checklists**: Generate actionable compliance items

### User Interface
- **Precision Legal Theme**: Sharp, professional dark interface
- **Real-time Analysis**: Live progress tracking
- **History Management**: Access past analyses
- **Template Library**: Pre-built legal document templates
- **Client Profiles**: Manage client information

---

## 🚀 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLModel**: Type-safe SQL database interactions
- **Google Cloud Vision**: OCR processing
- **DeepSeek LLM**: Legal text analysis
- **SQLite**: Lightweight database

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Vision API Key
- DeepSeek API Key

### Backend Setup

```bash
# Navigate to project root
cd EVIDEX

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cd backend
cp .env.example .env  # Create this file with your API keys
```

**`.env` file structure:**
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🏃 Running the Application

### Start Backend Server

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

## 📸 Screenshots

### Analysis Dashboard
![Main Dashboard](screenshots/dashboard.png)

### Document Type Selection
![Document Types](screenshots/doc-types.png)

### Analysis Results
![Results View](screenshots/results.png)

---

## 🎯 Usage

1. **Select Document Type**: Choose from Contract, Pleading, Evidence, Correspondence, or Other
2. **Upload Document**: Drag and drop or click to upload your legal document
3. **Choose Analysis Task**: Select from summary, issue spotting, clause extraction, drafting, or checklist
4. **Execute Analysis**: Click to start analysis
5. **Review Results**: View structured analysis with key insights

---

## 🔧 API Endpoints

### Document Management
- `POST /api/upload` - Upload and process document
- `GET /api/docs` - List all uploaded documents

### Task Execution
- `POST /api/run_task` - Execute legal analysis task
- `GET /api/tasks/{id}` - Get task result
- `GET /api/tasks` - List all tasks

---

## 🏗️ Project Structure

```
EVIDEX/
├── backend/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── ocr.py            # OCR processing
│   │   └── llm.py            # LLM integration
│   ├── models.py             # Database models
│   ├── database.py           # Database configuration
│   └── main.py               # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   └── components/       # React components
│   └── package.json
└── README.md
```

---

## 🔐 Security

- API keys stored in environment variables
- Input validation on all endpoints
- Secure file upload handling
- No authentication in MVP (add before production)

---

## 🚧 Roadmap

- [ ] User authentication & authorization
- [ ] Multi-user support
- [ ] Export analysis reports (PDF, DOCX)
- [ ] Advanced template customization
- [ ] Real-time collaboration
- [ ] Cloud storage integration

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Affan Khan**
- GitHub: [@kaffan](https://github.com/kaffan)

---

## 🙏 Acknowledgments

- Google Cloud Vision for OCR capabilities
- DeepSeek for LLM processing
- Next.js team for excellent framework
- FastAPI community

---

**Built with ⚖️ for Legal Professionals**

**Advanced Legal Document Analysis Platform**

A cutting-edge web application designed for legal professionals to analyze documents using OCR and natural language processing.

---

## 🌟 Features

### Document Processing
- **Multi-Format Support**: Upload PDFs, images (PNG, JPG, JPEG)
- **OCR Integration**: Google Cloud Vision API for accurate text extraction
- **Intelligent Analysis**: Powered by DeepSeek LLM

### Legal Analysis Tools
- **Legal Summary**: Generate concise overviews of legal documents
- **Issue Spotting**: Identify potential legal concerns and risks
- **Clause Extraction**: Extract and analyze key contractual clauses
- **Document Drafting**: Assisted legal document creation
- **Compliance Checklists**: Generate actionable compliance items

### User Interface
- **Precision Legal Theme**: Sharp, professional dark interface
- **Real-time Analysis**: Live progress tracking
- **History Management**: Access past analyses
- **Template Library**: Pre-built legal document templates
- **Client Profiles**: Manage client information

---

## 🚀 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLModel**: Type-safe SQL database interactions
- **Google Cloud Vision**: OCR processing
- **DeepSeek LLM**: Legal text analysis
- **SQLite**: Lightweight database

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Vision API Key
- DeepSeek API Key

### Backend Setup

```bash
# Navigate to project root
cd EVIDEX

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cd backend
cp .env.example .env  # Create this file with your API keys
```

**`.env` file structure:**
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🏃 Running the Application

### Start Backend Server

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

## 📸 Screenshots

### Analysis Dashboard
![Main Dashboard](screenshots/dashboard.png)

### Document Type Selection
![Document Types](screenshots/doc-types.png)

### Analysis Results
![Results View](screenshots/results.png)

---

## 🎯 Usage

1. **Select Document Type**: Choose from Contract, Pleading, Evidence, Correspondence, or Other
2. **Upload Document**: Drag and drop or click to upload your legal document
3. **Choose Analysis Task**: Select from summary, issue spotting, clause extraction, drafting, or checklist
4. **Execute Analysis**: Click to start analysis
5. **Review Results**: View structured analysis with key insights

---

## 🔧 API Endpoints

### Document Management
- `POST /api/upload` - Upload and process document
- `GET /api/docs` - List all uploaded documents

### Task Execution
- `POST /api/run_task` - Execute legal analysis task
- `GET /api/tasks/{id}` - Get task result
- `GET /api/tasks` - List all tasks

---

## 🏗️ Project Structure

```
EVIDEX/
├── backend/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── ocr.py            # OCR processing
│   │   └── llm.py            # LLM integration
│   ├── models.py             # Database models
│   ├── database.py           # Database configuration
│   └── main.py               # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   └── components/       # React components
│   └── package.json
└── README.md
```

---

## 🔐 Security

- API keys stored in environment variables
- Input validation on all endpoints
- Secure file upload handling
- No authentication in MVP (add before production)

---

## 🚧 Roadmap

- [ ] User authentication & authorization
- [ ] Multi-user support
- [ ] Export analysis reports (PDF, DOCX)
- [ ] Advanced template customization
- [ ] Real-time collaboration
- [ ] Cloud storage integration

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Affan Khan**
- GitHub: [@kaffan](https://github.com/kaffan)

---

## 🙏 Acknowledgments

- Google Cloud Vision for OCR capabilities
- DeepSeek for LLM processing
- Next.js team for excellent framework
- FastAPI community

---

**Built with ⚖️ for Legal Professionals**

**Advanced Legal Document Analysis Platform**

A cutting-edge web application designed for legal professionals to analyze documents using AI-powered OCR and natural language processing.

---

## 🌟 Features

### Document Processing
- **Multi-Format Support**: Upload PDFs, images (PNG, JPG, JPEG)
- **OCR Integration**: Google Cloud Vision API for accurate text extraction
- **Intelligent Analysis**: Powered by DeepSeek LLM

### Legal Analysis Tools
- **Legal Summary**: Generate concise overviews of legal documents
- **Issue Spotting**: Identify potential legal concerns and risks
- **Clause Extraction**: Extract and analyze key contractual clauses
- **Document Drafting**: AI-assisted legal document creation
- **Compliance Checklists**: Generate actionable compliance items

### User Interface
- **Precision Legal Theme**: Sharp, professional dark interface
- **Real-time Analysis**: Live progress tracking
- **History Management**: Access past analyses
- **Template Library**: Pre-built legal document templates
- **Client Profiles**: Manage client information

---

## 🚀 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLModel**: Type-safe SQL database interactions
- **Google Cloud Vision**: OCR processing
- **DeepSeek LLM**: Legal text analysis
- **SQLite**: Lightweight database

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Vision API Key
- DeepSeek API Key

### Backend Setup

```bash
# Navigate to project root
cd EVIDEX

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cd backend
cp .env.example .env  # Create this file with your API keys
```

**`.env` file structure:**
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🏃 Running the Application

### Start Backend Server
```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

### Start Frontend Server
```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

## 📸 Screenshots

### Analysis Dashboard
![Main Dashboard](screenshots/dashboard.png)

### Document Type Selection
![Document Types](screenshots/doc-types.png)

### Analysis Results
![Results View](screenshots/results.png)

---

## 🎯 Usage

1. **Select Document Type**: Choose from Contract, Pleading, Evidence, Correspondence, or Other
2. **Upload Document**: Drag and drop or click to upload your legal document
3. **Choose Analysis Task**: Select from summary, issue spotting, clause extraction, drafting, or checklist
4. **Execute Analysis**: Click to start AI-powered analysis
5. **Review Results**: View structured analysis with key insights

---

## 🔧 API Endpoints

### Document Management
- `POST /api/upload` - Upload and process document
- `GET /api/docs` - List all uploaded documents

### Task Execution
- `POST /api/run_task` - Execute legal analysis task
- `GET /api/tasks/{id}` - Get task result
- `GET /api/tasks` - List all tasks

---

## 🏗️ Project Structure

```
EVIDEX/
├── backend/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── ocr.py            # OCR processing
│   │   └── llm.py            # LLM integration
│   ├── models.py             # Database models
│   ├── database.py           # Database configuration
│   └── main.py               # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   └── components/       # React components
│   └── package.json
└── README.md
```

---

## 🔐 Security

- API keys stored in environment variables
- Input validation on all endpoints
- Secure file upload handling
- No authentication in MVP (add before production)

---

## 🚧 Roadmap

- [ ] User authentication & authorization
- [ ] Multi-user support
- [ ] Export analysis reports (PDF, DOCX)
- [ ] Advanced template customization
- [ ] Real-time collaboration
- [ ] Cloud storage integration

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Affan Khan**
- GitHub: [@kaffan](https://github.com/kaffan)

---

## 🙏 Acknowledgments

- Google Cloud Vision for OCR capabilities
- DeepSeek for LLM processing
- Next.js team for excellent framework
- FastAPI community

---

**Built with ⚖️ for Legal Professionals**
