/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createFeedbackAPI = /* GraphQL */ `
  mutation CreateFeedbackAPI(
    $input: CreateFeedbackAPIInput!
    $condition: ModelFeedbackAPIConditionInput
  ) {
    createFeedbackAPI(input: $input, condition: $condition) {
      feedback
      id
      messages
      rating
      createdAt
      updatedAt
    }
  }
`;
export const updateFeedbackAPI = /* GraphQL */ `
  mutation UpdateFeedbackAPI(
    $input: UpdateFeedbackAPIInput!
    $condition: ModelFeedbackAPIConditionInput
  ) {
    updateFeedbackAPI(input: $input, condition: $condition) {
      feedback
      id
      messages
      rating
      createdAt
      updatedAt
    }
  }
`;
export const deleteFeedbackAPI = /* GraphQL */ `
  mutation DeleteFeedbackAPI(
    $input: DeleteFeedbackAPIInput!
    $condition: ModelFeedbackAPIConditionInput
  ) {
    deleteFeedbackAPI(input: $input, condition: $condition) {
      feedback
      id
      messages
      rating
      createdAt
      updatedAt
    }
  }
`;
