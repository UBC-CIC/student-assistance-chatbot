# Requirements

Before you deploy, you must have the following in place:
*  [AWS Account](https://aws.amazon.com/account/) 
*  [GitHub Account](https://github.com/) 
*  [AWS CLI](https://aws.amazon.com/cli/) 
*  [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install)  


# Step 1: Clone The Repository

First, clone the github repository onto your machine. To do this:
1. Create a folder on your desktop to contain the code.
2. Open terminal (or command prompt if on windows) and **cd** into the above folder.
3. Clone the github repository by entering the following:
```bash
git clone https://github.com/UBC-CIC/student-assistance-chatbot.git
```

The code should now be in the above folder. Now navigate into the repository folder by running the following command:
```bash
cd student-assitance-chatbot
```

# Step 2: Backend Deployment
We will have to deploy the backend of our solution first to obtain the chatbot's ID and alias ID before running the frontend.

First we need to enter the cdk folder of the code to deploy the cloudformation stack

```bash
cd cdk
```

Following this, we can deploy the cloudformation stack to our AWS account
```bash
cdk deploy
```

If you have multiple aws profiles, you may need to run 
```bash
cdk deploy --profile <desired aws profile>
```
Note that you may need to enter yes to the console a few times before the solution is deployed to AWS.
The deployment can take anywhere from 30 minutes to an hour as most of the time is spent creating the AWS Kendra indices.

Once deployed, the command will complete and you should be able to find the cloudformation stack on your AWS Account.


# Step 3: Scraper Deployment
1. Install the dependencies using the command:
```bash
pip install -r requirements.txt
```
2. Run the scraper with the following command:
```bash
python scraper.py
```

Note: The scraper code scrapes the courses from the [UBC courses website](https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea). We are able to extract the following information:
* Buildings
* Co-requisites
* Course Number
* Credits
* Date
* Description
* Instructor
* Mode of delivery
* Pre-requisites
* Requires in-person attendance

# Step 4: Frontend Deployment

[![amplifybutton](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/BX2000/student-assistant-bot)