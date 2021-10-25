const { test, expect } = require("@playwright/test");
const { firefox } = require("playwright");

(async () => {
    const browser = await firefox.connect({ timeout: 0, wsEndpoint: "ws://20.103.25.207:4444/playwright/firefox" });
    const page = await browser.newPage();
    await page.goto("https://aerokube.com/moon/");
    console.log(await page.title());
    //await page.screenshot({ path: `screenshot.png` });
    await browser.close();
})();
