const { prepareData } = require("./prepare_data");
const cron = require('node-cron');
require('events').EventEmitter.defaultMaxListeners = 15;

async function start() {
  prepareData();
  cron.schedule('*/120 * * * *', () => {
    prepareData();
  });
}
start();

