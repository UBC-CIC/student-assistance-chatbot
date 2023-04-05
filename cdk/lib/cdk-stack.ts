import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cr from 'aws-cdk-lib/custom-resources';
import * as kendra from 'aws-cdk-lib/aws-kendra';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class ubcStudentAssistantBot extends cdk.Stack {
  public readonly lexBotId: string;
  public readonly lexBotAliasId: string;
  public readonly courseIndexId: string;
  public readonly calendarIndexId: string;
  public readonly s3BucketId: string;
  public readonly lexCognitoPoolId: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    //Create lex custom role
    const lexCustomResourceRole = new iam.Role(this, 'lexCustomResourceRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      inlinePolicies: {
        ['lambdaPolicy']: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: ['*'],
              actions: [
                'lex:UpdateSlot',
                'lex:ListBots',
                'lex:UpdateBotAlias',
                'lex:DeleteCustomVocabulary',
                'lex:DeleteBotVersion',
                'lex:DeleteBotChannel',
                'lex:CreateResourcePolicy',
                'lex:UpdateBotLocale',
                'lex:ListBotAliases',
                'lex:CreateCustomVocabulary',
                'lex:CreateBotLocale',
                'lex:DeleteIntent',
                'lex:StartImport',
                'lex:UpdateSlotType',
                'lex:BuildBotLocale',
                'lex:CreateBot',
                'lex:DeleteBotAlias',
                'lex:CreateIntent',
                'lex:CreateUploadUrl',
                'lex:DeleteBot',
                'lex:CreateBotAlias',
                'lex:CreateSlotType',
                'lex:DeleteBotLocale',
                'lex:UpdateCustomVocabulary',
                'lex:UpdateResourcePolicy',
                'lex:CreateSlot',
                'lex:DeleteSlot',
                'lex:UpdateBot',
                'lex:DeleteSlotType',
                'lex:UpdateIntent',
                'lex:DeleteResourcePolicy',
                'iam:PassRole',
              ],
            }),
          ],
        }),
      },
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaBasicExecutionRole',
        ),
      ],
    });

    //import lex bot to deploy to customer account
    const lexDeployLambda = new lambda.Function(this, 'lexDeployLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      code: lambda.Code.fromAsset(path.join(__dirname, '../resources/lexBot')),
      handler: 'index.handler',
      architecture: lambda.Architecture.ARM_64,
      timeout: cdk.Duration.minutes(1),
      role: lexCustomResourceRole,
    });

    //Create lex service role
    const lexRole = new iam.Role(this, 'lexRole', {
      assumedBy: new iam.ServicePrincipal('lexv2.amazonaws.com'),
      inlinePolicies: {
        ['lexPolicy']: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: ['*'],
              actions: ['polly:SynthesizeSpeech', 'comprehend:DetectSentiment'],
            }),
          ],
        }),
      },
    });

    //Unique name for lex bot
    const uid: string = cdk.Names.uniqueId(this);;

    const LexResourceProvider = new cr.Provider(this, 'LexResourceProvider', {
      onEventHandler: lexDeployLambda,
    });

    //Create lex bot from zip file
    const lexBot = new cdk.CustomResource(this, 'LexCustomResource', {
      serviceToken: LexResourceProvider.serviceToken,
      properties: { uid: uid, lex_role_arn: lexRole.roleArn },
    });

    //Set lexbotid and lexaliasid
    new cdk.CfnOutput(this, 'bot_id', { value: lexBot.getAttString('bot_id') });
    new cdk.CfnOutput(this, 'bot_alias_id', { value: lexBot.getAttString('bot_alias_id') });

    this.lexBotId = lexBot.getAttString('bot_id');
    this.lexBotAliasId = lexBot.getAttString('bot_alias_id');

    //Create kendra IAM role and policies
    const kendraCloudWatchStatement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources:['*'],
      actions: ['cloudwatch:PutMetricData'],
    });
    kendraCloudWatchStatement.addCondition('StringEquals', {"cloudwatch:namespace": "AWS/Kendra"});

    const kendraIamPassRoleStatement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      resources: ['*'],
      actions: ['iam:PassRole']
    });
    kendraIamPassRoleStatement.addCondition('StringEquals', {"iam:PassedToService": "kendra.amazonaws.com"});
    
    const kendraPolicy = new iam.PolicyDocument({
      statements: [
        kendraCloudWatchStatement,
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ['*'],
          actions: ['logs:DescribeLogGroups']
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ['arn:aws:logs:' + props?.env?.region + ':' + props?.env?.account + ':log-group:/aws/kendra/*'],
          actions: ['logs:CreateLogGroup']
        }),
        new iam.PolicyStatement({
          effect:iam.Effect.ALLOW,
          resources: ['arn:aws:logs:' + props?.env?.region + ':' + props?.env?.account + ':log-group:/aws/kendra/*:log-stream:*'],
          actions: [
            "logs:DescribeLogStreams",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
        }),
        kendraIamPassRoleStatement,
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ['*'],
          actions: [
            'iam:ListRoles',
            "ec2:DescribeSecurityGroups",
            "ec2:DescribeVpcs",
            "ec2:DescribeSubnets",
            "kms:ListKeys",
            "kms:ListAliases",
            "kms:DescribeKey",
            "s3:ListAllMyBuckets",
            "s3:GetBucketLocation",
            "secretsmanager:ListSecrets",
            "cloudwatch:GetMetricData",
            "kendra:*",
          ]
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ["arn:aws:secretsmanager:*:*:secret:AmazonKendra-*"],
          actions: [
            "secretsmanager:CreateSecret",
            "secretsmanager:DescribeSecret"
          ]
        })
      ]
    });

    //Create Kendra Indices
    const kendraRole = new iam.Role(this, 'kendraRole', {
      assumedBy: new iam.ServicePrincipal('kendra.amazonaws.com'),
      inlinePolicies: {
        ['kendraPolicy']: kendraPolicy
      },
    });

    const courseIndex = new kendra.CfnIndex(this, 'UBCCoursesIndex', {
      edition: 'ENTERPRISE_EDITION',
      name: 'ubcCoursesData',
      roleArn: kendraRole.roleArn,
      documentMetadataConfigurations: [
        {
          name: 'Co-reqs',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'coreq',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'courseNumber',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'credit',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'date_buildings',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'description',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'instructor',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'mode_of_delivery',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'Pre-reqs',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'prereq',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'requires_in_person_attendance',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
        {
          name: 'ubcURI',
          type: 'STRING_VALUE',
          search: {
            displayable: true,
            facetable: true,
            searchable: true,
            sortable: true,
          },
        },
      ]
    });

    //Create UBC Calendar Index
    const calendarIndex = new kendra.CfnIndex(this, 'UBCCalendarIndex', {
      edition: 'ENTERPRISE_EDITION',
      name: 'ubcCalendarData',
      roleArn: kendraRole.roleArn
    });

    //Attach index ids for use later
    new cdk.CfnOutput(this, 'courses_index_id', { value: courseIndex.attrId });
    new cdk.CfnOutput(this, 'calendar_index_id', { value: calendarIndex.attrId });
    this.courseIndexId = courseIndex.attrId;
    this.calendarIndexId = calendarIndex.attrId;

    //Create S3 buckets for kendra data sources
    //Auto delete the bucket when stack is deleted
    const courseBucket = new s3.Bucket(this, 'ubcCourseBucket', {
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
    });

    //Create output for S3 bucket for scraper
    new cdk.CfnOutput(this, 's3_bucket_id', { value: courseBucket.bucketName });
    this.s3BucketId = courseBucket.bucketName

    //Create IAM role for kendra data source
    const dataSourceCoursePolicy = new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ["arn:aws:s3:::" + courseBucket.bucketName + "/*"],
          actions: ['s3:GetObject']
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ["arn:aws:s3:::" + courseBucket.bucketName],
          actions: ['s3:ListBucket']
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          resources: ["arn:aws:kendra:" + props?.env?.region + ":" + props?.env?.account + ":index/" + this.courseIndexId],
          actions: [
            "kendra:BatchPutDocument",
            "kendra:BatchDeleteDocument"
          ]
        }),
      ]
    });

    // Create datasource role for kendra courses (S3 access)
    const kendraCourseDataSourceRole = new iam.Role(this, 'kendraS3DataSourceRole', {
      assumedBy: new iam.ServicePrincipal('kendra.amazonaws.com'),
      inlinePolicies: {
        ['dataSourceCoursePolicy']: dataSourceCoursePolicy
      },
    });

    //Create the s3 data source config for data source
    const s3DataSourceConfigurationProperty: kendra.CfnDataSource.S3DataSourceConfigurationProperty = {
      bucketName: courseBucket.bucketName,
    };
    const dataSourceConfigurationProperty: kendra.CfnDataSource.DataSourceConfigurationProperty = {
      s3Configuration: s3DataSourceConfigurationProperty,
    };

    //Create Kendra course data source
    const kendraCourseDataSource = new kendra.CfnDataSource(this, 'UBCCoursesDataSource', {
      indexId: this.courseIndexId,
      name: 's3CourseBucketDataSource',
      type: 'S3',
      dataSourceConfiguration: dataSourceConfigurationProperty,
      schedule: 'cron(0 8 1 * ? *)',
      roleArn: kendraCourseDataSourceRole.roleArn
    });
    
    //Create Kendra Calendar data source
    const webCrawlerDataSourceConfigurationProperty: kendra.CfnDataSource.WebCrawlerConfigurationProperty = {
      urls: {
        seedUrlConfiguration: {
          seedUrls: ["https://www.calendar.ubc.ca/vancouver/index.cfm?tree=12,0,0,0"],
          webCrawlerMode: 'HOST_ONLY',
        }
      },
      crawlDepth: 4,
      maxContentSizePerPageInMegaBytes: 50,
      maxLinksPerPage: 100,
      maxUrlsPerMinuteCrawlRate: 300,
      urlInclusionPatterns: ['.*.*https://www.calendar.ubc.ca/vancouver/*.*.*'],
    };

    const webCrawlerDataSourceConfiguration: kendra.CfnDataSource.DataSourceConfigurationProperty = {
      webCrawlerConfiguration: webCrawlerDataSourceConfigurationProperty
    };

    const kendraCalendarDataSource = new kendra.CfnDataSource(this, 'UBCCalendarDataSource', {
      indexId: this.calendarIndexId,
      name: 'calendarWebCrawlerDataSource',
      type: 'WEBCRAWLER',
      dataSourceConfiguration: webCrawlerDataSourceConfiguration,
      schedule: 'cron(0 8 1 * ? *)',
      roleArn: kendraRole.roleArn
    });

    //Create lambda custom role
    const lexLambdaRole = new iam.Role(this, 'lexLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      inlinePolicies: {
        ['lambdaPolicy']: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              resources: [
                "arn:aws:kendra:*:" + props?.env?.account + ":index/*"
              ],
              actions:[
                "kendra:Query",
              ]
            })
          ],
        }),
      }, 
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaBasicExecutionRole',
        )
      ],
    });

    //Create lex's lambda handler
    const lexSearchLambda = new lambda.Function(this, "ubc-ECECapstoneBot-KendraSearchIntentHandler", {
      runtime: lambda.Runtime.PYTHON_3_9,
      timeout: cdk.Duration.minutes(1),
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../resources/lexLambda')),
      environment: {
        REGION: cdk.Stack.of(this).region,
        KENDRA_DATA_BUCKET: kendraCourseDataSource.name,
        KENDRA_INDEX: kendraCourseDataSource.indexId
      },
      role: lexLambdaRole
    });

    //Grant lex invocation access for lambda
    const servicePrincipal = new iam.ServicePrincipal('lexv2.amazonaws.com');
    const servicePrincipalWithConditions = servicePrincipal.withConditions({
      ArnLike: {
        'aws:SourceArn': "arn:aws:lex:" + props?.env?.region + ":" + props?.env?.account + ":bot-alias/" + this.lexBotId + "/" + this.lexBotAliasId
      },
      StringEquals: {
        'aws:SourceAccount': props?.env?.account,
      },
    });

    lexSearchLambda.grantInvoke(servicePrincipalWithConditions);
    
    //Create federated pool for lex
    const federatedPool = new cognito.CfnIdentityPool(this, 'LexIdentityPool', {
      allowUnauthenticatedIdentities: true,
      allowClassicFlow: true
    });

    //Create output for cognito pool ID
    new cdk.CfnOutput(this, "lexCognitoPoolId", { value: federatedPool.ref});
    this.lexCognitoPoolId = federatedPool.ref;

    //Create IAM role for federated lex pool
    const cognitoPoolRole = new iam.Role(this, 'lexCognitoPoolUnauthRole', {
      assumedBy: new iam.FederatedPrincipal(
        'cognito-identity.amazonaws.com',
        {
          StringEquals: {
            'cognito-identity.amazonaws.com:aud': federatedPool.ref,
          },
          'ForAnyValue:StringLike': {
            'cognito-identity.amazonaws.com:amr': 'unauthenticated',
          },
        },
        'sts:AssumeRoleWithWebIdentity',
      ),
      inlinePolicies: {
        ['cognitoLexPolicy']: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              resources: ["*"],
              actions: [
                "mobileanalytics:PutEvents",
                "cognito-sync:*",
                "lex:PostContent",
                "lex:PostText",
                "lex:PutSession",
                "lex:GetSession",
                "lex:DeleteSession",
                "lex:RecognizeText",
                "lex:RecognizeUtterance",
                "lex:StartConversation",
                "polly:DescribeVoices",
                "polly:GetLexicon",
                "polly:GetSpeechSynthesisTask",
                "polly:ListLexicons",
                "polly:ListSpeechSynthesisTasks",
                "polly:SynthesizeSpeech"
              ]
            })
          ],
        }),
      }, 
    });

    //Attach the IAM role to the identity pool
    new cognito.CfnIdentityPoolRoleAttachment(this, 'attachLexRole', {
      identityPoolId: federatedPool.ref,
      roles: {
        unauthenticated: cognitoPoolRole.roleArn
      }
    });
  }
}
