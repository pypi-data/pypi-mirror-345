import random
import requests

def get_random_gif(query: str, key) -> str:
    """
    Search for a random GIF using the Tenor API based on a search query.

    Parameters:
        query (str): The search term for the GIF.

    Returns:
        str: A URL to a randomly selected GIF.

    Raises:
        RuntimeError: If there are issues fetching the GIFs.
    """
    if not key:
        raise RuntimeError("Tenor API key is not set")

    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={key}&limit=10"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            raise RuntimeError("No GIFs found for that search term!")

        return random.choice(data['results'])['url']

    except requests.exceptions.RequestException as e:
        raise RuntimeError("Network error occurred.") from e
    except KeyError:
        raise RuntimeError("Unexpected API response format.")
    except Exception as e:
        raise RuntimeError("An unexpected error occurred.") from e

def main():
    query = input("Enter a search term for a GIF: ")
    TENOR_API_KEY = ''  # v2
    try:
        gif_url = get_random_gif(query, TENOR_API_KEY)
        print(gif_url)
    except RuntimeError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()