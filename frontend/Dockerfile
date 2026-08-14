# ---------------------------------------------------------------------------
# Estágio 1 — build dos arquivos estáticos
# ---------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# package.json e lock primeiro, sozinhos: assim a camada do `npm ci` só é
# refeita quando as dependências mudam, não a cada alteração de código.
COPY package.json package-lock.json ./
# `npm ci` (e não `install`) instala exatamente o que está no lock — build
# reproduzível, que é o ponto de versionar o package-lock.json.
RUN npm ci

COPY . .

# ATENÇÃO: o Vite injeta as variáveis VITE_* em tempo de BUILD, substituindo
# no código gerado — não são lidas em tempo de execução. Por isso vem como
# ARG e não como variável de ambiente do container.
# O padrão "/api" faz o frontend chamar o próprio domínio, onde o nginx faz
# proxy para o backend (ver nginx.conf).
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ---------------------------------------------------------------------------
# Estágio 2 — servir
# ---------------------------------------------------------------------------
# Imagem "unprivileged": roda como usuário sem privilégios (uid 101) em vez
# de root, mesma disciplina dos outros serviços do projeto.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
# Só o resultado do build entra na imagem final: nada de node_modules,
# código-fonte ou o próprio Node.
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080
