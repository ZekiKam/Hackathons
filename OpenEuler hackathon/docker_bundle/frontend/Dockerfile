FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci || npm install

COPY . .

ARG VITE_API_BASE
ENV VITE_API_BASE=$VITE_API_BASE

RUN npm run build

EXPOSE 5173

ENV BROWSER=none

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
