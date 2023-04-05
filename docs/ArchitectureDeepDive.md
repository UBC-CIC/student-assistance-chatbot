# Backend and Frontend Stack Deep Dive

## Architecture

![Architecture diagram](images/architectureDiagram.png)

## Description
### User/bot conversation flow (Blue)
1. The user sends a question to the chatbot. 
2. The text is parsed by Amplify before being passed to Lex. 
3. Lex continues to question the user for key data until the intent is fulfilled. Lex then triggers a Lambda function, sending all this key data (ex: course number, major, faculty, etc).
4. Lex execution logs are sent to CloudWatch for debugging purposes. 
5. The Lambda executed will choose a routine to run based on the understood Lex intent. This routine will query a specific Kendra index for the correct response. 
6. Lambda execution logs are sent to CloudWatch for debugging purposes. 
7. Data stored in Kendra indices are originated from S3 buckets populated by web-scraping. 
8. Kendra returns the unformatted data back to the Lambda handler. 
9. The Lambda handler formats the answer and returns it back to Lex.
10. Lex passes the answer back to Amplify where it is displayed in the frontend. 
### Submitting feedback flow (Green)
1. The user sends feedback through the chatbot interface. 
2. Amplify sends feedback to AppSync via an API call.
3. AppSync saves the rating and comments into the DynamoDB feedback table. This also includes a log of the conversation for reference. 
4. System admin can view all the feedback by logging into the admin account through the chatbot interface. 

## GraphQL Schema
Our application backend works around `AWS AppSync`, a serverless `GraphQL` API service. With each call to the AppSync GraphQL API a `resolver` is triggered which will trigger the `AWS DynamoDB` API. This resolver will submit the request to the application's `DynamoDB` instance. To add an `AWS AppSync` service to your `AWS Amplify` app, you can follow the instructions [here](https://docs.amplify.aws/lib/graphqlapi/getting-started/q/platform/js/#create-the-graphql-api). 

For our application, the `schema` is defined as follows.

```
id: ID!
feedback: String
messages: AWSJSON
rating: Int
```

- The `id` field is a mandatory field and is created in the application code when a feedback object is created.
- The `feedback` field contains a user's comments, if any, about their chatbot experience and potential improvement areas.
- The `messages` field contains a list of messages that was sent between the user and our chatbot, such that future developers can utilize the feedback provided by the user to improve the chatbot interface.
- The `rating` field contains the user's rating that they can enter on the UI. This rating value will range between 1 and 5.

