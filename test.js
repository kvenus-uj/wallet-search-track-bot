const { Builder, By, Key, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
(async function getTopWalletAddress() {

    let options = new chrome.Options();
    options.addArguments("--headless");
    options.addArguments("--disable-gpu");
    options.addArguments("--window-size=1920x1080");
    options.addArguments("--disable-dev-shm-usage");
    options.addArguments("--no-sandbox");
    options.addArguments("--remote-debugging-port=9222");
    options.addArguments("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537");
    options.addArguments("--disable-blink-features");
    options.addArguments("--disable-blink-features=AutomationControlled");
    let driver = await new Builder().forBrowser("chrome").setChromeOptions(options).build();

    try {
        await driver.get('https://io.dexscreener.com/dex/log/amm/v2/uniswap/top/ethereum/0x1a1b82217094953c05c3fa7d2f134b360a82390c?q=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2');

        const data = await driver.getPageSource();
        let match;
        let matches = [];
        const regexPattern = /0x[a-fA-F0-9]{40}\b/g;
        while ((match = regexPattern.exec(data)) !== null) {
            matches.push(match[0]);

            if (matches.length === 10) {
                break;
            }
        }
        console.log(matches);
        return matches;
    } finally {
        await driver.quit();
    }
})();

