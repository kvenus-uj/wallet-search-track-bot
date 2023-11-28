import requests

# Replace with your GraphQL endpoint URL
graphql_endpoint_v2 = "https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v2-dev"

graphql_endpoint_v3 = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"


def get_swaps(trader_address, start_timestamp, version):
    try:
        graphql_query_v2 = """
            query {
            swaps(
              first:1000,orderBy: timestamp, orderDirection: desc,where:{ from:"{trader_address}",timestamp_gt:{start_timestamp}}
            ) {
                from
                transaction{
                    id
                    blockNumber
                    swaps{
                        id
                    }
                }                
                pair{
                  token0 {
                    id
                }
                token1 {
                    id
                  }
                }
                amount0In,
                amount0Out,
                amount1In,
                amount1Out,
                amountUSD
             }
            }   
        """

        graphql_query_v3 = """
            query {
            swaps(first:1000,orderBy: timestamp, orderDirection: desc,where:{ origin:"{trader_address}",timestamp_gt:{start_timestamp}}
            ) {

                origin
                transaction{
                    id
                    blockNumber
                    swaps{
                        id
                    }
                }                
                token0 {
                  id
                }
                token1 {
                  id
                }
                amount0
                amount1
                amountUSD
             }
            }   
        """

        graphql_query_v2 = graphql_query_v2.replace("{trader_address}", trader_address)
        graphql_query_v2 = graphql_query_v2.replace("{start_timestamp}", str(start_timestamp))
        graphql_query_v3 = graphql_query_v3.replace("{trader_address}", trader_address)
        graphql_query_v3 = graphql_query_v3.replace("{start_timestamp}", str(start_timestamp))

        query = graphql_query_v2 if version == 2 else graphql_query_v3
        endpoint = graphql_endpoint_v2 if version == 2 else graphql_endpoint_v3

        # Set up the headers for the request
        headers = {
            "Content-Type": "application/json",
        }

        # Create a dictionary with the GraphQL query
        graphql_request_data = {
            "query": query,
        }

        # Convert the dictionary to a JSON string
        r = requests.post(endpoint, json=graphql_request_data, headers=headers)
        json_data = r.json()
        swaps = json_data["data"]["swaps"]
        return swaps
    except Exception as error:
        print(error)
        return []


get_swaps("0xdb9aa7c0624d3cf65b0e081aa49a3e9fce2b6447", 0, 3)
