from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse  # Importar HTMLResponse
from fastapi.encoders import jsonable_encoder
import logging
import traceback
from typing import Dict, Any
from pathlib import Path  # Para manejar la lectura del archivo HTML

# Importaciones internas
from api.endpoints import user_router, attendance_router, recognition_router
from core.config import settings
from db.init_db import init_db
from db.session import SessionLocal

# Configuración de logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Sistema de Reconocimiento Facial para Control de Asistencia",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configuración de CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclusión de routers con sus respectivos prefijos y tags
    application.include_router(
        user_router,
        prefix=settings.API_V1_STR,
        tags=["usuarios"]
    )

    application.include_router(
        attendance_router,
        prefix=settings.API_V1_STR,
        tags=["asistencia"]
    )

    application.include_router(
        recognition_router,
        prefix=settings.API_V1_STR,
        tags=["reconocimiento"]
    )

    return application


app = create_application()


@app.on_event("startup")
async def startup_event() -> None:
    """
    Evento de inicio de la aplicación.
    Inicializa la base de datos y configura recursos necesarios.
    """
    try:
        logger.info("Iniciando la aplicación...")
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error durante el inicio de la aplicación: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Evento de cierre de la aplicación.
    Realiza limpieza de recursos y cierre de conexiones.
    """
    logger.info("Deteniendo la aplicación...")
    try:
        await SessionLocal.close_all()
        logger.info("Conexiones de base de datos cerradas correctamente")
    except Exception as e:
        logger.error(f"Error durante el cierre de la aplicación: {str(e)}")


@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """
    Endpoint raíz que proporciona información sobre el estado de la API.
    """
    return {
        "message": "Sistema de Reconocimiento Facial",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """
    Endpoint para verificar el estado de salud de la aplicación.
    Verifica la conexión a la base de datos y otros servicios críticos.
    """
    try:
        # Verificar conexión a la base de datos
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Manejador global de excepciones.
    Proporciona respuestas consistentes para todos los errores de la aplicación.
    """
    logger.error(f"Error no manejado: {str(exc)}")
    logger.error(traceback.format_exc())
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({
                "detail": exc.detail,
                "status_code": exc.status_code
            })
        )
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder({
            "detail": "Error interno del servidor",
            "status_code": 500
        })
    )


# Registro del router
app.include_router(
    recognition_router,
    prefix=f"{settings.API_V1_STR}/recognition",
    tags=["reconocimiento"]
)


@app.get("/stream", response_class=HTMLResponse, tags=["stream"])
async def serve_stream_page():
    """
    Endpoint para servir la página HTML del stream de rostros detectados.
    """
    template_path = Path("backend/templates/stream.html")
    if not template_path.exists():
        return HTMLResponse(content="<h1>El archivo HTML no se encontró</h1>", status_code=404)
    return template_path.read_text()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
