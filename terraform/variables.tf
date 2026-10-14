variable "region" {
  type    = string
  default = "ap-south-1"
}
variable "name" {
  type    = string
  default = "applytrail"
}
variable "kubernetes_version" {
  type    = string
  default = "1.35"
}
variable "admin_principal_arn" {
  type        = string
  description = "IAM role ARN used by the human operator (not an STS assumed-role ARN)."
}
variable "github_repository" {
  type    = string
  default = "Prisha4gupta/ApplyTrail"
}
variable "github_oidc_provider_arn" {
  type        = string
  default     = null
  description = "Existing account GitHub OIDC provider ARN; null creates one."
}
variable "api_allowed_cidrs" {
  type        = list(string)
  description = "Operator and fixed-egress CI public CIDRs. 0.0.0.0/0 supports hosted runners but broadens network exposure; IAM still required."
}
variable "node_instance_type" {
  type    = string
  default = "t3.medium"
}
variable "addon_versions" {
  type        = map(string)
  default     = {}
  description = "Override with exact compatible builds from aws eks describe-addon-versions; otherwise resolve compatible versions during plan."
}
