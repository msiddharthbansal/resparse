import json
from src.services.orchestrator import orchestrator

with open('data/sample_queries.json', 'r') as f:
    test_data = json.load(f)

test_queries = test_data['test_queries']

print("Testing RESPARSE System\n")

for i, test in enumerate(test_queries, 1):
    query = test['query']
    expected_categories = test.get('expected_categories', [])
    
    print(f"\n{i}. Query: '{query}'")
    print(f"   Expected categories: {expected_categories}")
    try:
        results = orchestrator.search(query, use_cache=False)
        
        found_categories = [c['category_name'] for c in results['categories']]
        print(f"Found categories: {found_categories}")
        print(f"Candidates evaluated: {results['total_candidates']}")
        print(f"Results returned: {len(results['results'])}")
        
        if results['results']:
            top_result = results['results'][0]
            print(f"\nTop Result:")
            print(f"      Title: {top_result['title'][:80]}...")
            print(f"      Journal: {top_result['journal']['name']} ({top_result['journal']['quartile']})")
            print(f"      JIF: {top_result['journal']['jif']:.1f}")
            print(f"      Year: {top_result['publication']['year']}")
            print(f"      Semantic Score: {top_result['scores']['semantic']:.2%}")
            print(f"      Final Score: {top_result['scores']['final']:.3f}")
            print(f"\nExplanation: {top_result['explanation'][:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")
    

print("\nTesting complete!")
