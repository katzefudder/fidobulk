const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const { typeDefs, resolvers } = require('./graphql');
const { getAccessToken } = require('./auth');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT;

// Endpoint to fetch access token from Entra ID
app.post('/auth/token', async (req, res) => {
  const token = await getAccessToken();
  if (token) {
    console.log(access_token);
    res.json({ access_token: token });
  } else {
    res.status(500).json({ error: 'Failed to get token' });
  }
});

// app.use((req, res) => {
//   res.status(404).json({ error: 'Endpoint not found' });
// });

// GraphQL Server
const startApollo = async () => {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    context: ({ req }) => {
      const auth = req.headers.authorization || '';
      if (!auth.startsWith('Bearer ')) {
        throw new Error('Unauthorized');
      }

      const token = auth.replace('Bearer ', '');
      return { token };
    },
  });

  await server.start();
  server.applyMiddleware({ app });
};

startApollo().then(() => {
  app.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}/graphql`);
    console.log(`🔑 Get token at http://localhost:${PORT}/auth/token`);
  });
});
