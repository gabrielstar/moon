#init project
npm init -y
#install playwright
npm i -D @playwright/test
#install supproted browsers
npx playwright install
#run tests
npx playwright test --browser=chromium --headed