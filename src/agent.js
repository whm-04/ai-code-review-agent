const { OpenAI } = require('openai');
const { RecursiveCharacterTextSplitter } = require('langchain/text_splitter');
const { MemoryVectorStore } = require('langchain/vectorstores/memory');
const { OpenAIEmbeddings } = require('langchain/embeddings/openai');
const { RetrievalQAChain } = require('langchain/chains');
const { ChatOpenAI } = require('langchain/chat_models/openai');
const { PDFLoader } = require('langchain/document_loaders/fs/pdf');
const fs = require('fs');
const path = require('path');

class DocumentAgent {
  constructor() {
    this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    this.vectorStore = null;
    this.qaChain = null;
  }

  async initialize() {
    this.embeddings = new OpenAIEmbeddings();
    this.chatModel = new ChatOpenAI({ 
      modelName: 'gpt-4-turbo',
      temperature: 0.3 
    });
  }

  async loadDocument(filePath) {
    const loader = new PDFLoader(filePath);
    const docs = await loader.load();
    return docs;
  }

  async splitDocuments(documents) {
    const splitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
    const splitDocs = await splitter.splitDocuments(documents);
    return splitDocs;
  }

  async buildVectorStore(documents) {
    this.vectorStore = await MemoryVectorStore.fromDocuments(
      documents,
      this.embeddings
    );
    this.qaChain = RetrievalQAChain.fromLLM(
      this.chatModel,
      this.vectorStore.asRetriever()
    );
  }

  async summarizeDocument(documents) {
    const combinedText = documents.map(doc => doc.pageContent).join('\n\n');
    
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4-turbo',
      messages: [
        {
          role: 'system',
          content: '你是一个专业的文档摘要助手。请提供详细、准确的文档摘要，包括关键要点、结论和建议。'
        },
        {
          role: 'user',
          content: `请对以下文档进行详细摘要：\n\n${combinedText}`
        }
      ],
      max_tokens: 1500
    });

    return response.choices[0].message.content;
  }

  async answerQuestion(question) {
    if (!this.qaChain) {
      throw new Error('请先加载文档');
    }
    
    const result = await this.qaChain.call({
      query: question
    });
    
    return result.text;
  }

  async extractKeyPoints(documents) {
    const combinedText = documents.map(doc => doc.pageContent).join('\n\n');
    
    const response = await this.openai.chat.completions.create({
      model: 'gpt-4-turbo',
      messages: [
        {
          role: 'system',
          content: '你是一个专业的信息提取助手。请从文档中提取关键要点，以清晰的列表形式呈现。'
        },
        {
          role: 'user',
          content: `请从以下文档中提取关键要点：\n\n${combinedText}`
        }
      ],
      max_tokens: 1000
    });

    return response.choices[0].message.content;
  }

  async processDocument(filePath, options) {
    const { task = 'summarize' } = options;
    
    const documents = await this.loadDocument(filePath);
    const splitDocs = await this.splitDocuments(documents);
    
    await this.buildVectorStore(splitDocs);

    let result;
    switch (task) {
      case 'summarize':
        result = await this.summarizeDocument(documents);
        break;
      case 'extract':
        result = await this.extractKeyPoints(documents);
        break;
      case 'qa':
        result = await this.answerQuestion(options.question);
        break;
      default:
        result = await this.summarizeDocument(documents);
    }

    return {
      task,
      document: path.basename(filePath),
      content: result,
      tokenUsage: this.calculateTokenUsage(documents)
    };
  }

  calculateTokenUsage(documents) {
    const totalChars = documents.reduce((sum, doc) => sum + doc.pageContent.length, 0);
    const estimatedTokens = Math.floor(totalChars / 4);
    return {
      input: estimatedTokens,
      output: 500
    };
  }
}

module.exports = { DocumentAgent };