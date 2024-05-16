# openstack-nagios-plugins

Nagios/Icinga2 plugins to monitor an OpenStack installation.

For all checks there are some common arguments:

```text
Global Options:
  -h, --help            show this help message and exit
  --os-cloud <name>     Named cloud to connect to
  --os-auth-type <name>, --os-auth-plugin <name>
                        Authentication type to use

Check Options:
  --check-timeout CHECK_TIMEOUT
                        Timeout for total check execution in seconds (default:
                        10)
  --verbose             Increase output verbosity

Authentication Options:
  Options specific to the password plugin.

  --os-auth-url OS_AUTH_URL
                        Authentication URL
  --os-system-scope OS_SYSTEM_SCOPE
                        Scope for system operations
  --os-domain-id OS_DOMAIN_ID
                        Domain ID to scope to
  --os-domain-name OS_DOMAIN_NAME
                        Domain name to scope to
  --os-project-id OS_PROJECT_ID, --os-tenant-id OS_PROJECT_ID
                        Project ID to scope to
  --os-project-name OS_PROJECT_NAME, --os-tenant-name OS_PROJECT_NAME
                        Project name to scope to
  --os-project-domain-id OS_PROJECT_DOMAIN_ID
                        Domain ID containing project
  --os-project-domain-name OS_PROJECT_DOMAIN_NAME
                        Domain name containing project
  --os-trust-id OS_TRUST_ID
                        ID of the trust to use as a trustee use
  --os-default-domain-id OS_DEFAULT_DOMAIN_ID
                        Optional domain ID to use with v3 and v2 parameters.
                        It will be used for both the user and project domain
                        in v3 and ignored in v2 authentication.
  --os-default-domain-name OS_DEFAULT_DOMAIN_NAME
                        Optional domain name to use with v3 API and v2
                        parameters. It will be used for both the user and
                        project domain in v3 and ignored in v2 authentication.
  --os-user-id OS_USER_ID
                        User id
  --os-username OS_USERNAME, --os-user-name OS_USERNAME
                        Username
  --os-user-domain-id OS_USER_DOMAIN_ID
                        User's domain id
  --os-user-domain-name OS_USER_DOMAIN_NAME
                        User's domain name
  --os-password OS_PASSWORD
                        User's password

API Connection Options:
  Options controlling the HTTP API Connections

  --insecure            Explicitly allow client to perform "insecure" TLS
                        (https) requests. The server's certificate will not be
                        verified against any certificate authorities. This
                        option should be used with caution.
  --os-cacert <ca-certificate>
                        Specify a CA bundle file to use in verifying a TLS
                        (https) server certificate. Defaults to
                        env[OS_CACERT].
  --os-cert <certificate>
                        The location for the keystore (PEM formatted)
                        containing the public key of this client. Defaults to
                        env[OS_CERT].
  --os-key <key>        The location for the keystore (PEM formatted)
                        containing the private key of this client. Defaults to
                        env[OS_KEY].
  --timeout <seconds>   Set request timeout (in seconds).
  --collect-timing      Collect per-API call timing information.

Service Options:
  Options controlling the specialization of the API Connection from
  information found in the catalog

  --os-service-type <name>
                        Service type to request from the catalog
  --os-service-name <name>
                        Service name to request from the catalog
  --os-interface <name>
                        API Interface to use [public, internal, admin]
  --os-region-name <name>
                        Region of the cloud to use
  --os-endpoint-override <name>
                        Endpoint to use instead of the endpoint in the catalog
  --os-api-version <name>
                        Which version of the service API to use
```

Individual checks will expose more _Check Options_ relevant to what they do.

Currently, the following checks are implemented:

## Cinder

### check_cinder_services

```text
Determines the status of the cinder agents/services.

Check Options:
  -w RANGE, --warn RANGE
                        return warning if number of up agents is outside RANGE
                        (default: 0:, never warn)
  -c RANGE, --critical RANGE
                        return critical if number of up agents is outside
                        RANGE (default 1:, never critical)
  --warn-disabled RANGE
                        return warning if number of disabled agents is outside
                        RANGE (default: @1:, warn if any disabled agents)
  --critical-disabled RANGE
                        return critical if number of disabled agents is
                        outside RANGE (default: 0:, never critical)
  --warn-down RANGE     return warning if number of down agents is outside
                        RANGE (default: 0:, never warn)
  --critical-down RANGE
                        return critical if number of down agents is outside
                        RANGE (default: 0, always critical if any)
  --binary BINARY       filter agent binary
  --host HOST           filter hostname
```

Admin rights are necessary to run this check.

## Glance

### check_glance_images

```text
Lists glance images and gets timing

Check Options:
  -w RANGE, --warn RANGE
                        return warning if repsonse time is outside RANGE
                        (default: 0:, never warn)
  -c RANGE, --critical RANGE
                        return critical if repsonse time is outside RANGE
                        (default 1:, never critical)
```

