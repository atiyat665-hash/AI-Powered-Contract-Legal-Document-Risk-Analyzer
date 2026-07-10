"""
AI Prompt Templates for Contract Analysis
Engineered prompts for Google Gemini to extract structured data from contracts
"""

CONTRACT_ANALYSIS_PROMPT = """You are an expert legal contract analyzer. Your task is to carefully read the provided contract document and extract key information into a structured JSON format.

**INSTRUCTIONS:**
1. Read the contract text thoroughly
2. Extract the following information if present in the document
3. Return ONLY a valid JSON object with the specified fields
4. Do NOT include markdown code fences, explanations, or any text outside the JSON
5. If a field is not found or unclear in the document, use null for that field
6. Do NOT guess or hallucinate information - only extract what is explicitly stated
7. For lists (like parties), return an array of strings

**FIELDS TO EXTRACT:**

- contract_type: The type of contract (e.g., "Employment Agreement", "Service Agreement", "Lease Agreement", "NDA", etc.)
- parties: Array of party names involved in the contract (e.g., ["Company ABC Inc.", "John Doe"])
- effective_date: The date when the contract becomes effective (format: "YYYY-MM-DD" or as written if unclear)
- expiry_date: The date when the contract expires or terminates (format: "YYYY-MM-DD" or as written if unclear)
- payment_terms: Summary of payment terms, amounts, and schedules
- renewal_clause: Summary of automatic renewal or extension terms
- termination_clause: Summary of how and when the contract can be terminated
- confidentiality: Summary of confidentiality or non-disclosure obligations
- responsibilities: Summary of key responsibilities or obligations of each party
- jurisdiction: The governing law or jurisdiction mentioned (e.g., "State of California", "England and Wales")
- notice_period: Required notice period for termination or changes (e.g., "30 days", "60 days written notice")

**OUTPUT FORMAT:**
Return ONLY this JSON structure with no additional text:

{{
  "contract_type": "string or null",
  "parties": ["string1", "string2"] or null,
  "effective_date": "string or null",
  "expiry_date": "string or null",
  "payment_terms": "string or null",
  "renewal_clause": "string or null",
  "termination_clause": "string or null",
  "confidentiality": "string or null",
  "responsibilities": "string or null",
  "jurisdiction": "string or null",
  "notice_period": "string or null"
}}

**CONTRACT TEXT TO ANALYZE:**

{contract_text}

**REMEMBER:** Return ONLY the JSON object. No markdown, no explanations, no code fences."""


RETRY_STRICT_PROMPT = """
The previous response was not valid JSON. Please try again.

CRITICAL: Return ONLY a valid JSON object with no markdown formatting, no code fences (no ```json or ```), and no explanatory text.

Start your response with {{ and end with }}.

Extract the contract information and return it as pure JSON only.
"""


PARTIAL_ANALYSIS_PROMPT = """You are an expert legal contract analyzer. Extract the following specific information from the contract:

**FIELDS TO EXTRACT:**
{fields_to_extract}

**INSTRUCTIONS:**
- Return ONLY valid JSON
- No markdown, no code fences, no explanations
- Use null if a field is not found
- Do not guess or hallucinate

**CONTRACT TEXT:**
{contract_text}

Return only the JSON object."""


