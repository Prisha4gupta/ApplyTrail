output "cluster_name" { value = aws_eks_cluster.main.name }
output "region" { value = var.region }
output "vpc_id" { value = aws_vpc.main.id }
output "public_subnets" { value = aws_subnet.public[*].id }
output "deployment_role_arn" { value = aws_iam_role.deploy.arn }
output "kubeconfig_command" { value = "aws eks update-kubeconfig --region ${var.region} --name ${var.name}" }
output "resolved_addon_versions" { value = { for name, addon in data.aws_eks_addon_version.compatible : name => addon.version } }
