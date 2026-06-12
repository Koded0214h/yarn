import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import get_settings
from db.database import engine, Base
from api.routes import router

logging.basicConfig(level=logging.INFO, format='%(levelname)s  %(name)s  %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Create tables on startup (idempotent for prototype)
    Base.metadata.create_all(bind=engine)
    logger.info('Database tables ready.')
    yield


settings = get_settings()

app = FastAPI(
    title='YARN API',
    description='Voice-First Agent for the Oral Majority',
    version='1.0.0-prototype',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, 'http://localhost:5173', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Serve generated PDFs
invoices_dir = Path(__file__).parent / 'static' / 'invoices'
invoices_dir.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=Path(__file__).parent / 'static'), name='static')

app.include_router(router)


@app.get('/health')
def health():
    return {'status': 'ok', 'version': '1.0.0-prototype'}
