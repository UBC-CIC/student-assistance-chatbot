/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getFeedbackAPI = /* GraphQL */ `
  query GetFeedbackAPI($id: ID!) {
    getFeedbackAPI(id: $id) {
      feedback
      id
      messages
      rating
      createdAt
      updatedAt
    }
  }
`;
export const listFeedbackAPIS = /* GraphQL */ `
  query ListFeedbackAPIS(
    $filter: ModelFeedbackAPIFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listFeedbackAPIS(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        feedback
        id
        messages
        rating
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
