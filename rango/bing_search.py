import json
import requests

def read_bing_key():
    bing_api_key = None

    try:
        with open('bing.key.txt', 'r') as f:
            bing_api_key = f.readline().strip()
    except FileNotFoundError:
        try:
            with open('../bing.key') as f:
                bing_api_key = f.readline().strip()
        except FileNotFoundError:
            raise IOError('bing.key file not found')

    if not bing_api_key:
        raise KeyError('Bing key not found')

    return bing_api_key

def run_query(search_terms):
    try:
        bing_key = read_bing_key()
        search_url = 'https://api.bing.microsoft.com/v7.0/search'
        headers = {'Ocp-Apim-Subscription-Key': bing_key}
        params = {'q': search_terms, 'textDecorations': 'True', 'textFormat': 'HTML'}

        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        # Extract relevant information from the response
        results = [{'title': result.get('name', ''),
                    'link': result.get('url', ''),
                    'summary': result.get('snippet', '')}
                   for result in search_results.get('webPages', {}).get('value', [])]

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return None

if __name__ == "__main__":
    query = input("Enter your search query: ")

    if query:
        results = run_query(query)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Title: {result['title']}")
                print(f"Link: {result['link']}")
                print(f"Summary: {result['summary']}")
        else:
            print("No results or error occurred.")
    else:
        print("Please enter a valid search query.")
