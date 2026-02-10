FROM front-deps as build
WORKDIR /app

RUN chown -R node:node /app

COPY --from=front-deps /deps/node_modules /app/node_modules
COPY . .
RUN chmod -R 755 /app/node_modules
RUN npm run build

FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5173
CMD [ "nginx", "-g", "daemon off;" ]