RISK_DETECTION_PROMPT = """You are an expert legal contract risk analyst. Your task is to identify potential risks, problems, and red flags in the provided contract document.

**INSTRUCTIONS:**
1. Read the contract text thoroughly
2. Optionally use the provided structured analysis as additional context
3. Identify risks in the following categories:
   - Missing critical clauses (termination, confidentiality, dispute resolution, liability caps, etc.)
   - High-risk conditions (unlimited liability, one-sided indemnification, unreasonable obligations)
   - Ambiguous or vague wording that could lead to disputes
   - Unfair or unusual payment terms (excessive fees, penalties, late charges)
   - Auto-renewal risks (difficult to cancel, automatic renewal without notice)
   - Penalty or liquidated damages risks (excessive or unclear penalties)
   - Jurisdiction and legal red flags (unfavorable jurisdiction, waiver of rights)
4. For EACH risk identified, create an object with these EXACT fields:
   - risk_title: Short descriptive name (e.g., "Unlimited Liability Clause")
   - risk_level: Must be exactly "High", "Medium", or "Low"
   - confidence_score: Float between 0.0 and 1.0 indicating how confident you are this is a risk
   - explanation: 1-2 sentences explaining WHY this is a risk
   - recommendation: 1-2 sentences on HOW to mitigate or address this risk
5. Return ONLY a valid JSON array of risk objects
6. Do NOT include markdown code fences, explanations, or any text outside the JSON
7. If no risks are found, return an empty array: []

**OUTPUT FORMAT:**
Return ONLY this JSON array structure with no additional text:

[
  {{
    "risk_title": "string",
    "risk_level": "High" | "Medium" | "Low",
    "confidence_score": 0.0 to 1.0,
    "explanation": "string",
    "recommendation": "string"
  }}
]

**STRUCTURED ANALYSIS CONTEXT (if available):**
{analysis_context}

**CONTRACT TEXT TO ANALYZE:**
{contract_text}

**REMEMBER:** 
- Return ONLY a JSON array of risk objects
- No markdown, no explanations, no code fences
- Start with [ and end with ]
- Each risk must have all 5 fields
- risk_level must be exactly "High", "Medium", or "Low"
- confidence_score must be between 0.0 and 1.0
- If no risks found, return []
"""


RISK_RETRY_PROMPT = """
The previous response was not a valid JSON array. Please try again.

CRITICAL: Return ONLY a valid JSON array with no markdown formatting, no code fences (no ```json or ```), and no explanatory text.

Start your response with [ and end with ].

Identify the contract risks and return them as a pure JSON array only.

If no risks are found, return an empty array: []
"""


SUMMARY_PROMPT = """You are an expert contract analyst preparing an executive summary for a business person who is not a lawyer.

**YOUR TASK:**
Generate a comprehensive yet clear executive summary of the contract using plain language. Avoid legal jargon. Be specific and actionable.

**CONTEXT PROVIDED:**

**Structured Analysis:**
{analysis_context}

**Detected Risks:**
{risks_context}

**CONTRACT TEXT:**
{contract_text}

**INSTRUCTIONS:**
1. Write in clear, business-friendly language (avoid legal jargon)
2. Be specific with dates, amounts, and terms
3. Focus on what matters most to the business person
4. Make the risk summary actionable
5. Provide concrete next steps
6. Return ONLY valid JSON with the exact structure below
7. Do NOT include markdown code fences, explanations, or any text outside the JSON

**OUTPUT FORMAT:**
Return ONLY this JSON structure with no additional text:

{{
  "executive_summary": "3-5 sentence plain-language overview of what this contract is, who the parties are, and its main purpose",
  "key_obligations": [
    "Short bullet point on what Party A must do",
    "Short bullet point on what Party B must do",
    "Additional key obligations..."
  ],
  "important_dates": [
    "Effective Date: [date] - when the contract begins",
    "Expiry Date: [date] - when the contract ends",
    "Notice Period: [period] - required notice for termination",
    "Other critical dates..."
  ],
  "important_clauses": [
    "Clause name/topic - one-line reason why it's important",
    "Another critical clause - why you should pay attention",
    "Additional important clauses..."
  ],
  "payment_summary": "2-3 sentence plain-language summary of payment amounts, frequency, and terms",
  "termination_summary": "2-3 sentence plain-language summary of how and when this contract can be terminated",
  "risk_summary": "2-3 sentence overview of the overall risk profile, mentioning key risks and their severity",
  "recommended_actions": [
    "Concrete action step 1 before signing",
    "Concrete action step 2 before signing",
    "Concrete action step 3 before signing",
    "Additional recommended actions..."
  ]
}}

**IMPORTANT:**
- All list fields (key_obligations, important_dates, important_clauses, recommended_actions) must be arrays of strings
- All text fields (executive_summary, payment_summary, termination_summary, risk_summary) must be strings
- Be specific: include actual dates, amounts, party names when available
- Write for clarity, not for legal precision
- If information is not available, use phrases like "Not specified in contract" rather than leaving fields empty
- Return ONLY the JSON object - no markdown, no explanations, no code fences
"""


SUMMARY_RETRY_PROMPT = """
The previous response was not valid JSON. Please try again.

CRITICAL: Return ONLY a valid JSON object with no markdown formatting, no code fences (no ```json or ```), and no explanatory text.

Start your response with {{ and end with }}.

Generate the executive summary and return it as pure JSON only.
"""
