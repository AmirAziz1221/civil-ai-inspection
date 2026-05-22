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

SYSTEM_PROMPT = """You are a professional civil engineering inspection assistant.
Your role is to generate clear, formal, and practical inspection reports based on AI detection results.
Always write in professional civil engineering language.
Always mention that results should be verified by a qualified civil engineer.
Respond ONLY with a valid JSON object, no markdown, no extra text."""

REPORT_PROMPT_TEMPLATE = """Generate a detailed civil engineering inspection report based on these AI detection results.

Client name: Dani
Asset type: {asset_type}
Model used: {model_name}
Total defects detected: {total_defects}

Detected pathologies (JSON):
{detections_json}

Engineer notes:
{engineer_notes}

Return a JSON object with these exact keys:
{{
  "executive_summary": "2-3 sentence overview of findings",
  "defect_descriptions": "Detailed description of each detected defect type",
  "possible_causes": "Technical analysis of likely causes for the detected pathologies",
  "severity_assessment": "Assessment of defect severity with engineering justification",
  "risk_explanation": "Explanation of risks to structural integrity and safety",
  "recommended_actions": "Specific, prioritized repair and maintenance actions",
  "priority_level": "Immediate / Short-term / Long-term",
  "final_conclusion": "Professional conclusion and next steps"
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
    """Template-based fallback when LLM is not available."""
    classes = list({d["class"] for d in detections})
    severity_counts = {}
    for d in detections:
        sev = d.get("severity", "Unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    critical = severity_counts.get("Critical", 0)
    high = severity_counts.get("High", 0)

    if critical > 0:
        priority = "Immediate"
    elif high > 0:
        priority = "Short-term"
    else:
        priority = "Long-term"

    defect_list = ", ".join(classes) if classes else "general deterioration"

    return {
        "executive_summary": (
            f"AI-assisted inspection of {asset_type} identified {len(detections)} pathological instances "
            f"including {defect_list}. Immediate professional review is recommended for critical findings."
        ),
        "defect_descriptions": (
            f"The detection model identified the following defect types: {defect_list}. "
            f"These pathologies are characteristic of typical deterioration patterns observed in {asset_type} infrastructure. "
            f"Distribution: {', '.join(f'{k}: {v}' for k, v in severity_counts.items())}."
        ),
        "possible_causes": (
            "Detected pathologies may be attributed to: environmental exposure and weathering cycles, "
            "mechanical loading and fatigue, material aging and carbonation, inadequate maintenance history, "
            "and/or design or construction deficiencies. A detailed forensic investigation is required to "
            "confirm root causes."
        ),
        "severity_assessment": (
            f"Based on AI confidence scores, defect severity distribution is as follows: "
            f"{', '.join(f'{k}: {v} instances' for k, v in severity_counts.items())}. "
            f"Critical and high-severity findings require priority attention."
        ),
        "risk_explanation": (
            "Unaddressed pathologies in {asset_type} infrastructure may lead to progressive deterioration, "
            "reduced structural capacity, safety hazards for users, and increased remediation costs. "
            "Critical defects pose immediate risk and must be addressed urgently.".format(asset_type=asset_type)
        ),
        "recommended_actions": (
            "1. Engage a licensed structural engineer for on-site verification. "
            "2. Establish safety perimeter around critical defect zones. "
            "3. Prepare detailed repair specification for identified pathologies. "
            "4. Implement targeted repair interventions using appropriate materials. "
            "5. Establish routine inspection schedule (6–12 month intervals). "
            "6. Document all findings and remediation actions."
        ),
        "priority_level": priority,
        "final_conclusion": (
            f"This AI-assisted inspection of {asset_type} identified {len(detections)} defects requiring "
            f"professional attention. The {priority.lower()} priority classification reflects the severity "
            f"and distribution of detected pathologies. This report should be used as a screening tool only "
            f"and must be validated by a qualified civil engineer before any remediation decisions are made."
        )
    }
