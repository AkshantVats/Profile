#!/usr/bin/env python3
"""Verification test for OpenAI blog cover integration (no API calls)."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all required imports work."""
    try:
        from generate_covers_from_content import (
            image_prompt,
            cover_title,
            SERIES_LABEL,
            ACCENT,
            TOPIC_HINTS,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_prompt_generation():
    """Test prompt generation for sample slugs."""
    from generate_covers_from_content import image_prompt, SERIES_LABEL
    
    test_slugs = [
        "day-11-semantic-caching-vs-exact-match-redis",
        "building-tsdb-at-agoda",
        "building-ai-inference-observability",
    ]
    
    for slug in test_slugs:
        if slug not in SERIES_LABEL:
            print(f"❌ Slug not in SERIES_LABEL: {slug}")
            return False
        
        prompt = image_prompt(slug)
        
        # Validate prompt structure
        if len(prompt) < 100:
            print(f"❌ Prompt too short for {slug}: {len(prompt)} chars")
            return False
        
        if "1200×630" not in prompt:
            print(f"❌ Missing size spec in prompt for {slug}")
            return False
        
        badge = SERIES_LABEL[slug]
        if badge not in prompt:
            print(f"❌ Missing badge '{badge}' in prompt for {slug}")
            return False
        
        # Check NO day numbers constraint
        if "NO day numbers" not in prompt and "NO 'Day X of N'" not in prompt:
            print(f"❌ Missing 'NO day numbers' constraint in prompt for {slug}")
            return False
    
    print(f"✅ Prompt generation verified for {len(test_slugs)} slugs")
    return True


def test_function_signatures():
    """Test that new functions exist with correct signatures."""
    from generate_covers_from_content import generate_with_openai, run_generate
    import inspect
    
    # Check generate_with_openai
    sig = inspect.signature(generate_with_openai)
    if 'slug' not in sig.parameters:
        print("❌ generate_with_openai missing 'slug' parameter")
        return False
    
    # Check run_generate
    sig = inspect.signature(run_generate)
    if 'slugs' not in sig.parameters or 'install' not in sig.parameters:
        print("❌ run_generate missing required parameters")
        return False
    
    print("✅ Function signatures verified")
    return True


def test_styling_consistency():
    """Test that all slugs have required styling metadata."""
    from generate_covers_from_content import SERIES_LABEL, ACCENT, TOPIC_HINTS
    
    missing_accent = []
    missing_topics = []
    
    for slug in SERIES_LABEL:
        if slug not in ACCENT:
            missing_accent.append(slug)
        if slug not in TOPIC_HINTS:
            missing_topics.append(slug)
    
    if missing_accent:
        print(f"❌ Slugs missing ACCENT: {missing_accent}")
        return False
    
    if missing_topics:
        print(f"❌ Slugs missing TOPIC_HINTS: {missing_topics}")
        return False
    
    print(f"✅ Styling metadata complete for {len(SERIES_LABEL)} slugs")
    return True


def test_openai_sdk_available():
    """Test that OpenAI SDK is installed."""
    try:
        import openai
        from openai import OpenAI
        print(f"✅ OpenAI SDK installed (version: {openai.__version__})")
        return True
    except ImportError as e:
        print(f"❌ OpenAI SDK not installed: {e}")
        return False


def test_error_handling():
    """Test error handling for missing API key."""
    import os
    from generate_covers_from_content import generate_with_openai
    
    # Save original key if exists
    original_key = os.environ.get("OPENAI_API_KEY")
    
    try:
        # Remove key temporarily
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Should raise ValueError
        try:
            generate_with_openai("day-11-semantic-caching-vs-exact-match-redis")
            print("❌ Should have raised ValueError for missing API key")
            return False
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                print("✅ Error handling for missing API key works")
                return True
            else:
                print(f"❌ Wrong error message: {e}")
                return False
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def main():
    """Run all verification tests."""
    print("🧪 Running OpenAI integration verification tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Prompt Generation", test_prompt_generation),
        ("Function Signatures", test_function_signatures),
        ("Styling Consistency", test_styling_consistency),
        ("OpenAI SDK", test_openai_sdk_available),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 All verification tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
