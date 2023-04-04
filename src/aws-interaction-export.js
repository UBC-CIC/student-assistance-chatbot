const interactionsConfig = {
    Auth: {
        identityPoolId: "ca-central-1:d9039ad6-f9d8-4f9a-8114-66e79188f63a",
        region: "ca-central-1"
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: "TSTALIASID",  //Change to your bot's alias ID
                botId: "T5ALQLFKDU",  //Change to your bot's created ID
                localeId: "en_US",
                region: "ca-central-1",
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;
