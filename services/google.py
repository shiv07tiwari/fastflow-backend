from googlesearch import search


def get_urls_for_search_query(company_name, num_results=10):
    query = f"{company_name} reviews"
    search_results = []

    for j in search(query, num=num_results):
        search_results.append(j)

    return search_results
