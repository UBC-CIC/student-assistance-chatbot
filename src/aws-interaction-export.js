const interactionsConfig = {
    Auth: {
        identityPoolId: process.env.REACT_APP_LEX_COGNITO_POOL_ID,
        region: process.env.REACT_APP_AWS_REGION
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: "TSTALIASID",
                botId: process.env.REACT_APP_LEX_BOT_ID,
                localeId: "en_US",
                region: process.env.REACT_APP_AWS_REGION,
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;