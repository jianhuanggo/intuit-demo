# intuit-demo

data-driven - Instead of manually writing code for invoking AWS SDK for every single instance which may end up with different code for a different component which will increase the upkeep cost as the environments scale up, I think it's better for me to standardize the construct using a data-driven approach, more often than not, dealing with configuration files instead code not only allow a faster pace to accommodate a particular change, but it also has a better chance in withstanding the test of time.  Code generation is an extension of this.  I have implemented a mechanism to resolve references.

Operational management -  I have implemented a mechanism that allows me to gracefully start from the last known point. The mechanism also archives metadata regarding past runs.  These data can be analyzed to ameliorate future runs.

Security - to improve security, I have added a custom domain name, making sure IAM policies are compliant with AWS's least privileged principle.  In a production setting, WAF and CloudFront can be complemented to increase security measures

Tagging - In a frequently changing environment, I think tagging is important for us  This would allow automated service discovery 
