FROM nginx:1.27-alpine

WORKDIR /usr/share/nginx/html

COPY index.html ./index.html
COPY chat.html ./chat.html
COPY orb-chat-ui.css ./orb-chat-ui.css
COPY orb-chat-ui.js ./orb-chat-ui.js
COPY landing-orb.js ./landing-orb.js

EXPOSE 80
