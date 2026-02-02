# 🎓 LearnHub - SaaS Platform with Stripe

Modern SaaS platform for online courses with subscription management powered by Stripe.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Stripe](https://img.shields.io/badge/Stripe-Integrated-blueviolet)

---

## Features

- User authentication and authorization (JWT)
- Subscription plans (Free, Pro, Premium)
- Stripe Checkout integration
- Webhook handling for payment confirmation
- Customer Portal for subscription management
- Payment history and invoices
- Responsive design

---

## Tech Stack

**Backend**
- FastAPI (Python 3.11)
- PostgreSQL
- SQLAlchemy ORM
- Stripe Python SDK
- Redis (webhooks queue)

**Frontend**
- React 18
- Stripe.js & Stripe Elements
- Axios

**Infrastructure**
- Docker & Docker Compose

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Stripe account (test mode - free)

### Installation

1. Clone the repository

```bash
git clone https://github.com/carles-cervera/learnhub-saas.git
cd learnhub-saas
```

2. Create `.env` file

```bash
cp .env.example .env
# Edit .env and add your Stripe test keys
```

3. Start services

```bash
docker-compose up --build
```

4. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Stripe Setup (Test Mode - Free)

1. Create account at https://dashboard.stripe.com/register
2. Get your test API keys from https://dashboard.stripe.com/test/apikeys
3. Add to `.env`:
    - `STRIPE_SECRET_KEY=sk_test_...`
    - `STRIPE_PUBLISHABLE_KEY=pk_test_...`

---

## Project Structure

```
learnhub-saas/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── core/        # Config & security
│   └── Dockerfile
├── frontend/            # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

---

## Development

### Backend (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (without Docker)

```bash
cd frontend
npm install
npm start
```

---

## License

MIT

---

## Author

**Carles Cervera**
- GitHub: [@carles-cervera](https://github.com/carles-cervera)
- LinkedIn: [carles-cervera](https://linkedin.com/in/carles-cervera-3581442a6)