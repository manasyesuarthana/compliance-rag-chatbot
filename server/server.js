const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const RAG_URL = process.env.RAG_SERVICE_URL || 'http://rag-engine:8000';

app.use(cors());
app.use(express.json());

//proxy Endpoint
app.use('/api/rag', createProxyMiddleware({
    target: RAG_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/rag': '' }, //removes /api/rag before sending to Python
    onProxyReq: (proxyReq, req, res) => {

        if (req.body) {
            const bodyData = JSON.stringify(req.body);
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
        }
    }
}));

app.listen(PORT, () => {
    console.log(`Middleware running on port ${PORT}`);
    console.log(`Proxying to: ${RAG_URL}`);
});