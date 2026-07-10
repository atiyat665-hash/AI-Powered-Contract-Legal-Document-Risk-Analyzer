"""
Google Gemini API Service
Handles AI-powered contract analysis using Google's Gemini model
"""
import os
import json
import re
from typing import Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from prompts.analysis_prompts import (
    CONTRACT_ANALYSIS_PROMPT,
    RETRY_STRICT_PROMPT,
    RISK_DETECTION_PROMPT,
    RISK_RETRY_PROMPT,
    SUMMARY_PROMPT,
    SUMMARY_RETRY_PROMPT
)

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = "gemini-2.5-flash"
MAX_CONTRACT_LENGTH = 15000  # Characters to stay within token limits

# Initialize Gemini
_model = None


def initialize_gemini() -> bool:
    """
    Initialize the Gemini API with the API key.
    
    Returns:
        True if initialization successful, False otherwise
    """
    global _model
    
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(MODEL_NAME)
        print(f"✓ Gemini API initialized with model: {MODEL_NAME}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to initialize Gemini API: {e}")
        return False


def is_gemini_configured() -> bool:
    """
    Check if Gemini API is properly configured.
    
    Returns:
        True if API key is set, False otherwise
    """
    return GEMINI_API_KEY is not None and len(GEMINI_API_KEY) > 0


def strip_markdown_fences(text: str) -> str:
    """
    Remove markdown code fences from response.
    Gemini sometimes wraps JSON in ```json ... ``` despite instructions.
    
    Args:
        text: Raw response text
        
    Returns:
        Cleaned text without markdown fences
    """
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*\n?', '', text.strip())
    text = re.sub(r'\n?```\s*$', '', text.strip())
    return text.strip()


