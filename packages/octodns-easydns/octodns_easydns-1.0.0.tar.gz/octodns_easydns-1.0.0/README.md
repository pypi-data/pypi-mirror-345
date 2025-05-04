## easyDns API v3 provider for octoDNS

An [octoDNS](https://github.com/octodns/octodns/) provider that targets [easyDNS](https://easydns.com/).

### Installation

#### Command line

```
pip install octodns-easydns
```

#### requirements.txt/setup.py

Pinning specific versions or SHAs is recommended to avoid unplanned upgrades.

##### Versions

```
# Start with the latest versions and don't just copy what's here
octodns==0.9.14
octodns-easydns==0.0.1
```

##### SHAs

```
# Start with the latest/specific versions and don't just copy what's here
-e git+https://git@github.com/octodns/octodns.git@9da19749e28f68407a1c246dfdf65663cdc1c422#egg=octodns
-e git+https://git@github.com/octodns/octodns-easydns.git@ec9661f8b335241ae4746eea467a8509205e6a30#egg=octodns_easydns
```

### Configuration

```yaml
providers:
  easydns:
    class: octodns_easydns.EasyDnsProvider
    # Your EasyDNS API token (required)
    token: env/EASYDNS_TOKEN
    # Your EasyDNS API Key (required)
    api_key: env/EASYDNS_API_KEY
    # Use SandBox or Live environment, optional, defaults to live
    #sandbox: False
    # Currency to use for creating domains, default CAD
    #default_currency: CAD
    # Domain Portfolio under which to create domains
    portfolio: env/EASYDNS_PORTFOLIO
```

### Support Information

#### Records

EasyDnsProvider supports A, AAAA, CAA, CNAME, DS, MX, NAPTR, NS, SRV, and TXT.

#### Root NS Records

EasyDnsProvider supports full root NS record management.

#### Dynamic

EasyDnsProvider does not support dynamic records.

### Development

See the [/script/](/script/) directory for some tools to help with the development process. They generally follow the [Script to rule them all](https://github.com/github/scripts-to-rule-them-all) pattern. Most useful is `./script/bootstrap` which will create a venv and install both the runtime and development related requirements. It will also hook up a pre-commit hook that covers most of what's run by CI.
