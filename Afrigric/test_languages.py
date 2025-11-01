#!/usr/bin/env python3
"""Test script for language translations"""

from translations import get_text, SUPPORTED_LANGUAGES, get_recommendations

def test_translations():
    print("Testing language translations...")
    print("=" * 50)

    for lang in SUPPORTED_LANGUAGES:
        try:
            # Test basic translations
            home = get_text('home', lang)
            disease = get_text('disease', lang)
            pests = get_text('pests', lang)
            nutrients = get_text('nutrients', lang)
            yield_prediction = get_text('yield_prediction', lang)

            # Test recommendations for multiple problems
            problems_to_test = ['Gray_Leaf_Spot', 'Blight', 'Ants', 'Nitrogen Deficiency']
            translation_counts = 0

            for problem in problems_to_test:
                rec = get_recommendations(problem, lang)
                if rec is not None and 'description' in rec:
                    # Check if solutions are translated
                    if 'solutions' in rec and isinstance(rec['solutions'], list) and len(rec['solutions']) > 0:
                        # Check if the first solution looks translated (not English)
                        first_solution = str(rec['solutions'][0])
                        if lang == 'en' or not first_solution.startswith('Step 1:'):
                            translation_counts += 1

            has_rec = translation_counts > 0
            has_translated_solutions = translation_counts == len(problems_to_test)

            print(f"\n{lang} ({SUPPORTED_LANGUAGES[lang]}):")
            print(f"  Home: '{home}'")
            print(f"  Disease: '{disease}'")
            print(f"  Pests: '{pests}'")
            print(f"  Nutrients: '{nutrients}'")
            print(f"  Yield Prediction: '{yield_prediction}'")
            print(f"  Has Recommendations: {has_rec}")
            print(f"  Has Translated Solutions: {has_translated_solutions}")

            # Show first solution if translated
            if has_translated_solutions:
                first_solution = rec['solutions'][0][:50] + "..." if len(str(rec['solutions'][0])) > 50 else rec['solutions'][0]
                print(f"  First Solution Preview: '{first_solution}'")

        except Exception as e:
            print(f"{lang}: ERROR - {e}")

    print("\n" + "=" * 50)
    print("Language testing complete!")

if __name__ == "__main__":
    test_translations()