def truncate_contract_text(text: str, max_length: int = MAX_CONTRACT_LENGTH) -> str:
    """
    Truncate contract text to stay within token limits.
    Tries to cut at sentence boundaries for better context.
    
    Args:
        text: Full contract text
        max_length: Maximum character length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Try to cut at last sentence boundary
    truncated = text[:max_length]
    
    # Look for last period, exclamation, or question mark
    last_sentence_end = max(
        truncated.rfind('. '),
        truncated.rfind('.\n'),
        truncated.rfind('! '),
        truncated.rfind('? ')
    )
    
    if last_sentence_end > max_length * 0.8:  # If we found a good break point
        truncated = truncated[:last_sentence_end + 1]
    
    return truncated + "\n\n[... document truncated for analysis ...]"


def parse_json_response(response_text: str) -> Dict:
    """
    Parse JSON from Gemini response with error handling.
    
    Args:
        response_text: Raw response from Gemini
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        json.JSONDecodeError: If parsing fails
    """
    # Clean the response
    cleaned = strip_markdown_fences(response_text)
    
    # Try to parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        raise e


def analyze_contract(contract_text: str) -> Dict:
    """
    Analyze contract text using Google Gemini and extract structured information.
    
    Args:
        contract_text: Full text of the contract document
        
    Returns:
        Dictionary containing extracted contract information with fields:
        - contract_type, parties, effective_date, expiry_date, payment_terms,
          renewal_clause, termination_clause, confidentiality, responsibilities,
          jurisdiction, notice_period
        
        On error, returns dict with 'error' key and 'raw_response' for debugging
    """
    # Check if Gemini is configured
    if not is_gemini_configured():
        return {
            "error": "Gemini API not configured",
            "message": "GEMINI_API_KEY not found in environment variables. Please add your API key to the .env file.",
            "raw_response": None
        }
    
    # Initialize model if needed
    global _model
    if _model is None:
        if not initialize_gemini():
            return {
                "error": "Failed to initialize Gemini API",
                "message": "Could not initialize the Gemini model. Check your API key and internet connection.",
                "raw_response": None
            }
    
    try:
        # Truncate text if too long
        if len(contract_text) > MAX_CONTRACT_LENGTH:
            print(f"⚠️  Contract text truncated from {len(contract_text)} to {MAX_CONTRACT_LENGTH} characters")
            contract_text = truncate_contract_text(contract_text)
        
        # Fill prompt template
        prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=contract_text)
        
        print("📤 Sending contract to Gemini for analysis...")
        
        # Call Gemini API
        response = _model.generate_content(prompt)
        
        # Check if response was blocked
        if not response.text:
            if hasattr(response, 'prompt_feedback'):
                return {
                    "error": "Content blocked by safety filters",
                    "message": f"The response was blocked. Reason: {response.prompt_feedback}",
                    "raw_response": str(response.prompt_feedback)
                }
            return {
                "error": "Empty response from Gemini",
                "message": "Gemini returned an empty response. The content may have been filtered.",
                "raw_response": None
            }
        
        raw_response = response.text
        print(f"📥 Received response from Gemini ({len(raw_response)} characters)")
        
        # Try to parse JSON
        try:
            analysis_data = parse_json_response(raw_response)
            print("✓ Successfully parsed JSON response")
            return analysis_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse JSON on first attempt: {e}")
            print("🔄 Retrying with stricter instructions...")
            
            # Retry with stricter prompt
            retry_prompt = prompt + "\n\n" + RETRY_STRICT_PROMPT
            
            retry_response = _model.generate_content(retry_prompt)
            
            if not retry_response.text:
                return {
                    "error": "Invalid JSON response",
                    "message": "Gemini did not return valid JSON after retry",
                    "raw_response": raw_response
                }
            
            try:
                analysis_data = parse_json_response(retry_response.text)
                print("✓ Successfully parsed JSON on retry")
                return analysis_data
                
            except json.JSONDecodeError as e2:
                print(f"✗ Failed to parse JSON on retry: {e2}")
                return {
                    "error": "Invalid JSON response after retry",
                    "message": "Could not parse Gemini's response as valid JSON",
                    "raw_response": retry_response.text
                }
    
    except Exception as e:
        error_type = type(e).__name__
        print(f"✗ Error during contract analysis: {error_type}: {e}")
        
        # Provide helpful error messages for common issues
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            message = "API quota exceeded or rate limit reached. Please try again later or check your Gemini API quota."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            message = "Invalid API key. Please check your GEMINI_API_KEY in the .env file."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            message = "Network error. Please check your internet connection and try again."
        else:
            message = f"An error occurred during analysis: {str(e)}"
        
        return {
            "error": error_type,
            "message": message,
            "raw_response": str(e)
        }


def validate_risk_object(risk: Dict) -> bool:
    """
    Validate that a risk object has all required fields.
    
    Args:
        risk: Risk dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['risk_title', 'risk_level', 'confidence_score', 'explanation', 'recommendation']
    
    # Check all required fields exist
    if not all(field in risk for field in required_fields):
        return False
    
    # Validate risk_level
    if risk['risk_level'] not in ['High', 'Medium', 'Low']:
        return False
    
    # Validate confidence_score
    try:
        score = float(risk['confidence_score'])
        if not (0.0 <= score <= 1.0):
            return False
    except (ValueError, TypeError):
        return False
    
    # Validate string fields are not empty
    for field in ['risk_title', 'explanation', 'recommendation']:
        if not isinstance(risk[field], str) or not risk[field].strip():
            return False
    
    return True


def parse_json_array_response(response_text: str) -> list:
    """
    Parse JSON array from Gemini response with error handling.
    
    Args:
        response_text: Raw response from Gemini
        
    Returns:
        Parsed JSON as list
        
    Raises:
        json.JSONDecodeError: If parsing fails
    """
    # Clean the response
    cleaned = strip_markdown_fences(response_text)
    
    # Try to parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Try to find JSON array in the text
        json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        raise e


