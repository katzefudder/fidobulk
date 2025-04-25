const { gql } = require('apollo-server-express');

const typeDefs = gql`
  type Query {
    users: [User!]!
    groups: [Group!]!
  }

  type User {
    id: ID!
    displayName: String!
    email: String!
  }

  type Group {
    id: ID!
    displayName: String!
    members: [User!]!
  }
`;

const users = [
  { id: '1', displayName: 'Alice Smith', email: 'alice@example.com' },
  { id: '2', displayName: 'Bob Jones', email: 'bob@example.com' },
  { id: '3', displayName: 'Charlie Johnson', email: 'charlie@example.com' },
  { id: '4', displayName: 'Diana Lee', email: 'diana@example.com' },
  { id: '5', displayName: 'Ethan Kim', email: 'ethan@example.com' },
  { id: '6', displayName: 'Fiona Brown', email: 'fiona@example.com' },
  { id: '7', displayName: 'George White', email: 'george@example.com' },
  { id: '8', displayName: 'Hannah Scott', email: 'hannah@example.com' },
  { id: '9', displayName: 'Ian Clark', email: 'ian@example.com' },
  { id: '10', displayName: 'Julia Adams', email: 'julia@example.com' },
  { id: '11', displayName: 'Kevin Turner', email: 'kevin@example.com' },
];

const groups = [
  //{ id: 'g1', displayName: 'Admins', members: [users[0]] },
  { id: 'g1', displayName: 'Users', members: users },
];

const resolvers = {
  Query: {
    users: () => users,
    groups: () => groups,
  },
};

module.exports = { typeDefs, resolvers };
