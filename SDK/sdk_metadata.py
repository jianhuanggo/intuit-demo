import boto3


def justreturn(**kwargs):
    return "always_return_success"


_SDK_FUNC_DICT = {"add_permission": boto3.client('lambda').add_permission,
                  "create_function": boto3.client('lambda').create_function,
                  "delete_function": boto3.client('lambda').delete_function,
                  "remove_permission": boto3.client('lambda').remove_permission,
                  "create_rest_api": boto3.client('apigateway').create_rest_api,
                  "get_resources": boto3.client('apigateway').get_resources,
                  "create_resource": boto3.client('apigateway').create_resource,
                  "put_method": boto3.client('apigateway').put_method,
                  "put_integration": boto3.client('apigateway').put_integration,
                  "create_deployment": boto3.client('apigateway').create_deployment,
                  "delete_rest_api": boto3.client('apigateway').delete_rest_api,
                  "update_stage": boto3.client('apigateway').update_stage,
                  "update_account": boto3.client('apigateway').update_account,
                  "create_api_mapping": boto3.client('apigatewayv2').create_api_mapping,
                  "delete_api_mapping": boto3.client('apigatewayv2').delete_api_mapping,
                  "get_api_mappings": boto3.client('apigatewayv2').get_api_mappings,
                  "create_policy": boto3.client('iam').create_policy,
                  "delete_policy": boto3.client('iam').delete_policy,
                  "create_role": boto3.client('iam').create_role,
                  "delete_role": boto3.client('iam').delete_role,
                  "attach_role_policy": boto3.client('iam').attach_role_policy,
                  "detach_role_policy": boto3.client('iam').detach_role_policy,
                  "create_table": boto3.client('dynamodb').create_table,
                  "delete_table": boto3.client('dynamodb').delete_table,
                  "notdummy": justreturn
                  }