def detect_risks(contract_text: str, analysis_context: Optional[Dict] = None) -> list[Dict]:
    """
    Detect potential risks in a contract using Google Gemini.
    
    Args:
        contract_text: Full text of the contract document
        analysis_context: Optional structured analysis data for additional context
        
    Returns:
        List of risk dictionaries, each containing:
        - risk_title: Short descriptive name
        - risk_level: "High", "Medium", or "Low"
        - confidence_score: Float between 0.0 and 1.0
        - explanation: Why this is a risk
        - recommendation: How to mitigate it
        
        On error, returns list with a single error risk object
    """
    # Check if Gemini is configured
    if not is_gemini_configured():
        return [{
            "risk_title": "Configuration Error",
            "risk_level": "High",
            "confidence_score": 1.0,
            "explanation": "Gemini API is not configured. Cannot perform risk detection.",
            "recommendation": "Add your GEMINI_API_KEY to the .env file to enable AI risk detection."
        }]
    
    # Initialize model if needed
    global _model
    if _model is None:
        if not initialize_gemini():
            return [{
                "risk_title": "Initialization Error",
                "risk_level": "High",
                "confidence_score": 1.0,
                "explanation": "Failed to initialize Gemini API. Cannot perform risk detection.",
                "recommendation": "Check your API key and internet connection."
            }]
    
    try:
        # Truncate text if too long
        if len(contract_text) > MAX_CONTRACT_LENGTH:
            print(f"⚠️  Contract text truncated from {len(contract_text)} to {MAX_CONTRACT_LENGTH} characters")
            contract_text = truncate_contract_text(contract_text)
        
        # Prepare analysis context string
        context_str = "Not available"
        if analysis_context:
            try:
                # Format analysis context as readable text
                context_parts = []
                if analysis_context.get('contract_type'):
                    context_parts.append(f"Contract Type: {analysis_context['contract_type']}")
                if analysis_context.get('parties'):
                    parties = analysis_context['parties'] if isinstance(analysis_context['parties'], list) else [analysis_context['parties']]
                    context_parts.append(f"Parties: {', '.join(parties)}")
                if analysis_context.get('payment_terms'):
                    context_parts.append(f"Payment Terms: {analysis_context['payment_terms']}")
                if analysis_context.get('termination_clause'):
                    context_parts.append(f"Termination: {analysis_context['termination_clause']}")
                if analysis_context.get('renewal_clause'):
                    context_parts.append(f"Renewal: {analysis_context['renewal_clause']}")
                
                if context_parts:
                    context_str = "\n".join(context_parts)
            except Exception as e:
                print(f"⚠️  Error formatting analysis context: {e}")
                context_str = str(analysis_context)
        
        # Fill prompt template
        prompt = RISK_DETECTION_PROMPT.format(
            analysis_context=context_str,
            contract_text=contract_text
        )
        
        print("📤 Sending contract to Gemini for risk detection...")
        
        # Call Gemini API
        response = _model.generate_content(prompt)
        
        # Check if response was blocked
        if not response.text:
            if hasattr(response, 'prompt_feedback'):
                return [{
                    "risk_title": "Content Blocked",
                    "risk_level": "Medium",
                    "confidence_score": 1.0,
                    "explanation": f"The AI response was blocked by safety filters: {response.prompt_feedback}",
                    "recommendation": "Review the contract content for sensitive or inappropriate material."
                }]
            return [{
                "risk_title": "Empty Response",
                "risk_level": "Medium",
                "confidence_score": 1.0,
                "explanation": "Gemini returned an empty response during risk detection.",
                "recommendation": "Try again or check if the content triggered safety filters."
            }]
        
        raw_response = response.text
        print(f"📥 Received risk detection response from Gemini ({len(raw_response)} characters)")
        
        # Try to parse JSON array
        try:
            risks_list = parse_json_array_response(raw_response)
            
            # Validate it's a list
            if not isinstance(risks_list, list):
                print(f"⚠️  Response is not a list, got {type(risks_list)}")
                raise ValueError("Response is not a JSON array")
            
            # Validate and filter risk objects
            valid_risks = []
            for i, risk in enumerate(risks_list):
                if validate_risk_object(risk):
                    valid_risks.append(risk)
                else:
                    print(f"⚠️  Skipping invalid risk object at index {i}: {risk}")
            
            print(f"✓ Successfully parsed {len(valid_risks)} valid risk(s)")
            return valid_risks
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Failed to parse JSON on first attempt: {e}")
            print("🔄 Retrying with stricter instructions...")
            
            # Retry with stricter prompt
            retry_prompt = prompt + "\n\n" + RISK_RETRY_PROMPT
            
            retry_response = _model.generate_content(retry_prompt)
            
            if not retry_response.text:
                return [{
                    "risk_title": "Parsing Error",
                    "risk_level": "Medium",
                    "confidence_score": 0.8,
                    "explanation": "Failed to parse AI response after retry. The response may not be in valid JSON format.",
                    "recommendation": "Try running the risk detection again."
                }]
            
            try:
                risks_list = parse_json_array_response(retry_response.text)
                
                if not isinstance(risks_list, list):
                    raise ValueError("Retry response is not a JSON array")
                
                # Validate and filter risk objects
                valid_risks = []
                for i, risk in enumerate(risks_list):
                    if validate_risk_object(risk):
                        valid_risks.append(risk)
                    else:
                        print(f"⚠️  Skipping invalid risk object at index {i}: {risk}")
                
                print(f"✓ Successfully parsed {len(valid_risks)} valid risk(s) on retry")
                return valid_risks
                
            except (json.JSONDecodeError, ValueError) as e2:
                print(f"✗ Failed to parse JSON on retry: {e2}")
                return [{
                    "risk_title": "Analysis Error",
                    "risk_level": "Medium",
                    "confidence_score": 0.7,
                    "explanation": "Could not parse AI response as valid JSON after multiple attempts.",
                    "recommendation": "Review the contract manually for potential risks, or try again later."
                }]
    
    except Exception as e:
        error_type = type(e).__name__
        print(f"✗ Error during risk detection: {error_type}: {e}")
        
        # Provide helpful error messages
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            explanation = "API quota exceeded or rate limit reached during risk detection."
            recommendation = "Wait a few minutes and try again, or check your Gemini API quota."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            explanation = "Invalid API key during risk detection."
            recommendation = "Check your GEMINI_API_KEY in the .env file."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            explanation = "Network error during risk detection."
            recommendation = "Check your internet connection and try again."
        else:
            explanation = f"An error occurred during risk detection: {str(e)}"
            recommendation = "Try again or review the contract manually."
        
        return [{
            "risk_title": f"Risk Detection Error: {error_type}",
            "risk_level": "Medium",
            "confidence_score": 0.8,
            "explanation": explanation,
            "recommendation": recommendation
        }]


