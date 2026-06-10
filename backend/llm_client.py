import os
import json
import logging
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

SYSTEM_PROMPT = """Eres un asistente profesional de inspección de ingeniería civil.
Tu función es generar informes de inspección claros, formales y prácticos basados en los resultados de detección por IA.
SIEMPRE escribe en español formal y profesional de ingeniería civil.
SIEMPRE menciona que los resultados deben ser verificados por un ingeniero civil cualificado.
Responde ÚNICAMENTE con un objeto JSON válido, sin markdown, sin texto adicional."""

REPORT_PROMPT_TEMPLATE = """Genera un informe detallado de inspección de ingeniería civil basado en estos resultados de detección por IA.
IMPORTANTE: Todo el informe debe estar escrito completamente en español.

Nombre del cliente: Dani
Tipo de activo: {asset_type}
Modelo utilizado: {model_name}
Total de defectos detectados: {total_defects}

Patologías detectadas (JSON):
{detections_json}

Notas del ingeniero:
{engineer_notes}

Devuelve un objeto JSON con exactamente estas claves (todo el contenido en español):
{{
  "executive_summary": "Resumen ejecutivo de 2-3 oraciones sobre los hallazgos",
  "defect_descriptions": "Descripción detallada de cada tipo de defecto detectado",
  "possible_causes": "Análisis técnico de las causas probables de las patologías detectadas",
  "severity_assessment": "Evaluación de la gravedad de los defectos con justificación técnica",
  "risk_explanation": "Explicación de los riesgos para la integridad estructural y la seguridad",
  "recommended_actions": "Acciones de reparación y mantenimiento específicas y priorizadas",
  "priority_level": "Inmediato / Corto plazo / Largo plazo",
  "final_conclusion": "Conclusión profesional y próximos pasos"
}}"""


def generate_llm_report(
    asset_type: str,
    model_name: str,
    detections: list,
    engineer_notes: str
) -> Dict[str, Any]:

    if not LLM_API_KEY:
        logger.warning("No LLM_API_KEY configured. Using template report.")
        return _fallback_report(asset_type, model_name, detections, engineer_notes)

    prompt = REPORT_PROMPT_TEMPLATE.format(
        asset_type=asset_type,
        model_name=model_name,
        total_defects=len(detections),
        detections_json=json.dumps(detections, indent=2),
        engineer_notes=engineer_notes or "No additional notes provided."
    )

    try:
        with httpx.Client(timeout=LLM_TIMEOUT) as client:
            response = client.post(
                f"{LLM_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API HTTP error: {e.response.status_code} - {e.response.text}")
        return _fallback_report(asset_type, model_name, detections, engineer_notes)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        return _fallback_report(asset_type, model_name, detections, engineer_notes)
    except Exception as e:
        logger.error(f"LLM report generation failed: {e}")
        return _fallback_report(asset_type, model_name, detections, engineer_notes)


def _fallback_report(asset_type: str, model_name: str, detections: list, engineer_notes: str) -> Dict[str, Any]:
    """Informe de plantilla cuando no hay clave LLM disponible."""
    classes = list({d["class"] for d in detections})
    severity_counts = {}
    for d in detections:
        sev = d.get("severity", "Unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    critical = severity_counts.get("Critical", 0)
    high = severity_counts.get("High", 0)

    if critical > 0:
        priority = "Inmediato"
    elif high > 0:
        priority = "Corto plazo"
    else:
        priority = "Largo plazo"

    defect_list = ", ".join(classes) if classes else "deterioro general"

    return {
        "executive_summary": (
            f"La inspección asistida por IA del activo tipo {asset_type} identificó "
            f"{len(detections)} instancias patológicas, incluyendo {defect_list}. "
            f"Se recomienda revisión profesional inmediata para los hallazgos críticos."
        ),
        "defect_descriptions": (
            f"El modelo de detección identificó los siguientes tipos de defectos: {defect_list}. "
            f"Estas patologías son características de los patrones típicos de deterioro observados "
            f"en infraestructuras de tipo {asset_type}. "
            f"Distribución: {', '.join(f'{k}: {v}' for k, v in severity_counts.items())}."
        ),
        "possible_causes": (
            "Las patologías detectadas pueden atribuirse a: exposición ambiental y ciclos de "
            "meteorización, carga mecánica y fatiga, envejecimiento del material y carbonatación, "
            "historial de mantenimiento inadecuado y/o deficiencias de diseño o construcción. "
            "Se requiere una investigación forense detallada para confirmar las causas raíz."
        ),
        "severity_assessment": (
            f"Basándose en las puntuaciones de confianza de la IA, la distribución de gravedad "
            f"de los defectos es la siguiente: "
            f"{', '.join(f'{k}: {v} instancias' for k, v in severity_counts.items())}. "
            f"Los hallazgos críticos y de alta gravedad requieren atención prioritaria."
        ),
        "risk_explanation": (
            f"Las patologías no tratadas en infraestructuras de tipo {asset_type} pueden provocar "
            f"deterioro progresivo, reducción de la capacidad estructural, riesgos de seguridad "
            f"para los usuarios y mayores costes de reparación. Los defectos críticos representan "
            f"un riesgo inmediato y deben abordarse con urgencia."
        ),
        "recommended_actions": (
            "1. Contratar a un ingeniero estructural colegiado para verificación in situ. "
            "2. Establecer perímetro de seguridad alrededor de las zonas con defectos críticos. "
            "3. Preparar especificaciones detalladas de reparación para las patologías identificadas. "
            "4. Implementar intervenciones de reparación específicas con materiales adecuados. "
            "5. Establecer programa de inspección rutinaria (intervalos de 6-12 meses). "
            "6. Documentar todos los hallazgos y acciones de reparación."
        ),
        "priority_level": priority,
        "final_conclusion": (
            f"Esta inspección asistida por IA del activo tipo {asset_type} identificó "
            f"{len(detections)} defectos que requieren atención profesional. "
            f"La clasificación de prioridad '{priority}' refleja la gravedad y distribución "
            f"de las patologías detectadas. Este informe debe utilizarse únicamente como "
            f"herramienta de cribado y debe ser validado por un ingeniero civil cualificado "
            f"antes de tomar cualquier decisión de reparación."
        )
    }