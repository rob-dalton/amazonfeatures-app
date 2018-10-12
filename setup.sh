#!bin/bash
# amazonfeatures setup intended for AWS EC2 Ubutu 14.04 instance

# install dependencies
sudo apt-get update
cat requirements.txt | xargs sudo apt-get install -y
pip install -r pip_requirements.txt

# get project and data
git clone https://github.com/rob-dalton/amazonfeatures-app.git
aws s3 cp s3://amazon-review-data/test_products.json ./ --region us-west-1

mongoimport --db app --collection products --file test_products.json