def generate_summary(contract_text: str, analysis_dict: Dict, risks_list: list[Dict]) -> Dict:
    """
    Generate an executive summary of the contract using Google Gemini.
    
    Args:
        contract_text: Full text of the contract document
        analysis_dict: Structured analysis data (contract type, parties, dates, etc.)
        risks_list: List of detected risks
        
    Returns:
        Dictionary containing:
        - executive_summary: Overview of the contract
        - key_obligations: List of obligations
        - important_dates: List of critical dates
        - important_clauses: List of important clauses
        - payment_summary: Payment terms summary
        - termination_summary: Termination terms summary
        - risk_summary: Overall risk profile
        - recommended_actions: List of next steps
        
        On error, returns dict with 'error' key
    """
    # Check if Gemini is configured
    if not is_gemini_configured():
        return {
            "error": "Gemini API not configured",
            "message": "GEMINI_API_KEY not found in environment variables.",
            "executive_summary": "Error: Cannot generate summary without API configuration.",
            "key_obligations": [],
            "important_dates": [],
            "important_clauses": [],
            "payment_summary": "Not available",
            "termination_summary": "Not available",
            "risk_summary": "Not available",
            "recommended_actions": ["Configure Gemini API key to enable summary generation"]
        }
    
    # Initialize model if needed
    global _model
    if _model is None:
        if not initialize_gemini():
            return {
                "error": "Failed to initialize Gemini API",
                "message": "Could not initialize the Gemini model.",
                "executive_summary": "Error: Failed to initialize AI model.",
                "key_obligations": [],
                "important_dates": [],
                "important_clauses": [],
                "payment_summary": "Not available",
                "termination_summary": "Not available",
                "risk_summary": "Not available",
                "recommended_actions": ["Check API key and internet connection"]
            }
    
    try:
        # Truncate text if too long
        if len(contract_text) > MAX_CONTRACT_LENGTH:
            print(f"⚠️  Contract text truncated from {len(contract_text)} to {MAX_CONTRACT_LENGTH} characters")
            contract_text = truncate_contract_text(contract_text)
        
        # Format analysis context
        analysis_context_str = "Not available"
        if analysis_dict:
            try:
                context_parts = []
                if analysis_dict.get('contract_type'):
                    context_parts.append(f"Contract Type: {analysis_dict['contract_type']}")
                if analysis_dict.get('parties'):
                    parties = analysis_dict['parties'] if isinstance(analysis_dict['parties'], list) else [analysis_dict['parties']]
                    context_parts.append(f"Parties: {', '.join(parties)}")
                if analysis_dict.get('effective_date'):
                    context_parts.append(f"Effective Date: {analysis_dict['effective_date']}")
                if analysis_dict.get('expiry_date'):
                    context_parts.append(f"Expiry Date: {analysis_dict['expiry_date']}")
                if analysis_dict.get('payment_terms'):
                    context_parts.append(f"Payment Terms: {analysis_dict['payment_terms']}")
                if analysis_dict.get('termination_clause'):
                    context_parts.append(f"Termination: {analysis_dict['termination_clause']}")
                if analysis_dict.get('jurisdiction'):
                    context_parts.append(f"Jurisdiction: {analysis_dict['jurisdiction']}")
                
                if context_parts:
                    analysis_context_str = "\n".join(context_parts)
            except Exception as e:
                print(f"⚠️  Error formatting analysis context: {e}")
                analysis_context_str = str(analysis_dict)
        
        # Format risks context
        risks_context_str = "No risks detected"
        if risks_list and len(risks_list) > 0:
            try:
                risk_parts = [f"Total Risks Found: {len(risks_list)}"]
                high_risks = sum(1 for r in risks_list if r.get('risk_level') == 'High')
                medium_risks = sum(1 for r in risks_list if r.get('risk_level') == 'Medium')
                low_risks = sum(1 for r in risks_list if r.get('risk_level') == 'Low')
                
                risk_parts.append(f"High: {high_risks}, Medium: {medium_risks}, Low: {low_risks}")
                risk_parts.append("\nKey Risks:")
                
                for i, risk in enumerate(risks_list[:5], 1):  # Top 5 risks
                    risk_parts.append(f"{i}. [{risk.get('risk_level', 'Unknown')}] {risk.get('risk_title', 'Unknown')}")
                
                risks_context_str = "\n".join(risk_parts)
            except Exception as e:
                print(f"⚠️  Error formatting risks context: {e}")
                risks_context_str = f"{len(risks_list)} risks detected"
        
        # Fill prompt template
        prompt = SUMMARY_PROMPT.format(
            analysis_context=analysis_context_str,
            risks_context=risks_context_str,
            contract_text=contract_text
        )
        
        print("📤 Sending contract to Gemini for summary generation...")
        
        # Call Gemini API
        response = _model.generate_content(prompt)
        
        # Check if response was blocked
        if not response.text:
            if hasattr(response, 'prompt_feedback'):
                return {
                    "error": "Content blocked",
                    "message": f"Response blocked: {response.prompt_feedback}",
                    "executive_summary": "Summary generation was blocked by content filters.",
                    "key_obligations": [],
                    "important_dates": [],
                    "important_clauses": [],
                    "payment_summary": "Not available",
                    "termination_summary": "Not available",
                    "risk_summary": "Not available",
                    "recommended_actions": ["Review contract content for sensitive material"]
                }
            return {
                "error": "Empty response",
                "message": "Gemini returned empty response",
                "executive_summary": "Could not generate summary - empty response from AI.",
                "key_obligations": [],
                "important_dates": [],
                "important_clauses": [],
                "payment_summary": "Not available",
                "termination_summary": "Not available",
                "risk_summary": "Not available",
                "recommended_actions": ["Try generating summary again"]
            }
        
        raw_response = response.text
        print(f"📥 Received summary response from Gemini ({len(raw_response)} characters)")
        
        # Try to parse JSON
        try:
            summary_dict = parse_json_response(raw_response)
            
            # Validate and fill missing fields with defaults
            required_fields = {
                'executive_summary': "Summary not available",
                'key_obligations': [],
                'important_dates': [],
                'important_clauses': [],
                'payment_summary': "Not specified in contract",
                'termination_summary': "Not specified in contract",
                'risk_summary': "Risk analysis not available",
                'recommended_actions': []
            }
            
            for field, default in required_fields.items():
                if field not in summary_dict or summary_dict[field] is None:
                    summary_dict[field] = default
                    print(f"⚠️  Missing field '{field}', using default")
            
            print("✓ Successfully parsed and validated summary")
            return summary_dict
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse JSON on first attempt: {e}")
            print("🔄 Retrying with stricter instructions...")
            
            # Retry with stricter prompt
            retry_prompt = prompt + "\n\n" + SUMMARY_RETRY_PROMPT
            
            retry_response = _model.generate_content(retry_prompt)
            
            if not retry_response.text:
                return {
                    "error": "Parsing error",
                    "message": "Failed to parse response after retry",
                    "executive_summary": "Could not generate summary - parsing error.",
                    "key_obligations": [],
                    "important_dates": [],
                    "important_clauses": [],
                    "payment_summary": "Not available",
                    "termination_summary": "Not available",
                    "risk_summary": "Not available",
                    "recommended_actions": ["Try generating summary again"]
                }
            
            try:
                summary_dict = parse_json_response(retry_response.text)
                
                # Validate and fill missing fields
                required_fields = {
                    'executive_summary': "Summary not available",
                    'key_obligations': [],
                    'important_dates': [],
                    'important_clauses': [],
                    'payment_summary': "Not specified in contract",
                    'termination_summary': "Not specified in contract",
                    'risk_summary': "Risk analysis not available",
                    'recommended_actions': []
                }
                
                for field, default in required_fields.items():
                    if field not in summary_dict or summary_dict[field] is None:
                        summary_dict[field] = default
                
                print("✓ Successfully parsed and validated summary on retry")
                return summary_dict
                
            except json.JSONDecodeError as e2:
                print(f"✗ Failed to parse JSON on retry: {e2}")
                return {
                    "error": "Invalid JSON",
                    "message": "Could not parse response as valid JSON after retry",
                    "executive_summary": "Could not generate summary - invalid response format.",
                    "key_obligations": [],
                    "important_dates": [],
                    "important_clauses": [],
                    "payment_summary": "Not available",
                    "termination_summary": "Not available",
                    "risk_summary": "Not available",
                    "recommended_actions": ["Try generating summary again"]
                }
    
    except Exception as e:
        error_type = type(e).__name__
        print(f"✗ Error during summary generation: {error_type}: {e}")
        
        # Provide helpful error messages
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            message = "API quota exceeded or rate limit reached."
            recommendation = "Wait a few minutes and try again."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            message = "Invalid API key."
            recommendation = "Check your GEMINI_API_KEY in the .env file."
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            message = "Network error."
            recommendation = "Check your internet connection and try again."
        else:
            message = f"An error occurred: {str(e)}"
            recommendation = "Try again or review the contract manually."
        
        return {
            "error": error_type,
            "message": message,
            "executive_summary": f"Error generating summary: {message}",
            "key_obligations": [],
            "important_dates": [],
            "important_clauses": [],
            "payment_summary": "Not available",
            "termination_summary": "Not available",
            "risk_summary": "Not available",
            "recommended_actions": [recommendation]
        }


def test_gemini_connection() -> tuple[bool, str]:
    """
    Test the Gemini API connection with a simple query.
    
    Returns:
        Tuple of (success, message)
    """
    if not is_gemini_configured():
        return False, "GEMINI_API_KEY not configured"
    
    try:
        if not initialize_gemini():
            return False, "Failed to initialize Gemini API"
        
        # Simple test query
        test_prompt = "Respond with only the word 'connected' in lowercase."
        response = _model.generate_content(test_prompt)
        
        if response.text and "connected" in response.text.lower():
            return True, "Gemini API connection successful"
        else:
            return True, f"API responded but with unexpected output: {response.text}"
            
    except Exception as e:
        return False, f"Connection test failed: {str(e)}"


def get_model_info() -> Dict:
    """
    Get information about the current Gemini model configuration.
    
    Returns:
        Dictionary with model information
    """
    return {
        "model_name": MODEL_NAME,
        "api_configured": is_gemini_configured(),
        "max_contract_length": MAX_CONTRACT_LENGTH,
        "api_key_prefix": GEMINI_API_KEY[:10] + "..." if GEMINI_API_KEY else None
    }
