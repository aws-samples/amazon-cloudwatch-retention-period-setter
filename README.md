## Automatically Configure Amazon CloudWatch Log Groups Retention Period

One pillar of our six Well-Architected Framework Pillars is Cost Optimization. The cost optimization pillar focuses on avoiding unnecessary costs. By default, all the logs stored in *Amazon CloudWatch* log groups are kept indefinitely and their retention period is set to Never Expire which might result in excessive costs.
 
To reduce storage costs, customers should consider changing the default retention period. Changing Amazon CloudWatch log groups retention period manually could be tedious considering that you need to track all the newly created log groups. This solution shall take care of this task in your behalf.

**Deployment Instructions**: 

Covered in this blog post:

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

