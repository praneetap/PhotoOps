init:
	pipenv --python 3.8
	pipenv install --dev

# Command to run everytime you make changes to verify everything works
dev: flake lint test

# Verifications to run before sending a pull request
pr: init dev

SAM_TEMPLATE ?= template.yaml
ENV ?= ${USER}
APPNAME = $(shell basename ${CURDIR})
STACKNAME = $(APPNAME)-$(ENV)
AWS_REGION ?= $(shell aws configure get region)
PIPELINE_STACKNAME = $(shell basename ${CURDIR})-pipeline-$(ENV)
BRANCH ?= 'master'

check_profile:
	# Make sure we have a user-scoped credentials profile set. We don't want to be accidentally using the default profile
	@aws configure --profile ${AWS_PROFILE} list 1>/dev/null 2>/dev/null || (echo '\nMissing AWS Credentials Profile called '${AWS_PROFILE}'. Run `aws configure --profile ${AWS_PROFILE}` to create a profile called '${AWS_PROFILE}' with creds to your personal AWS Account'; exit 1)

build:
	$(info Building application)
	sam build --use-container --parallel --template ${SAM_TEMPLATE}

validate:
	$(info linting SAM template)
	$(info linting CloudFormation)
	@cfn-lint template.yaml
	$(info validating SAM template)
	@sam validate

deploy: validate build
	$(info Deploying to personal development stack)
	sam deploy --stack-name $(STACKNAME) --region ${AWS_REGION} --resolve-s3 --parameter-overrides ServiceEnv=$(ENV)

# Requires usage of PipelineUser IAM user.
deploy-pipeline:
	$(info Deploying to personal development stack)
	sam deploy \
		--region ${AWS_REGION} \
		--resolve-s3 \
		--template codepipeline.yaml \
		--stack-name $(PIPELINE_STACKNAME) \
		--parameter-overrides ServiceEnv=$(ENV) FeatureGitBranch=$(BRANCH) CodeStarConnectionArn="arn:aws:codestar-connections:us-east-1:346402060170:connection/0628e0e2-2afe-48bf-8705-f66170a6a41e"

describe:
	$(info Describing stack)
	@aws cloudformation describe-stacks --stack-name $(STACKNAME) --output table --query 'Stacks[0]'

outputs:
	$(info Displaying stack outputs)
	@aws cloudformation describe-stacks --stack-name $(STACKNAME) --output table --query 'Stacks[0].Outputs'

parameters:
	$(info Displaying stack parameters)
	@aws cloudformation describe-stacks --stack-name $(STACKNAME) --output table --query 'Stacks[0].Parameters'

delete:
	$(info Delete stack)
	@sam delete --stack-name $(STACKNAME)

function:
	$(info creating function: ${F})
	mkdir -p src/handlers/${F}
	touch src/handlers/${F}/__init__.py
	touch src/handlers/${F}/function.py
	mkdir -p tests/{unit,integration}/src/handlers/${F}
	touch tests/unit/src/handlers/${F}/__init__.py
	touch tests/unit/src/handlers/${F}/test_handler.py
	touch tests/integration/src/handlers/${F}/__init__.py
	touch tests/integration/src/handlers/${F}/test_handler.py
	echo "-e src/common/" > src/handlers/${F}/requirements.txt
	touch data/events/${F}-{event,msg}.json

unit-test:
	$(info running unit tests)
	# Integration tests don't need code coverage
	pipenv run pytest tests/unit

integ-test:
	$(info running integration tests)
	# Integration tests don't need code coverage
	pipenv run pytest tests/integration

test:
	$(info running tests)
	# Run unit tests
	# Fail if coverage falls below 95%
	pipenv run test

flake8:
	$(info running flake8 on code)
	# Make sure code conforms to PEP8 standards
	pipenv run flake8 src
	pipenv run flake8 tests/unit tests/integration

pylint:
	$(info running pylint on code)
	# Linter performs static analysis to catch latent bugs
	pipenv run lint --rcfile .pylintrc src

lint: pylint flake8

clean:
	$(info cleaning project)
	# remove sam cache
	rm -rf .aws-sam
