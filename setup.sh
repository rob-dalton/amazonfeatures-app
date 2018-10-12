#!bin/bash
# amazonfeatures setup intended for AWS EC2 Ubutu 14.04 instance

# install non-python dependencies
sudo apt-get update
cat requirements.txt | xargs sudo apt-get install -y

# get project and data
git clone https://github.com/rob-dalton/amazonfeatures-app.git
aws s3 cp s3://amazon-review-data/test_products.json ./ --region us-west-1

mongoimport --db app --collection products --file test_products.json
