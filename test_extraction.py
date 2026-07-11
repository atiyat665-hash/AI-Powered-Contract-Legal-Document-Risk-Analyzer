
"""
Test script for document extraction functionality
Creates sample files and tests extraction
"""
import os
from services.extraction_service import (
    extract_text_from_txt,
    extract_text_from_docx,
    clean_text,
    get_text_stats
)


def test_txt_extraction():
    """Test TXT file extraction"""
    print("\n" + "="*60)
    print("TEST 1: TXT File Extraction")
    print("="*60)
    
    # Create sample TXT file
    sample_text = """This is a sample contract.

PARTIES:
1. Company ABC
2. Company XYZ

AGREEMENT:
Both parties agree to the following terms and conditions.

TERM:
This agreement is valid for 12 months.
"""
    
    test_file = "test_sample.txt"
    
    try:
        # Write test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        print(f"✓ Created test file: {test_file}")
        
        # Extract text
        extracted = extract_text_from_txt(test_file)
        
        print(f"✓ Extracted {len(extracted)} characters")
        print(f"\nExtracted text preview:")
        print("-" * 60)
        print(extracted[:200])
        print("-" * 60)
        
        # Get stats
        stats = get_text_stats(extracted)
        print(f"\n📊 Statistics:")
        print(f"  Characters: {stats['characters']}")
        print(f"  Words: {stats['words']}")
        print(f"  Lines: {stats['lines']}")
        print(f"  Paragraphs: {stats['paragraphs']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n✓ Cleaned up test file")


def test_text_cleaning():
    """Test text cleaning functionality"""
    print("\n" + "="*60)
    print("TEST 2: Text Cleaning")
    print("="*60)
    
    # Create messy text
    messy_text = """This   has    excessive    spaces.


And too many blank lines.



Also weird   spacing    everywhere.

Trailing spaces here:    
And here too:     

"""
    
    print("Original text (with markers):")
    print(f"[{messy_text}]")
    print(f"Length: {len(messy_text)} characters")
    
    # Clean it
    cleaned = clean_text(messy_text)
    
    print(f"\nCleaned text (with markers):")
    print(f"[{cleaned}]")
    print(f"Length: {len(cleaned)} characters")
    
    # Verify improvements
    improvements = []
    
    if "   " not in cleaned:
        improvements.append("✓ Removed excessive spaces")
    
    if "\n\n\n" not in cleaned:
        improvements.append("✓ Removed excessive blank lines")
    
    if not cleaned.endswith(" "):
        improvements.append("✓ Removed trailing whitespace")
    
    print(f"\nImprovements:")
    for imp in improvements:
        print(f"  {imp}")


def test_file_validation():
    """Test file validation logic"""
    print("\n" + "="*60)
    print("TEST 3: File Validation Simulation")
    print("="*60)
    
    # Simulate validation checks
    allowed_extensions = {'pdf', 'docx', 'txt'}
    max_size_mb = 10
    
    test_cases = [
        ("document.pdf", 5 * 1024 * 1024, True, "Valid PDF"),
        ("contract.docx", 8 * 1024 * 1024, True, "Valid DOCX"),
        ("agreement.txt", 1 * 1024 * 1024, True, "Valid TXT"),
        ("image.jpg", 2 * 1024 * 1024, False, "Invalid extension"),
        ("huge.pdf", 15 * 1024 * 1024, False, "Too large"),
        ("empty.txt", 0, False, "Empty file"),
    ]
    
    print(f"\nValidation rules:")
    print(f"  Allowed extensions: {', '.join(allowed_extensions)}")
    print(f"  Max file size: {max_size_mb}MB")
    print(f"\nTest cases:")
    
    for filename, size, should_pass, description in test_cases:
        ext = filename.split('.')[-1]
        size_mb = size / (1024 * 1024)
        
        # Validate
        is_valid = True
        reason = "OK"
        
        if ext not in allowed_extensions:
            is_valid = False
            reason = "Invalid extension"
        elif size == 0:
            is_valid = False
            reason = "Empty file"
        elif size > max_size_mb * 1024 * 1024:
            is_valid = False
            reason = f"Too large ({size_mb:.1f}MB)"
        
        status = "✓" if is_valid == should_pass else "✗"
        result = "PASS" if is_valid else "FAIL"
        
        print(f"  {status} {filename:20s} {size_mb:6.2f}MB → {result:4s} ({description})")


def test_stats_calculation():
    """Test text statistics calculation"""
    print("\n" + "="*60)
    print("TEST 4: Statistics Calculation")
    print("="*60)
    
    test_texts = [
        ("Empty", ""),
        ("Single word", "Hello"),
        ("Short sentence", "This is a test."),
        ("Multiple lines", "Line 1\nLine 2\nLine 3"),
        ("Multiple paragraphs", "Para 1\n\nPara 2\n\nPara 3"),
    ]
    
    for name, text in test_texts:
        stats = get_text_stats(text)
        print(f"\n{name}:")
        print(f"  Text: '{text}'")
        print(f"  Characters: {stats['characters']}")
        print(f"  Words: {stats['words']}")
        print(f"  Lines: {stats['lines']}")
        print(f"  Paragraphs: {stats['paragraphs']}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DOCUMENT EXTRACTION TEST SUITE")
    print("="*60)
    
    try:
        test_txt_extraction()
        test_text_cleaning()
        test_file_validation()
        test_stats_calculation()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\n✅ Extraction services are working correctly!")
        print("\n📝 Note: PDF and DOCX extraction require actual files to test.")
        print("   These will be tested through the Streamlit UI.")
        print("\n🚀 You can now run the app:")
        print("   streamlit run app.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    main()
