#!/usr/bin/env python3
"""Verification test for blog cover generation workflow."""

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
    """Test that core functions exist with correct signatures."""
    from generate_covers_from_content import image_prompt, install_source, run_from_dir
    import inspect
    
    # Check image_prompt
    sig = inspect.signature(image_prompt)
    if 'slug' not in sig.parameters:
        print("❌ image_prompt missing 'slug' parameter")
        return False
    
    # Check install_source
    sig = inspect.signature(install_source)
    if 'slug' not in sig.parameters or 'src' not in sig.parameters:
        print("❌ install_source missing required parameters")
        return False
    
    # Check run_from_dir
    sig = inspect.signature(run_from_dir)
    if 'src_dir' not in sig.parameters:
        print("❌ run_from_dir missing required parameters")
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


def test_cursor_workflow():
    """Test that Cursor workflow documentation exists."""
    from pathlib import Path
    
    workflow_file = Path(__file__).parent / "CURSOR_COVER_WORKFLOW.md"
    readme_file = Path(__file__).parent / "README_COVER_GENERATION.md"
    
    if not workflow_file.exists():
        print(f"❌ CURSOR_COVER_WORKFLOW.md not found")
        return False
    
    if not readme_file.exists():
        print(f"❌ README_COVER_GENERATION.md not found")
        return False
    
    print("✅ Cursor workflow documentation exists")
    return True


def test_generated_dir_structure():
    """Test that generated directory structure is correct."""
    from pathlib import Path
    from generate_covers_from_content import GENERATED_DIR
    
    # Check GENERATED_DIR is properly defined
    if not isinstance(GENERATED_DIR, Path):
        print(f"❌ GENERATED_DIR not a Path object")
        return False
    
    expected_name = "cover_generated"
    if GENERATED_DIR.name != expected_name:
        print(f"❌ GENERATED_DIR should be named '{expected_name}', got '{GENERATED_DIR.name}'")
        return False
    
    print("✅ Generated directory structure correct")
    return True


def main():
    """Run all verification tests."""
    print("🧪 Running blog cover generation verification tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Prompt Generation", test_prompt_generation),
        ("Function Signatures", test_function_signatures),
        ("Styling Consistency", test_styling_consistency),
        ("Cursor Workflow", test_cursor_workflow),
        ("Directory Structure", test_generated_dir_structure),
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