## Keystone

### check_keystone_status

```text
Nagios/Icinga plugin to check keystone.

Check Options:
  --tversion TOKENVERSION
                        the version of the keystoneclient to use to verify the
                        token. currently supported is 3 and 2 (default 3)
  -w RANGE, --warn RANGE
                        return warning if number of up agents is outside RANGE
                        (default: 0:, never warn)
  -c RANGE, --critical RANGE
                        return critical if number of up agents is outside
                        RANGE (default 1:, never critical)
```

## Neutron

### check_neutron_agents

```text
Determines the status of the neutron agents.

Check Options:
  -w RANGE, --warn RANGE
                        return warning if number of up agents is outside RANGE
                        (default: 0:, never warn)
  -c RANGE, --critical RANGE
                        return critical if number of up agents is outside
                        RANGE (default 1:, never critical)
  --warn-disabled RANGE
                        return warning if number of disabled agents is outside
                        RANGE (default: @1:, warn if any disabled agents)
  --critical-disabled RANGE
                        return critical if number of disabled agents is
                        outside RANGE (default: 0:, never critical)
  --warn-down RANGE     return warning if number of down agents is outside
                        RANGE (default: 0:, never warn)
  --critical-down RANGE
                        return critical if number of down agents is outside
                        RANGE (default: 0, always critical if any)
  --binary BINARY       filter agent binary
  --host HOST           filter hostname
```

Admin rights are necessary to run this check.

### check_neutron_floatingips

```text
Determines the number of assigned (used and unused) floating ip's

Check Options:
  -w RANGE, --warn RANGE
                        return warning if number of assigned floating ip's is
                        outside range (default: 0:200, warn if more than 200
                        are used)
  -c RANGE, --critical RANGE
                        return critical if number of assigned floating ip's is
                        outside RANGE (default 0:230, critical if more than
                        230 are used)
```

Admin rights are necessary to run this check.

### check_neutron_network_ip_availability

```text
Determines the number of total and used neutron network ip's

Check Options:
  -w RANGE, --warn RANGE
                        return warning if number of used ip's is outside range
                        (default: 0:200, warn if more than 200 are used)
  -c RANGE, --critical RANGE
                        return critical if number of used ip's is outside
                        RANGE (default 0:230, critical if more than 230 are
                        used)
  -n NETWORK, --network NETWORK
                        The network to check
```

Admin rights are necessary to run this check.

## Nova

### check_nova_hypervisors

```text
Check Options:
  -H HOST, --host HOST  hostname where the hypervisor is running if not
                        defined (default), summary of all hosts is used
  -w RANGE, --warn RANGE
                        return warning if number of running vms is outside
                        RANGE (default: 0:, never warn)
  -c RANGE, --critical RANGE
                        return critical if number of running vms is outside
                        RANGE (default 0:, never critical)
  --warn-memory RANGE   return warning if used memory is outside RANGE
                        (default: 0:, never warn
  --critical-memory RANGE
                        return critical if used memory is outside RANGE
                        (default: 0:, never critical
  --warn-memory-percent RANGE
                        return warning if used memory is outside percent RANGE
                        (default: 0:90, warn if 90% of memory is used
  --critical-memory-percent RANGE
                        return critical if used memory is outside percent
                        RANGE (default: 0:90, critical if 95% of memory is
                        used
  --warn-vcpus RANGE    return warning if used vcpus is outside RANGE
                        (default: 0:, never warn)
  --critical-vcpus RANGE
                        return critical if used vcpus is outside RANGE
                        (default: 0, always critical if any
  --warn-vcpus-percent RANGE
                        return warning if used vcpus is outside percent RANGE
                        (default: 0:90, warn if 90% of vcpus are used)
  --critical-vcpus-percent RANGE
                        return critical if used vcpus is outside percent RANGE
                        (default: 0:95, critical if 95% of vcpus are used
```

Admin rights are necessary to run this check.

### check_nova_services

```text
Determines the status of the nova services.

Check Options:
  --warn RANGE          return warning if number of up agents is outside RANGE
                        (default: 0:, never warn)
  --critical RANGE      return critical if number of up agents is outside
                        RANGE (default 1:, never critical)
  --warn-disabled RANGE
                        return warning if number of disabled agents is outside
                        RANGE (default: @1:, warn if any disabled agents)
  --critical-disabled RANGE
                        return critical if number of disabled agents is
                        outside RANGE (default: 0:, never critical)
  --warn-down RANGE     return warning if number of down agents is outside
                        RANGE (default: 0:, never warn)
  --critical-down RANGE
                        return critical if number of down agents is outside
                        RANGE (default: 0, always critical if any)
  --binary BINARY       filter agent binary
  --host HOST           filter hostname
```

Admin rights are necessary to run this check.
