const interactionsConfig = {
    Auth: {
        identityPoolId: process.env.LEX_COGNITO_POOL_ID,
        region: process.env.AWS_REGION
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: "TSTALIASID",
                botId: process.env.LEX_BOT_ID,
                localeId: "en_US",
                region: process.env.AWS_REGION,
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;