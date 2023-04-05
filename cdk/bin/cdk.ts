#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ubcStudentAssistantBot } from '../lib/cdk-stack';

const app = new cdk.App();
const cdkApp = new ubcStudentAssistantBot(app, 'ubcStudentAssistantBot', { env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION } });

const interactionsConfig = {
    Auth: {
        identityPoolId: cdkApp.lexCognitoPoolId,
        region: process.env.CDK_DEFAULT_REGION
    },
    Interactions: {
        bots: {
            // LexV2 Bot
            ubcStudentAssistantBot: {
                name: "ubcStudentAssistantBot",
                aliasId: cdkApp.lexBotAliasId,
                botId: cdkApp.lexBotId,
                localeId: "en_US",
                region: process.env.CDK_DEFAULT_REGION,
                providerName: "AWSLexV2Provider",
            },
        }
    }
}

export default interactionsConfig;