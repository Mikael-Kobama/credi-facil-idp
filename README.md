CrediFácil — Intelligent Document Processing para Análise de Crédito

🏆 1º lugar do júri no hackathon Hack2Hire (Escola da Nuvem), com avanço para fase de apresentação direta a empresas parceiras.

Plataforma de Processamento Inteligente de Documentos (IDP) que automatiza a extração, validação e análise de documentos financeiros, agilizando a tomada de decisão em processos de concessão de crédito.

Arquitetura 100% serverless na AWS: o pipeline usa AWS Lambda e Step Functions para orquestração, EventBridge para comunicação assíncrona entre componentes, e Amazon S3 para armazenamento dos documentos. A extração estruturada de dados é feita com Amazon Bedrock Data Automation (4 blueprints customizados), e a análise/geração do parecer de crédito usa Amazon Nova Pro com function calling.

No frontend, desenvolvido em React e Vite, o usuário acompanha o processamento em tempo real através de um terminal de logs, faz upload via drag-and-drop e visualiza o resultado em um dashboard de score de crédito.

Principais funcionalidades:
- Upload de documentos com feedback de progresso em tempo real
- Extração automática de dados a partir de documentos não estruturados
- Geração de parecer de crédito via IA generativa
- Pipeline rastreável de ponta a ponta
- Interface responsiva com tema claro/escuro

Stack: AWS Lambda · Step Functions · EventBridge · Amazon S3 · Amazon Bedrock Data Automation · Amazon Nova Pro · React · Vite

🔗 Repositório: github.com/Mikael-Kobama/credi-facil-idp
🔗 Demo: [adicionar link]
