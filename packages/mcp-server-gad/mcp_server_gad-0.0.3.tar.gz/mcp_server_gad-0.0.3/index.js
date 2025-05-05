#!/usr/bin/env node

import { execa } from 'execa';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// 讀取 .env（可選）
dotenv.config();

// 處理 __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 取得資料庫參數
const dbUrl = process.argv[2] || process.env.DATABASE_URL;

if (!dbUrl) {
  console.error('[mcp-server-gad] ❌ Missing DATABASE_URL.');
  console.error('Usage: npx mcp-server-gad <DATABASE_URL>');
  process.exit(1);
}

// 安裝 Python 套件 + 執行模組
(async () => {
  try {
    const wheelPath = path.join(__dirname, 'dist', 'mcp_server_gad-0.0.2.tar.gz');
    console.log(`[mcp-server-gad] 📦 Installing Python package from ${wheelPath}`);
    
    await execa('pip', ['install', wheelPath], { stdio: 'inherit' });

    console.log(`[mcp-server-gad] 🚀 Starting MCP server...`);
    await execa('python3', ['-m', 'mcp_server_gad'], {
      stdio: 'inherit',
      env: {
        ...process.env,
        DATABASE_URL: dbUrl,
      }
    });
  } catch (err) {
    console.error('[mcp-server-gad] ❌ Failed to start:', err.message);
    process.exit(1);
  }
})();
