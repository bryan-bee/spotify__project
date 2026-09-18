# Two stages: build the React frontend with Node, then run the app with
# only Python + the already-built static files - the final image never
# needs Node installed at all, keeping it smaller.

FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend-build /app/frontend/build /app/frontend/build

ENV APP_ENV=production
# Render (and most platforms) assign the actual port via $PORT at runtime -
# this is just the conventional default for running it elsewhere.
ENV PORT=5000
EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT app:app
