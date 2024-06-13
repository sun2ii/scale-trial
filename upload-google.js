const axios = require('axios');
require('dotenv').config();

knowledge_base = {
    'jpmorgan': '32cabd39-c257-493e-ab12-517905d4a800',
    'farmers': 'f682abae-a359-4025-884a-b5e19529e76f',
    'chegg': '1f8e6b89-5133-4fba-bfb1-fbb2e6213e0d',
    'bible': 'e35d10df-6b14-4cc4-876a-3083284f8316'
}

drive_folder = {
    'jpmorgan': '1dkhKsiw6bQsfivp_RHveub8-5FGwqMQ1',
    'farmers': '1efqrgcVUTWbZIZNIg1mLA2SB8LTI2ddy',
    'chegg': '1eKpXafk52As1jYkFMHYrI4eFSgJP5LMJ',
    'bible': '1Ga0oFzE6k3JzqLyadf4DRYKVCQ8skwWr'
}

const profile = 'chegg';
const drive_id = drive_folder[profile];
const knowledge_id = knowledge_base[profile];

const options = {
  method: 'POST',
  url: `https://api.egp.scale.com/v3/knowledge-bases/${knowledge_id}/uploads`,
  headers: {
    accept: 'application/json',
    'content-type': 'application/json',
    'x-api-key': process.env.API_KEY
  },
  data: {
    data_source_config: {source: 'GoogleDrive', drive_id: drive_id},
    data_source_auth_config: {
      encrypted: false,
      source: 'GoogleDrive',
      client_email: process.env.GOOGLE_CLIENT_EMAIL,
      private_key: process.env.GOOGLE_PRIVATE_KEY,
      token_uri: process.env.GOOGLE_TOKEN_URI,
      client_id: process.env.GOOGLE_CLIENT_ID
    },
    chunking_strategy_config: {strategy: 'character', separator: '\n\n', chunk_size: 1000, chunk_overlap: 200},
    force_reupload: false
  }
};

axios
  .request(options)
  .then(function (response) {
    console.log(response.data);
  })
  .catch(function (error) {
    console.error(error);
  });