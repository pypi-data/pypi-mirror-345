r'''
# Tailscale Lambda Proxy

[![npm version](https://badge.fury.io/js/tailscale-lambda-proxy.svg)](https://badge.fury.io/js/tailscale-lambda-proxy)
[![PyPI version](https://badge.fury.io/py/tailscale-lambda-proxy.svg)](https://badge.fury.io/py/tailscale-lambda-proxy)

* [Tailscale Lambda Proxy](#tailscale-lambda-proxy)

  * [Why use a proxy?](#why-use-a-proxy)
  * [Usage](#usage)

    * [Installation](#installation)
  * [Accessing your Tailscale Network through the Proxy](#accessing-your-tailscale-network-through-the-proxy)

    * [Signing Requests](#signing-requests)
    * [Including Target Headers](#including-target-headers)
    * [Creating CloudWatch Tracking Metrics](#creating-cloudwatch-tracking-metrics)
    * [Error Handling](#error-handling)
    * [Code Examples](#code-examples)
  * [Additional Information](#additional-information)
  * [AWS SigV4 Headers](#aws-sigv4-headers)

A CDK construct that creates an AWS Lambda Function acting as a transparent proxy to your Tailscale network.

Available as both a TypeScript NPM Package and a Python PyPi Package:

* [TypeScript NPM Package](https://www.npmjs.com/package/tailscale-lambda-proxy)
* [Python PyPi Package](https://pypi.org/project/tailscale-lambda-proxy/)

## Why use a proxy?

The Proxy Lambda leverages the [Tailscale Lambda Extension](https://github.com/rehanvdm/tailscale-lambda-extension) CDK
construct.

It is recommended to use the Proxy Lambda to simplify connecting to your Tailscale network and reduces cold starts
by reusing the same Lambda function for all your Tailscale connected traffic.

Use the extension directly if:

* You have **a single Lambda** or service that needs to connect to your Tailscale network.
* You are comfortable with this Lambda having mixed responsibilities, such as connecting to Tailscale and running
  business logic.

Use the Proxy Lambda (recommended) if:

* You have **multiple Lambdas** or services requiring connection to your Tailscale network. The Proxy Lambda *eventually*
  creates a "pool of warm connections" to the Tailscale network, ready for use by other Lambdas.
* You want to separate responsibilities by having a dedicated Lambda for Tailscale connectivity.
* Authentication to the Tailscale network is handled at the IAM level, where access is granted to the Proxy Lambda's
  Function URL (FURL), instead of directly to the Tailscale API Secret Manager.

## Usage

> [!TIP]
> Refer to the [tailscale-lambda-proxy-example](https://github.com/rehanvdm/tailscale-lambda-proxy-example) repository
> for a complete example.

### Installation

Install the package:

```bash
npm install tailscale-lambda-proxy
```

The Proxy Lambda requires the following:

* `tsSecretApiKey`: The AWS Secrets Manager secret containing the Tailscale API Key as plain text.
* `tsHostname`: The "Machine" name as shown in the Tailscale admin console, which identifies the Lambda function(s).

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { TailscaleLambdaProxy } from "tailscale-lambda-proxy";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";

export class MyStack extends cdk.Stack {

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const tailscaleProxy = new TailscaleLambdaProxy(this, "tailscale-proxy", {
      tsSecretApiKey: secretsmanager.Secret.fromSecretNameV2(this, "tailscale-api-key", "tailscale-api-key"),
      tsHostname: "lambda-test",
      // // Optional configuration
      // options: {
      //   extension: {
      //     layerVersionName: "tailscale-extension",
      //     nodeTlsRejectUnauthorized: false, // Sets the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0'
      //   },
      //   lambda: {
      //     functionName: "tailscale-proxy",
      //   }
      // }
    });

    const caller = new NodejsFunction(this, "tailscale-caller", {
      functionName: "tailscale-caller",
      runtime: lambda.Runtime.NODEJS_20_X,
      timeout: cdk.Duration.seconds(30),
      entry: "lib/lambda/tailscale-caller/index.ts",
      environment: {
        TS_PROXY_URL: tailscaleProxy.lambdaFunctionUrl.url,
      }
    });
    tailscaleProxy.lambdaFunctionUrl.grantInvokeUrl(caller); // Important! Allow the caller to invoke the proxy

  }

}
```

## Accessing your Tailscale Network through the Proxy

The [tailscale-lambda-proxy-example](https://github.com/rehanvdm/tailscale-lambda-proxy-example) repository contains
the following example.

The Tailscale Lambda Proxy is fully transparent. It forwards requests (path, method, headers, and body) to the machine
and returns the response without modification.

Key considerations when using the Proxy:

1. All requests must be signed with the IAM Signature V4 algorithm.
2. The target machine's IP address and port must be included in the headers when making requests to the Proxy.

### Signing Requests

The Proxy Lambda exposes a Function URL secured with IAM Authentication. The caller Lambda requires this URL and
IAM permissions to make requests. These requests must be signed with the IAM Signature V4 algorithm. For TypeScript,
use the [aws4](https://www.npmjs.com/package/aws4) package to sign requests.

### Including Target Headers

When calling the Proxy, include the following headers to specify the target machine:

* `ts-target-ip`: The IP address of the Tailscale-connected machine/device.
* `ts-target-port`: The port of the Tailscale-connected machine/device.
* `ts-https`: OPTIONAL, if undefined, the default behaviour is to use https when the port is 443. If specified then it
  will override the default behaviour.
* See the remaining AWS SigV4 headers in the next section (special case for `Authorization`).

These `ts-` headers are removed before the request is forwarded to the target machine.

#### AWS SigV4 Headers

The proxy automatically removes AWS SigV4 headers from the incoming request and replaces them with their `ts-`
prefixed counterparts when forwarding the request if they exist. This allows you to forward headers that
are named the same as required by the AWS SigV4 signature request.

The following headers are handled:

* `ts-authorization` → `Authorization`
* `ts-x-amz-date` → `x-amz-date`
* `ts-host` → `host`
* `ts-x-amz-content-sha256` → `x-amz-content-sha256`

This is useful when you need to include an `Authorization` header in the request to the target machine. If
you place the value directly in the `Authorization` header, it will be overwritten by the AWS SigV4 signature
that the caller generates. Instead, place your authorization value in the `ts-authorization` header. The
proxy will remove all `ts-` prefixed headers before forwarding the request and will correctly set the
`ts-authorization` value as the `Authorization` header in the forwarded request.

### Creating CloudWatch Tracking Metrics

To enable optional tracking metrics, add the following headers to your request:

* `ts-metric-service`: The name of the service or API making the request.
* `ts-metric-dimension-name`: The dimension name for tracking (such as client name).
* `ts-metric-dimension-value`: The value associated with the dimension.

Metrics generated in CloudWatch:

* `success`: Logged when a request reaches the target server, regardless of the API response status.
* `failure`: Logged when a request fails to reach the target server, typically due to network issues or server
  unavailability.

Example headers for a request:

* `ts-metric-service`: `gallagher`, indicating the service or API making the request.
* `ts-metric-dimension-name`: `client`, used for monitoring or alerts.
* `ts-metric-dimension-value`: `rehan-test-client`, identifying the specific client.

This configuration generates CloudWatch metrics similar to the screenshot below:

![tailscale-cloudwatch-metric.png](_imgs/tailscale-cloudwatch-metric.png)

### Error Handling

To maintain transparency, the Proxy Lambda passes all traffic, including errors, back to the caller. This approach
makes it difficult to determine whether an error originated from the Proxy Lambda or the Tailscale-connected machine.

A Proxy Lambda error can be identified by the following headers in the response:

* `ts-error-name`: The error name.
* `ts-error-message`: The error message.

### Code Examples

Refer to the [tailscale-lambda-proxy-example](https://github.com/rehanvdm/tailscale-lambda-proxy-example) repository
for the complete example. The partial snippet below shows a Lambda function accessing an express server running
on a Tailscale-connected machine. The [TailscaleProxyApi](https://github.com/rehanvdm/tailscale-lambda-proxy-example/blob/f5e95c9b2294bd185bbe5b372a24dafcafc17297/lib/lambda/tailscale-caller/tailscale-proxy-api.ts)
class implements the above-mentioned usage specifications.

```python
import {TailscaleProxyApi} from "./tailscale-proxy-api";

export const handler = async (event: any) => {
  console.log(JSON.stringify(event, null, 2));

  // Connect to the tailscale network with your laptop, get your tailscale IP, then start the express server in
  // `express-local-api` with `npm run start` and then run the lambda function to test the connection.
  const targetIp = "100.91.164.93";
  const targetPort = 3000;

  const api = new TailscaleProxyApi(process.env.TS_PROXY_URL!, process.env.AWS_REGION!,
    targetIp, targetPort,
    "express-local-api", "client", "client-a"
    );

  const resp = await api.request("/ping", "GET");

  if(resp.proxyError) {
    throw new Error(`PROXY ERROR: ${resp.proxyError}`);
  }
  else if(resp.response.statusCode !== 200) {
    throw new Error(`API ERROR: ${resp.response.statusCode} with body: ${resp.response.body}`);
  }

  console.log('');
  console.log('API SUCCESS: ', resp.response.body);

  return true;
};
```

## Additional Information

Refer to the [Tailscale Lambda Extension](https://github.com/rehanvdm/tailscale-lambda-extension) documentation for:

* Configuring Tailscale.
* Understanding limitations such as cold start times, package sizes, and the lack of DNS resolution.
* Additional implementation details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_lambda_nodejs as _aws_cdk_aws_lambda_nodejs_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8
import tailscale_lambda_extension as _tailscale_lambda_extension_3efe799a


class TailscaleLambdaProxy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="tailscale-lambda-proxy.TailscaleLambdaProxy",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ts_hostname: builtins.str,
        ts_secret_api_key: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        options: typing.Optional[typing.Union["TailscaleLambdaProxyPropsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ts_hostname: The "Machine" name as shown in the Tailscale admin console that identifies the Lambda function.
        :param ts_secret_api_key: The name of the AWS Secrets Manager secret that contains the pure text Tailscale API Key.
        :param options: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__526fa7750b0e7b9422bb864d1636199d3eb6a8950c9fbe1a2634e109edb4970c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TailscaleLambdaProxyProps(
            ts_hostname=ts_hostname,
            ts_secret_api_key=ts_secret_api_key,
            options=options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="extension")
    def extension(
        self,
    ) -> _tailscale_lambda_extension_3efe799a.TailscaleLambdaExtension:
        return typing.cast(_tailscale_lambda_extension_3efe799a.TailscaleLambdaExtension, jsii.get(self, "extension"))

    @builtins.property
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> _aws_cdk_aws_lambda_nodejs_ceddda9d.NodejsFunction:
        return typing.cast(_aws_cdk_aws_lambda_nodejs_ceddda9d.NodejsFunction, jsii.get(self, "lambda"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunctionUrl")
    def lambda_function_url(self) -> _aws_cdk_aws_lambda_ceddda9d.FunctionUrl:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.FunctionUrl, jsii.get(self, "lambdaFunctionUrl"))


@jsii.data_type(
    jsii_type="tailscale-lambda-proxy.TailscaleLambdaProxyProps",
    jsii_struct_bases=[],
    name_mapping={
        "ts_hostname": "tsHostname",
        "ts_secret_api_key": "tsSecretApiKey",
        "options": "options",
    },
)
class TailscaleLambdaProxyProps:
    def __init__(
        self,
        *,
        ts_hostname: builtins.str,
        ts_secret_api_key: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        options: typing.Optional[typing.Union["TailscaleLambdaProxyPropsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ts_hostname: The "Machine" name as shown in the Tailscale admin console that identifies the Lambda function.
        :param ts_secret_api_key: The name of the AWS Secrets Manager secret that contains the pure text Tailscale API Key.
        :param options: 
        '''
        if isinstance(options, dict):
            options = TailscaleLambdaProxyPropsOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1db2d7dac4f0d91262bca503b92335b2c7da889dea02a4605b962b6c445b4e3)
            check_type(argname="argument ts_hostname", value=ts_hostname, expected_type=type_hints["ts_hostname"])
            check_type(argname="argument ts_secret_api_key", value=ts_secret_api_key, expected_type=type_hints["ts_secret_api_key"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ts_hostname": ts_hostname,
            "ts_secret_api_key": ts_secret_api_key,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def ts_hostname(self) -> builtins.str:
        '''The "Machine" name as shown in the Tailscale admin console that identifies the Lambda function.'''
        result = self._values.get("ts_hostname")
        assert result is not None, "Required property 'ts_hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ts_secret_api_key(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The name of the AWS Secrets Manager secret that contains the pure text Tailscale API Key.'''
        result = self._values.get("ts_secret_api_key")
        assert result is not None, "Required property 'ts_secret_api_key' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def options(self) -> typing.Optional["TailscaleLambdaProxyPropsOptions"]:
        result = self._values.get("options")
        return typing.cast(typing.Optional["TailscaleLambdaProxyPropsOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TailscaleLambdaProxyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="tailscale-lambda-proxy.TailscaleLambdaProxyPropsLambdaOption",
    jsii_struct_bases=[],
    name_mapping={
        "function_name": "functionName",
        "node_tls_reject_unauthorized": "nodeTlsRejectUnauthorized",
    },
)
class TailscaleLambdaProxyPropsLambdaOption:
    def __init__(
        self,
        *,
        function_name: typing.Optional[builtins.str] = None,
        node_tls_reject_unauthorized: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param function_name: 
        :param node_tls_reject_unauthorized: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc605245a7905e261f1f575b026f71eb19dfac71fcdbbb59b18468ecce4a759)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument node_tls_reject_unauthorized", value=node_tls_reject_unauthorized, expected_type=type_hints["node_tls_reject_unauthorized"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if function_name is not None:
            self._values["function_name"] = function_name
        if node_tls_reject_unauthorized is not None:
            self._values["node_tls_reject_unauthorized"] = node_tls_reject_unauthorized

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_tls_reject_unauthorized(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("node_tls_reject_unauthorized")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TailscaleLambdaProxyPropsLambdaOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="tailscale-lambda-proxy.TailscaleLambdaProxyPropsOptions",
    jsii_struct_bases=[],
    name_mapping={"extension": "extension", "lambda_": "lambda"},
)
class TailscaleLambdaProxyPropsOptions:
    def __init__(
        self,
        *,
        extension: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LayerVersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_: typing.Optional[typing.Union[TailscaleLambdaProxyPropsLambdaOption, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param extension: 
        :param lambda_: 
        '''
        if isinstance(extension, dict):
            extension = _aws_cdk_aws_lambda_ceddda9d.LayerVersionOptions(**extension)
        if isinstance(lambda_, dict):
            lambda_ = TailscaleLambdaProxyPropsLambdaOption(**lambda_)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f012a3e49f709451167b5aea4e5d5e6bec3630984d9d528d842997a018da94e7)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
            check_type(argname="argument lambda_", value=lambda_, expected_type=type_hints["lambda_"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if extension is not None:
            self._values["extension"] = extension
        if lambda_ is not None:
            self._values["lambda_"] = lambda_

    @builtins.property
    def extension(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LayerVersionOptions]:
        result = self._values.get("extension")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.LayerVersionOptions], result)

    @builtins.property
    def lambda_(self) -> typing.Optional[TailscaleLambdaProxyPropsLambdaOption]:
        result = self._values.get("lambda_")
        return typing.cast(typing.Optional[TailscaleLambdaProxyPropsLambdaOption], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TailscaleLambdaProxyPropsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TailscaleLambdaProxy",
    "TailscaleLambdaProxyProps",
    "TailscaleLambdaProxyPropsLambdaOption",
    "TailscaleLambdaProxyPropsOptions",
]

publication.publish()

def _typecheckingstub__526fa7750b0e7b9422bb864d1636199d3eb6a8950c9fbe1a2634e109edb4970c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ts_hostname: builtins.str,
    ts_secret_api_key: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    options: typing.Optional[typing.Union[TailscaleLambdaProxyPropsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1db2d7dac4f0d91262bca503b92335b2c7da889dea02a4605b962b6c445b4e3(
    *,
    ts_hostname: builtins.str,
    ts_secret_api_key: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    options: typing.Optional[typing.Union[TailscaleLambdaProxyPropsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc605245a7905e261f1f575b026f71eb19dfac71fcdbbb59b18468ecce4a759(
    *,
    function_name: typing.Optional[builtins.str] = None,
    node_tls_reject_unauthorized: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f012a3e49f709451167b5aea4e5d5e6bec3630984d9d528d842997a018da94e7(
    *,
    extension: typing.Optional[typing.Union[_aws_cdk_aws_lambda_ceddda9d.LayerVersionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_: typing.Optional[typing.Union[TailscaleLambdaProxyPropsLambdaOption, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
