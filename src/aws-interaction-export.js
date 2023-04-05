const interactionsConfig = {
    Auth: {
        identityPoolId: "ca-central-1:d9039ad6-f9d8-4f9a-8114-66e79188f63a", //Change to your identity pool arn
        region: "ca-central-1" //Change to your region
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: "TSTALIASID",
                botId: "T5ALQLFKDU",  //Change to your bot's created ID
                localeId: "en_US",
                region: "ca-central-1", //Change to your region
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;