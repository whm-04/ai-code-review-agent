const fs = require('fs');
const path = require('path');

function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function validateFilePath(filePath) {
  const validExtensions = ['.pdf', '.docx', '.txt'];
  const ext = path.extname(filePath).toLowerCase();
  
  if (!validExtensions.includes(ext)) {
    throw new Error(`不支持的文件格式: ${ext}`);
  }
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`文件不存在: ${filePath}`);
  }
  
  return true;
}

function formatResult(result) {
  return {
    timestamp: new Date().toISOString(),
    ...result
  };
}

function saveResultToFile(result, outputDir = './output') {
  ensureDirectoryExists(outputDir);
  
  const filename = `result_${Date.now()}.json`;
  const filePath = path.join(outputDir, filename);
  
  fs.writeFileSync(filePath, JSON.stringify(result, null, 2));
  return filePath;
}

module.exports = {
  ensureDirectoryExists,
  validateFilePath,
  formatResult,
  saveResultToFile
};