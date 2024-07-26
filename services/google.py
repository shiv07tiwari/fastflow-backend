from googlesearch import search


def get_urls_for_search_query(company_name, num_results=10):
    """
    This uses a very basic wrapper around google search.
    Need to replace this with serper in future
    """
    query = f"{company_name} reviews"
    search_results = []
    try:
        for j in search(query, stop=num_results):
            print("Found URL from Google: ", j)
            search_results.append(j)

        return search_results
    except Exception as e:
        return []
