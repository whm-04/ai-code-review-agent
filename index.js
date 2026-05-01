require('dotenv').config();
const { DocumentAgent } = require('./src/agent');

async function main() {
  const agent = new DocumentAgent();
  await agent.initialize();
  
  const result = await agent.processDocument('./documents/sample.pdf', {
    task: 'summarize',
    options: { detailLevel: 'high' }
  });
  
  console.log('Document Processing Result:', result);
}

main().catch(console.error);