#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ubcStudentAssistantBot } from '../lib/cdk-stack';

const app = new cdk.App();
new ubcStudentAssistantBot(app, 'ubcStudentAssistantBot', { env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION } });