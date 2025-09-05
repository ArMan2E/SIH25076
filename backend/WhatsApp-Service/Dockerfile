# stage builder
FROM oven/bun:1.2.20 AS builder

#set the wrok dir
WORKDIR /app

#copy src to /app/src/ and package.json and bun.lockb to /app/
COPY package.json bun.lock ./
COPY src ./src

RUN bun install

# build the bun proj, explicitly --target bun runtime to specify run as server not in browser unlike jsx/tsx
# for server side always try --target bun
RUN bun build src/server.ts --target bun --outdir dist

# stage runtime

FROM oven/bun:latest AS runtime

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/bun.lock ./bun.lock

#no dev dependencies only prod dep
RUN bun install --production 

EXPOSE 8080

CMD [ "bun", "run", "dist/server.js"]
