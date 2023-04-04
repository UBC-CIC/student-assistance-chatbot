let allMessages = [{type:1, content: "Hello, welcome to the UBC Student Assistant Chatbot! We are currently able to answer questions on the following topics:\n - General Academic Session Information\n - UBC Course Registration\n - UBC Course Requirements\n\n To get started, please ask the bot a question."}]

export const addMessage = (m) => {
    allMessages.push(m)
}
export const getMessage = () => {
   return allMessages
}

export {allMessages}
