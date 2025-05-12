
# Leviosa AI - Document Processing

Leviosa AI is an intelligent document processing application that makes it easy to parse and extract data from documents.

## Features

- Parse Document: Upload and view PDF files with text extraction
- Extract Data: (Coming soon) Extract structured data from documents
- Dark/Light mode toggle
- Responsive design

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend**: (Planned) FastAPI with CORS support for file uploads

## Development

### Frontend

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The frontend development server will run on http://localhost:5173

### Backend (Future Implementation)

```bash
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn app.main:app --reload
```

The backend API will run on http://localhost:8000

## Backend API (Planned)

- `POST /api/parse`: Upload a document for parsing
  - Request: `FormData` with file
  - Response: `{ url: string }` - URL of the uploaded file

## Upcoming Features

- OCR for text extraction from images
- Table detection and structured data extraction
- Bounding box visualization for detected elements
- Export to various formats (JSON, CSV)

## License

MIT
