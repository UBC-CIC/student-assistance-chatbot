let lexCognitoPoolId = //YOUR COGNITO POOL ID
let region = //YOUR AWS REGION HERE
let lexBotId = //YOUR LEX BOT ID


const interactionsConfig = {
    Auth: {
        identityPoolId: lexCognitoPoolId,
        region: region
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: "TSTALIASID",
                botId: lexBotId,
                localeId: "en_US",
                region: region,
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;