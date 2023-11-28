const { ApolloClient } = require("apollo-boost");
const { fetch } = require("cross-fetch/polyfill");
const { InMemoryCache } = require("apollo-cache-inmemory");
const { createHttpLink } = require("apollo-link-http");

const subgraph = {
  1: {
    2: "https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v2-dev",
    3: "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
  },
};

module.exports = {
  tg_api: "6878353105:AAHYQ9ufibzvLRnf1vWr9SOx8Q0WvvGbFaQ",
  chat_id: -4072982727, //4085571318,
  morails_key:
    "3pPLbAJU77QC0ASflpRvGVCWEjHNSCpwT3k7OtrhSMo2iYo4Y2GykSLtQtlyfBYO",
  duneapikey: "umYKvUbhI4m7xCJMFmj7qQo0QNvozglu",
  etherscankey: "TQFRWS7IZAZTZE8XYXKCAI6R17BYISAP2D",
  apiUrl: "https://api.etherscan.io/api",
  wss: {
    [1]: "wss://mainnet.infura.io/ws/v3/c558761fd1204a879c54d5187f0ef53f",
  },
  providerUrl: "https://rpc.ankr.com/eth/709ed46cfa73f4def46d75a198bd5bc78fafa7dff95a4dc8c40d1af6660a4681",
  nodeProviderUrl: "https://eth.getblock.io/7c14aadb-9524-4852-a2c1-5036e1f9c6f4/mainnet/",

  APPOLO: (chainId, version) => {
    const defaultOptions = {
      watchQuery: {
        fetchPolicy: "no-cache",
        errorPolicy: "ignore",
      },
      query: {
        fetchPolicy: "no-cache",
        errorPolicy: "all",
      },
    };
    return new ApolloClient({
      link: createHttpLink({
        uri: subgraph[chainId][version],
        fetch: fetch,
      }),
      cache: new InMemoryCache(),
      defaultOptions: defaultOptions,
    });
  },
  launchtime: 24,
  minlp: 1,
  maxlp: 100,
  minbuys: 10,
  minsells: 10,
  limitMCap: 500000,
  pnlLimit: 1000,
  trade_ago_days: 60,
  minProfit: 5000,
  winRate: 70,
  minPnl: 3000,
  firstProfit: 2000,
};
