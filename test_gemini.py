"""
Test script for Gemini API integration
Tests connection and contract analysis functionality
"""
import os
from dotenv import load_dotenv
from services.gemini_service import (
    is_gemini_configured,
    test_gemini_connection,
    analyze_contract,
    get_model_info
)

# Load environment variables
load_dotenv()


def test_configuration():
    """Test if Gemini API is properly configured"""
    print("\n" + "="*60)
    print("TEST 1: Configuration Check")
    print("="*60)
    
    is_configured = is_gemini_configured()
    
    if is_configured:
        print("✓ GEMINI_API_KEY is configured")
        
        # Get model info
        info = get_model_info()
        print(f"✓ Model: {info['model_name']}")
        print(f"✓ Max contract length: {info['max_contract_length']} characters")
        print(f"✓ API key prefix: {info['api_key_prefix']}")
    else:
        print("✗ GEMINI_API_KEY not found in environment variables")
        print("\n⚠️  To configure:")
        print("1. Create or edit .env file")
        print("2. Add: GEMINI_API_KEY=your_key_here")
        print("3. Get key from: https://makersuite.google.com/app/apikey")
        return False
    
    return True


def test_connection():
    """Test connection to Gemini API"""
    print("\n" + "="*60)
    print("TEST 2: API Connection Test")
    print("="*60)
    
    print("🔄 Testing connection to Gemini API...")
    
    success, message = test_gemini_connection()
    
    if success:
        print(f"✓ {message}")
        return True
    else:
        print(f"✗ {message}")
        return False


def test_contract_analysis():
    """Test contract analysis with sample contract text"""
    print("\n" + "="*60)
    print("TEST 3: Contract Analysis")
    print("="*60)
    
    # Sample contract text
    sample_contract = """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024 ("Effective Date"),
by and between ABC Technologies Inc., a Delaware corporation ("Company"), and XYZ Consulting LLC,
a California limited liability company ("Consultant").

1. TERM
This Agreement shall commence on the Effective Date and continue for a period of twelve (12) months,
unless earlier terminated in accordance with Section 5 ("Term").

2. SERVICES
Consultant shall provide software development consulting services as described in Exhibit A.

3. COMPENSATION
Company shall pay Consultant a monthly fee of $10,000 USD, payable within 30 days of invoice receipt.

4. CONFIDENTIALITY
Both parties agree to maintain confidentiality of all proprietary information disclosed during the term
of this Agreement and for three (3) years thereafter.

5. TERMINATION
Either party may terminate this Agreement with sixty (60) days written notice. Upon termination,
Consultant shall return all Company materials.

6. RENEWAL
This Agreement shall automatically renew for successive one-year terms unless either party provides
written notice of non-renewal at least thirty (30) days prior to the end of the then-current Term.

7. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

ABC Technologies Inc.
By: John Smith, CEO

XYZ Consulting LLC
By: Jane Doe, Managing Partner
"""
    
    print("📄 Analyzing sample contract...")
    print(f"   Contract length: {len(sample_contract)} characters")
    
    # Analyze
    result = analyze_contract(sample_contract)
    
    # Check for errors
    if 'error' in result:
        print(f"\n✗ Analysis failed: {result['message']}")
        if result.get('raw_response'):
            print(f"\nRaw response:")
            print(result['raw_response'][:500])
        return False
    
    # Display results
    print("\n✓ Analysis successful!")
    print("\n📋 Extracted Information:")
    print("-" * 60)
    
    fields = [
        ('Contract Type', 'contract_type'),
        ('Parties', 'parties'),
        ('Effective Date', 'effective_date'),
        ('Expiry Date', 'expiry_date'),
        ('Payment Terms', 'payment_terms'),
        ('Renewal Clause', 'renewal_clause'),
        ('Termination Clause', 'termination_clause'),
        ('Confidentiality', 'confidentiality'),
        ('Responsibilities', 'responsibilities'),
        ('Jurisdiction', 'jurisdiction'),
        ('Notice Period', 'notice_period')
    ]
    
    for label, key in fields:
        value = result.get(key)
        if isinstance(value, list):
            print(f"\n{label}:")
            for item in value:
                print(f"  - {item}")
        elif value:
            # Truncate long values
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"\n{label}:")
            print(f"  {value}")
        else:
            print(f"\n{label}: Not specified")
    
    print("\n" + "-" * 60)
    
    return True


def test_json_parsing():
    """Test JSON parsing with various formats"""
    print("\n" + "="*60)
    print("TEST 4: JSON Parsing (Edge Cases)")
    print("="*60)
    
    from services.gemini_service import strip_markdown_fences, parse_json_response
    
    test_cases = [
        ("Plain JSON", '{"test": "value"}'),
        ("With markdown", '```json\n{"test": "value"}\n```'),
        ("With backticks", '```\n{"test": "value"}\n```'),
        ("With spaces", '  {"test": "value"}  '),
    ]
    
    for name, test_input in test_cases:
        try:
            result = parse_json_response(test_input)
            print(f"✓ {name}: {result}")
        except Exception as e:
            print(f"✗ {name}: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GEMINI API INTEGRATION TEST SUITE")
    print("="*60)
    
    # Test 1: Configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please configure GEMINI_API_KEY.")
        print("="*60 + "\n")
        return
    
    # Test 2: Connection
    if not test_connection():
        print("\n❌ Connection test failed. Check your API key and network.")
        print("="*60 + "\n")
        return
    
    # Test 3: Contract Analysis
    if not test_contract_analysis():
        print("\n❌ Contract analysis test failed.")
        print("="*60 + "\n")
        return
    
    # Test 4: JSON Parsing
    test_json_parsing()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\n✅ Gemini AI integration is working correctly!")
    print("\n📝 You can now run the app:")
    print("   streamlit run app.py")
    print("\n💡 Test the AI analysis by:")
    print("   1. Upload a contract document")
    print("   2. Extract text")
    print("   3. Click 'Analyze with AI'")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
